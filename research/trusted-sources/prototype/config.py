"""
Configuration management for trusted sources research
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Any

class TrustedSourcesConfig:
    """Configuration loader for trusted sources research"""

    def __init__(self, config_path: Path = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "data" / "trusted_domains.json"

        self.config_path = config_path
        self.config = self._load_config()
        self.logger = logging.getLogger("trusted-sources")

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_norwegian_sources(self) -> Dict[str, Dict]:
        """Get Norwegian health authority sources"""
        return self.config.get("norwegian_health_authorities", {})

    def get_international_sources(self) -> Dict[str, Dict]:
        """Get international sources"""
        return self.config.get("international_sources", {})

    def get_all_sources(self) -> Dict[str, Dict]:
        """Get all sources combined"""
        all_sources = {}
        all_sources.update(self.get_norwegian_sources())
        all_sources.update(self.get_international_sources())
        return all_sources

    def get_sources_by_priority(self, priority: str) -> Dict[str, Dict]:
        """Get sources filtered by priority level"""
        sources = {}
        for domain, config in self.get_all_sources().items():
            if config.get("priority") == priority:
                sources[domain] = config
        return sources

    def get_max_pages_for_domain(self, domain: str) -> int:
        """Get max pages to collect for a domain based on its priority"""
        source_config = self.get_all_sources().get(domain, {})
        priority = source_config.get("priority", "low")

        max_pages_config = self.config.get("research_settings", {}).get("max_pages_per_domain", {})
        return max_pages_config.get(priority, 10)

    def get_crawl_delay(self) -> float:
        """Get crawl delay in seconds"""
        return self.config.get("research_settings", {}).get("crawl_delay_seconds", 1.0)

    def get_content_filters(self) -> Dict[str, Any]:
        """Get content filtering settings"""
        return {
            "min_length": self.config.get("research_settings", {}).get("content_min_length", 500),
            "max_age_days": self.config.get("research_settings", {}).get("content_max_age_days", 730),
            "quality_threshold": self.config.get("research_settings", {}).get("quality_threshold", 0.7)
        }

    def is_trusted_domain(self, domain: str) -> bool:
        """Check if a domain is in our trusted list"""
        return domain in self.get_all_sources()

    def get_domain_info(self, domain: str) -> Dict[str, Any]:
        """Get configuration info for a specific domain"""
        return self.get_all_sources().get(domain, {})