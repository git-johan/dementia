"""
Base extractor interface for domain-specific content extraction.

This module provides the abstract base class and common utilities for
domain-specific content extractors. Each domain (e.g., helsedirektoratet.no,
fhi.no) should have its own extractor class implementing this interface.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re
import logging

logger = logging.getLogger(__name__)


class ExtractionResult:
    """Result object containing extracted content and metadata."""

    def __init__(
        self,
        content: str,
        title: Optional[str] = None,
        author: Optional[str] = None,
        date_published: Optional[str] = None,
        has_tables: bool = False,
        has_lists: bool = False,
        has_headings: bool = False,
        has_links: bool = False,
        structure_score: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.content = content
        self.title = title
        self.author = author
        self.date_published = date_published
        self.has_tables = has_tables
        self.has_lists = has_lists
        self.has_headings = has_headings
        self.has_links = has_links
        self.structure_score = structure_score
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for API responses."""
        return {
            "content": self.content,
            "title": self.title,
            "author": self.author,
            "date_published": self.date_published,
            "has_tables": self.has_tables,
            "has_lists": self.has_lists,
            "has_headings": self.has_headings,
            "has_links": self.has_links,
            "structure_score": self.structure_score,
            "metadata": self.metadata
        }


class BaseExtractor(ABC):
    """Abstract base class for domain-specific content extractors."""

    def __init__(self):
        self.domain_patterns = self.get_domain_patterns()
        self.supported_domains = self.get_supported_domains()

    @abstractmethod
    def get_supported_domains(self) -> List[str]:
        """Return list of domains this extractor supports."""
        pass

    @abstractmethod
    def get_domain_patterns(self) -> Dict[str, Any]:
        """Return domain-specific patterns for content detection."""
        pass

    @abstractmethod
    def extract_content(self, html: str, url: str) -> ExtractionResult:
        """Extract content from HTML for this domain."""
        pass

    def can_handle_domain(self, url: str) -> bool:
        """Check if this extractor can handle the given URL's domain."""
        try:
            domain = urlparse(url).netloc.lower()
            return domain in self.supported_domains
        except Exception as e:
            logger.warning(f"Error parsing URL {url}: {e}")
            return False

    def _create_soup(self, html: str) -> BeautifulSoup:
        """Create BeautifulSoup object with proper parsing."""
        return BeautifulSoup(html, 'html.parser')

    def _fix_encoding(self, text: str) -> str:
        """Fix common encoding issues in text content."""
        # Common encoding fixes
        encoding_fixes = {
            'Ã¦': 'æ',
            'Ã¥': 'å',
            'Ã¸': 'ø',
            'Ã†': 'Æ',
            'Ã…': 'Å',
            'Ã˜': 'Ø',
            'Â§': '§',
            '&quot;': '"',
            '&apos;': "'",
            '&lt;': '<',
            '&gt;': '>',
            '&amp;': '&'
        }

        for wrong, correct in encoding_fixes.items():
            text = text.replace(wrong, correct)

        return text

    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract page title from various possible sources."""
        # Try h1 first
        h1 = soup.find('h1')
        if h1 and h1.get_text(strip=True):
            return self._fix_encoding(h1.get_text(strip=True))

        # Try title tag
        title_tag = soup.find('title')
        if title_tag and title_tag.get_text(strip=True):
            title = title_tag.get_text(strip=True)
            # Remove common suffixes
            for suffix in [' - Helsedirektoratet', ' | alz.org', ' | Alzheimer Europe']:
                if title.endswith(suffix):
                    title = title[:-len(suffix)]
            return self._fix_encoding(title)

        return None

    def _remove_elements(self, soup: BeautifulSoup, selectors: List[str]) -> None:
        """Remove elements matching any of the given CSS selectors."""
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                element.decompose()

    def _extract_text_with_structure(self, element) -> str:
        """Extract text while preserving structure markers."""
        if not element:
            return ""

        result = []

        # Process all elements in order
        for child in element.descendants:
            if child.name == 'h1':
                result.append(f"\n[H1]{child.get_text(strip=True)}[/H1]\n")
            elif child.name == 'h2':
                result.append(f"\n[H2]{child.get_text(strip=True)}[/H2]\n")
            elif child.name == 'h3':
                result.append(f"\n[H3]{child.get_text(strip=True)}[/H3]\n")
            elif child.name == 'h4':
                result.append(f"\n[H4]{child.get_text(strip=True)}[/H4]\n")
            elif child.name == 'h5':
                result.append(f"\n[H5]{child.get_text(strip=True)}[/H5]\n")
            elif child.name == 'p':
                text = child.get_text(strip=True)
                if text:
                    result.append(f"\n[P]{text}[/P]\n")
            elif child.name == 'a' and child.get('href'):
                text = child.get_text(strip=True)
                href = child.get('href')
                if text and href:
                    result.append(f'[LINK href="{href}"]{text}[/LINK]')
            elif child.name in ['ul', 'ol']:
                result.append("\n[LIST_START]")
                for li in child.find_all('li', recursive=False):
                    item_text = li.get_text(strip=True)
                    if item_text:
                        result.append(f"\n [ITEM]{item_text}[/ITEM]")
                result.append("\n[LIST_END]\n")

        # Clean up excessive whitespace
        text = ' '.join(result)
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        text = re.sub(r'\s+', ' ', text)

        return self._fix_encoding(text.strip())

    def _calculate_structure_score(self, soup: BeautifulSoup) -> float:
        """Calculate a quality score based on content structure."""
        score = 0.0

        # Check for various structural elements
        if soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            score += 0.3

        if soup.find_all(['ul', 'ol']):
            score += 0.2

        if soup.find_all('p'):
            score += 0.2

        if soup.find_all('a'):
            score += 0.1

        # Check content length (not too short, not too long)
        text_length = len(soup.get_text())
        if 500 <= text_length <= 50000:
            score += 0.2

        return min(score, 1.0)

    def _extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract common metadata from the page."""
        metadata = {
            "url": url,
            "domain": urlparse(url).netloc
        }

        # Try to extract date from various sources
        date_patterns = [
            r'(\d{1,2})\.\s*(\w+)\s*(\d{4})',  # Norwegian format: "8. desember 2023"
            r'(\d{1,2})/(\d{1,2})/(\d{4})',    # US format: "12/8/2023"
            r'(\d{4})-(\d{1,2})-(\d{1,2})',    # ISO format: "2023-12-08"
        ]

        page_text = soup.get_text()
        for pattern in date_patterns:
            match = re.search(pattern, page_text)
            if match:
                metadata["date"] = match.group(0)
                break

        # Try to extract author
        author_patterns = [
            r'Forfatter:\s*([^,\n]+)',
            r'Utgitt av:\s*([^,\n]+)',
            r'Author:\s*([^,\n]+)',
        ]

        for pattern in author_patterns:
            match = re.search(pattern, page_text)
            if match:
                metadata["author"] = match.group(1).strip()
                break

        return metadata