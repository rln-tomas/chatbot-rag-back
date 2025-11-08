"""
Web scraping utilities with recursive crawling support.
"""

from typing import List, Set
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document


class WebScraper:
    """Web scraper with recursive crawling capabilities."""

    def __init__(
        self, 
        chunk_size: int = 2000, 
        chunk_overlap: int = 400,
        max_pages: int = 50,
        timeout: int = 10
    ):
        """
        Initialize web scraper.

        Args:
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            max_pages: Maximum number of pages to crawl (safety limit)
            timeout: Timeout for HTTP requests in seconds
        """
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
        self.max_pages = max_pages
        self.timeout = timeout

    def _get_domain(self, url: str) -> str:
        """
        Extract domain from URL.
        
        Args:
            url: URL to extract domain from
            
        Returns:
            Domain (e.g., 'example.com')
        """
        parsed = urlparse(url)
        return parsed.netloc

    def _is_same_domain(self, url: str, base_domain: str) -> bool:
        """
        Check if URL belongs to the same domain.
        
        Args:
            url: URL to check
            base_domain: Base domain to compare against
            
        Returns:
            True if same domain, False otherwise
        """
        return self._get_domain(url) == base_domain

    def _normalize_url(self, url: str) -> str:
        """
        Normalize URL by removing fragments and trailing slashes.
        
        Args:
            url: URL to normalize
            
        Returns:
            Normalized URL
        """
        parsed = urlparse(url)
        # Remove fragment and trailing slash
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if normalized.endswith('/') and len(normalized) > 1:
            normalized = normalized[:-1]
        return normalized

    def _extract_links(self, url: str, base_domain: str) -> Set[str]:
        """
        Extract all links from a page that belong to the same domain.
        
        Args:
            url: URL to extract links from
            base_domain: Base domain to filter links
            
        Returns:
            Set of normalized URLs from the same domain
        """
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            links = set()
            for anchor in soup.find_all('a', href=True):
                href = anchor['href']
                
                # Convert relative URLs to absolute
                absolute_url = urljoin(url, href)
                
                # Only keep links from the same domain
                if self._is_same_domain(absolute_url, base_domain):
                    # Skip non-HTTP(S) links and files
                    parsed = urlparse(absolute_url)
                    if parsed.scheme in ['http', 'https']:
                        # Skip common file extensions
                        if not any(absolute_url.lower().endswith(ext) for ext in [
                            '.pdf', '.jpg', '.jpeg', '.png', '.gif', '.zip', 
                            '.rar', '.doc', '.docx', '.xls', '.xlsx', '.mp4',
                            '.mp3', '.avi', '.mov', '.css', '.js'
                        ]):
                            normalized = self._normalize_url(absolute_url)
                            links.add(normalized)
            
            return links
            
        except Exception as e:
            print(f"Error extracting links from {url}: {str(e)}")
            return set()

    def crawl_website(self, start_url: str) -> List[str]:
        """
        Crawl website starting from a URL, discovering all pages in the same domain.
        
        Args:
            start_url: Starting URL to crawl from
            
        Returns:
            List of all discovered URLs from the same domain
        """
        base_domain = self._get_domain(start_url)
        start_url_normalized = self._normalize_url(start_url)
        
        visited: Set[str] = set()
        to_visit: Set[str] = {start_url_normalized}
        
        print(f"Starting crawl of {base_domain} from {start_url}")
        
        while to_visit and len(visited) < self.max_pages:
            current_url = to_visit.pop()
            
            if current_url in visited:
                continue
                
            print(f"Crawling [{len(visited) + 1}/{self.max_pages}]: {current_url}")
            visited.add(current_url)
            
            # Extract links from current page
            new_links = self._extract_links(current_url, base_domain)
            
            # Add new links to visit queue
            for link in new_links:
                if link not in visited and link not in to_visit:
                    to_visit.add(link)
        
        print(f"Crawl completed. Discovered {len(visited)} pages.")
        return list(visited)

    def scrape_url(self, url: str) -> List[dict]:
        """
        Scrape content from a single URL and split into chunks.

        Args:
            url: URL to scrape

        Returns:
            List of document chunks with metadata

        Raises:
            Exception: If scraping fails
        """
        try:
            # Load documents from URL
            loader = WebBaseLoader(url)
            documents = loader.load()

            # Split documents into chunks
            chunks = self.text_splitter.split_documents(documents)

            # Format chunks with metadata
            formatted_chunks = []
            for i, chunk in enumerate(chunks):
                formatted_chunks.append({
                    "content": chunk.page_content,
                    "metadata": {
                        **chunk.metadata,
                        "chunk_index": i,
                        "source": url
                    }
                })

            return formatted_chunks

        except Exception as e:
            print(f"Failed to scrape URL {url}: {str(e)}")
            return []

    def scrape_website_recursive(self, start_url: str) -> List[dict]:
        """
        Recursively scrape entire website starting from a URL.
        Discovers all pages in the same domain and scrapes them.
        
        Args:
            start_url: Starting URL to crawl and scrape
            
        Returns:
            List of all document chunks from all discovered pages
        """
        # First, discover all URLs in the website
        all_urls = self.crawl_website(start_url)
        
        # Then scrape each URL
        all_chunks = []
        
        print(f"\nStarting scraping of {len(all_urls)} discovered pages...")
        
        for i, url in enumerate(all_urls, 1):
            print(f"Scraping [{i}/{len(all_urls)}]: {url}")
            chunks = self.scrape_url(url)
            
            if chunks:
                all_chunks.extend(chunks)
                print(f"  ✓ Extracted {len(chunks)} chunks")
            else:
                print(f"  ✗ No content extracted")
        
        print(f"\nScraping completed. Total chunks: {len(all_chunks)}")
        return all_chunks

    def scrape_multiple_urls(self, urls: List[str]) -> List[dict]:
        """
        Scrape content from multiple URLs.

        Args:
            urls: List of URLs to scrape

        Returns:
            List of all document chunks from all URLs

        Raises:
            Exception: If scraping fails for any URL
        """
        all_chunks = []

        for url in urls:
            try:
                chunks = self.scrape_url(url)
                all_chunks.extend(chunks)
            except Exception as e:
                # Log error but continue with other URLs
                print(f"Error scraping {url}: {str(e)}")
                raise

        return all_chunks
