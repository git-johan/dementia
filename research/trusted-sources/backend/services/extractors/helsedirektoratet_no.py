"""
Helsedirektoratet.no domain-specific content extractor.

This extractor handles content from the Norwegian Directorate of Health,
including guidelines (veiledere), regulations (retningslinjer), and policy documents.
"""

from typing import List, Dict, Any
import re
from bs4 import BeautifulSoup
import logging

from .base_extractor import BaseExtractor, ExtractionResult

logger = logging.getLogger(__name__)


class HelsedirektoratetNoExtractor(BaseExtractor):
    """Content extractor for helsedirektoratet.no domain."""

    def get_supported_domains(self) -> List[str]:
        """Return domains this extractor supports."""
        return ["helsedirektoratet.no", "www.helsedirektoratet.no"]

    def get_domain_patterns(self) -> Dict[str, Any]:
        """Return Norwegian health directorate specific patterns."""
        return {
            "boilerplate_selectors": [
                # Navigation and site chrome
                ".navbar", ".nav-menu", ".breadcrumb", ".site-header", ".site-footer",
                ".cookie-banner", ".personvern", ".tilgjengelighet",
                # Print/share utilities
                ".print-button", ".share-buttons", ".social-share",
                # Sidebar content
                ".sidebar", ".related-content", ".related-links", ".kontaktinfo",
                # Advertisements and promotional content
                ".advertisement", ".promo", ".banner"
            ],
            "content_selectors": [
                ".main-content", "#content", ".page-content", ".article-content",
                ".veileder-content", ".retningslinje-content"
            ],
            "boilerplate_text_patterns": [
                r"Skriv ut \/ lag PDF",
                r"Se tidligere versjoner",
                r"Siste faglige endring:",
                r"Tilgjengelig fra https://",
                r"Åpne data \(API\)",
                r"FÃ¥ tilgang til innhold",
                r"https://utvikler\.helsedirektoratet\.no",
                r"Slik refererer du til innholdet",
                r"Helsedirektoratet \(\d{4}\)\."
            ],
            "content_type_indicators": {
                "guideline": ["veileder", "anbefaling", "råd"],
                "regulation": ["retningslinje", "forskrift", "bestemmelse"],
                "policy": ["rundskriv", "instruks", "directive"]
            }
        }

    def extract_content(self, html: str, url: str) -> ExtractionResult:
        """Extract content specifically for helsedirektoratet.no."""
        try:
            soup = self._create_soup(html)

            # Remove known boilerplate elements
            self._remove_helsedirektoratet_boilerplate(soup)

            # Extract main content
            content_element = self._find_main_content(soup)
            if not content_element:
                logger.warning(f"No main content found for {url}")
                return self._create_fallback_result(soup, url)

            # Extract structured content
            extracted_content = self._extract_text_with_structure(content_element)

            # Remove text-based boilerplate patterns
            extracted_content = self._remove_text_boilerplate(extracted_content)

            # Extract title
            title = self._extract_helsedirektoratet_title(soup)

            # Extract metadata
            metadata = self._extract_helsedirektoratet_metadata(soup, url)

            # Detect content features
            features = self._analyze_content_features(content_element)

            # Calculate quality score
            structure_score = self._calculate_helsedirektoratet_score(content_element, extracted_content)

            return ExtractionResult(
                content=extracted_content,
                title=title,
                author=metadata.get("author"),
                date_published=metadata.get("date"),
                has_tables=features["has_tables"],
                has_lists=features["has_lists"],
                has_headings=features["has_headings"],
                has_links=features["has_links"],
                structure_score=structure_score,
                metadata=metadata
            )

        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return self._create_fallback_result(self._create_soup(html), url)

    def _remove_helsedirektoratet_boilerplate(self, soup: BeautifulSoup) -> None:
        """Remove helsedirektoratet.no specific boilerplate elements."""
        patterns = self.get_domain_patterns()

        # Remove elements by CSS selectors
        self._remove_elements(soup, patterns["boilerplate_selectors"])

        # Remove citation and reference blocks
        citation_patterns = [
            lambda tag: tag.name == 'p' and 'Helsedirektoratet (' in tag.get_text(),
            lambda tag: tag.name == 'p' and 'Tilgjengelig fra https://' in tag.get_text(),
            lambda tag: tag.name == 'p' and 'Slik refererer du til innholdet' in tag.get_text()
        ]

        for pattern in citation_patterns:
            elements = soup.find_all(pattern)
            for element in elements:
                element.decompose()

    def _find_main_content(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Find the main content area for helsedirektoratet.no pages."""
        patterns = self.get_domain_patterns()

        # Try specific content selectors first
        for selector in patterns["content_selectors"]:
            element = soup.select_one(selector)
            if element:
                return element

        # Fallback: look for content indicators
        # Look for elements with substantial text content
        candidates = soup.find_all(['div', 'article', 'section'])
        best_candidate = None
        max_text_length = 0

        for candidate in candidates:
            # Skip if it's likely navigation or boilerplate
            class_name = ' '.join(candidate.get('class', []))
            if any(skip in class_name.lower() for skip in ['nav', 'header', 'footer', 'sidebar']):
                continue

            text_length = len(candidate.get_text(strip=True))
            if text_length > max_text_length:
                max_text_length = text_length
                best_candidate = candidate

        return best_candidate

    def _remove_text_boilerplate(self, text: str) -> str:
        """Remove text-based boilerplate patterns."""
        patterns = self.get_domain_patterns()

        for pattern in patterns["boilerplate_text_patterns"]:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)

        # Clean up whitespace
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        text = re.sub(r'\s+', ' ', text)

        return text.strip()

    def _extract_helsedirektoratet_title(self, soup: BeautifulSoup) -> str:
        """Extract title with helsedirektoratet.no specific patterns."""
        title = self._extract_title(soup)

        if title:
            # Remove domain suffix if present
            if title.endswith(' - Helsedirektoratet'):
                title = title[:-len(' - Helsedirektoratet')]

            # Clean up any remaining encoding issues
            title = self._fix_encoding(title)

        return title

    def _extract_helsedirektoratet_metadata(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract metadata specific to helsedirektoratet.no."""
        metadata = self._extract_metadata(soup, url)

        # Look for Norwegian date patterns
        text = soup.get_text()

        # Norwegian date patterns
        norwegian_date_patterns = [
            r'Siste faglige endring:\s*(\d{1,2})\.\s*(\w+)\s*(\d{4})',
            r'Publisert:\s*(\d{1,2})\.(\d{1,2})\.(\d{4})',
            r'Oppdatert:\s*(\d{1,2})\.(\d{1,2})\.(\d{4})'
        ]

        for pattern in norwegian_date_patterns:
            match = re.search(pattern, text)
            if match:
                metadata["last_updated"] = match.group(0)
                break

        # Detect content type
        content_type = self._detect_content_type(soup)
        if content_type:
            metadata["content_type"] = content_type

        # Extract subject area if available
        subject_patterns = [
            r'Fagområde:\s*([^,\n]+)',
            r'Tema:\s*([^,\n]+)'
        ]

        for pattern in subject_patterns:
            match = re.search(pattern, text)
            if match:
                metadata["subject_area"] = match.group(1).strip()
                break

        return metadata

    def _detect_content_type(self, soup: BeautifulSoup) -> str:
        """Detect the type of helsedirektoratet content."""
        patterns = self.get_domain_patterns()
        title = soup.find('title')
        h1 = soup.find('h1')

        text_to_analyze = ""
        if title:
            text_to_analyze += title.get_text().lower()
        if h1:
            text_to_analyze += " " + h1.get_text().lower()

        for content_type, indicators in patterns["content_type_indicators"].items():
            if any(indicator in text_to_analyze for indicator in indicators):
                return content_type

        return "general"

    def _analyze_content_features(self, element: BeautifulSoup) -> Dict[str, bool]:
        """Analyze structural features of the content."""
        return {
            "has_tables": bool(element.find_all('table')),
            "has_lists": bool(element.find_all(['ul', 'ol'])),
            "has_headings": bool(element.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])),
            "has_links": bool(element.find_all('a', href=True))
        }

    def _calculate_helsedirektoratet_score(self, element: BeautifulSoup, content: str) -> float:
        """Calculate quality score specific to helsedirektoratet content."""
        base_score = self._calculate_structure_score(element)

        # Additional scoring for helsedirektoratet-specific patterns
        bonus = 0.0

        # Bonus for Norwegian legal/medical structure
        if any(pattern in content for pattern in ['§', 'jf.', 'forskriften']):
            bonus += 0.1

        # Bonus for guideline structure
        if any(pattern in content for pattern in ['[H3]', 'anbefaling', 'veileder']):
            bonus += 0.1

        # Bonus for proper Norwegian encoding (no corruption detected)
        if 'Ã' not in content:  # No encoding corruption
            bonus += 0.1

        return min(base_score + bonus, 1.0)

    def _create_fallback_result(self, soup: BeautifulSoup, url: str) -> ExtractionResult:
        """Create a basic extraction result when main extraction fails."""
        title = self._extract_title(soup)
        basic_content = soup.get_text()

        if basic_content:
            basic_content = self._fix_encoding(basic_content)
            basic_content = re.sub(r'\s+', ' ', basic_content).strip()

        return ExtractionResult(
            content=basic_content or "No content extracted",
            title=title,
            structure_score=0.1,
            metadata={"url": url, "extraction_method": "fallback"}
        )