"""
Web scraping utilities using LangChain WebBaseLoader.
"""

from typing import List
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


class WebScraper:
    """Web scraper using LangChain WebBaseLoader."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize web scraper.

        Args:
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
        """
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )

    def scrape_url(self, url: str) -> List[dict]:
        """
        Scrape content from URL and split into chunks.

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
            raise Exception(f"Failed to scrape URL {url}: {str(e)}")

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
