"""
Script to test the web crawler functionality.
Run this to verify the crawler discovers all pages correctly.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.scraping.scraper import WebScraper


def test_crawler(url: str):
    """
    Test the crawler on a given URL.
    
    Args:
        url: Starting URL to crawl
    """
    print("=" * 80)
    print(f"Testing Web Crawler")
    print("=" * 80)
    print(f"\nStarting URL: {url}\n")
    
    # Create scraper with custom settings
    scraper = WebScraper(
        chunk_size=1000,
        chunk_overlap=200,
        max_pages=20,  # Limit for testing
        timeout=10
    )
    
    # Test 1: Just discover URLs without scraping
    print("\n" + "=" * 80)
    print("TEST 1: URL Discovery")
    print("=" * 80)
    
    discovered_urls = scraper.crawl_website(url)
    
    print(f"\n✓ Discovery complete!")
    print(f"  Total pages discovered: {len(discovered_urls)}")
    print(f"\n  Discovered URLs:")
    for i, discovered_url in enumerate(discovered_urls, 1):
        print(f"    {i}. {discovered_url}")
    
    # Test 2: Full scraping with content extraction
    print("\n" + "=" * 80)
    print("TEST 2: Full Scraping")
    print("=" * 80)
    
    chunks = scraper.scrape_website_recursive(url)
    
    print(f"\n✓ Scraping complete!")
    print(f"  Total chunks extracted: {len(chunks)}")
    
    # Show statistics
    unique_sources = set(chunk["metadata"].get("source") for chunk in chunks)
    print(f"  Unique pages scraped: {len(unique_sources)}")
    
    if chunks:
        total_chars = sum(len(chunk["content"]) for chunk in chunks)
        avg_chunk_size = total_chars / len(chunks)
        print(f"  Total characters: {total_chars:,}")
        print(f"  Average chunk size: {avg_chunk_size:.0f} characters")
        
        # Show sample of first chunk
        print(f"\n  Sample from first chunk:")
        print(f"  Source: {chunks[0]['metadata'].get('source')}")
        print(f"  Content preview (first 200 chars):")
        print(f"  {chunks[0]['content'][:200]}...")
    
    print("\n" + "=" * 80)
    print("Test completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    # Default test URL - change this to your target website
    test_url = "https://example.com"
    
    # Allow URL to be passed as command line argument
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    
    print("\nIMPORTANT: Make sure to test with a website you have permission to scrape!")
    print(f"Testing with: {test_url}\n")
    
    try:
        test_crawler(test_url)
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
