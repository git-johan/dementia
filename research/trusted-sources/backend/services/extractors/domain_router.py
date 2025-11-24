"""
Domain router for selecting appropriate content extractors.

Routes extraction requests to domain-specific extractors based on URL domain.
"""

from typing import Optional, Dict
from urllib.parse import urlparse
import logging

from .base_extractor import BaseExtractor
from .helsedirektoratet_no import HelsedirektoratetNoExtractor

logger = logging.getLogger(__name__)


class DomainRouter:
    """Routes extraction requests to appropriate domain-specific extractors."""

    def __init__(self):
        """Initialize router with available extractors."""
        self.extractors = {
            'helsedirektoratet.no': HelsedirektoratetNoExtractor(),
            'www.helsedirektoratet.no': HelsedirektoratetNoExtractor(),
        }

        # Build reverse mapping for quick lookup
        self.domain_mapping = {}
        for extractor in self.extractors.values():
            for domain in extractor.get_supported_domains():
                self.domain_mapping[domain.lower()] = extractor

    def get_extractor(self, url: str) -> Optional[BaseExtractor]:
        """Get the appropriate extractor for the given URL's domain."""
        try:
            domain = urlparse(url).netloc.lower()
            extractor = self.domain_mapping.get(domain)

            if extractor:
                logger.info(f"Using domain-specific extractor for {domain}")
                return extractor
            else:
                logger.info(f"No domain-specific extractor found for {domain}")
                return None

        except Exception as e:
            logger.error(f"Error determining extractor for {url}: {e}")
            return None

    def can_handle_domain(self, url: str) -> bool:
        """Check if we have a domain-specific extractor for this URL."""
        return self.get_extractor(url) is not None

    def get_supported_domains(self) -> Dict[str, str]:
        """Get mapping of supported domains to extractor names."""
        domain_info = {}
        for domain, extractor in self.domain_mapping.items():
            domain_info[domain] = extractor.__class__.__name__
        return domain_info