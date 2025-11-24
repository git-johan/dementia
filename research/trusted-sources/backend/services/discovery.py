#!/usr/bin/env python3
"""
Discovery service for finding sitemaps and collecting URLs from trusted sources.
"""

import time
import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional, Set
from urllib.parse import urlparse, urljoin
import re
from datetime import datetime
import logging

from models.trusted_sources import UrlCreate, JobType, JobStatus, UrlStatus
from services.database import get_trusted_sources_db


logger = logging.getLogger(__name__)


class DiscoveryService:
    """Service for discovering sitemaps and collecting URLs."""

    def __init__(self):
        self.db = get_trusted_sources_db()

        # Dementia/Alzheimer's related keywords for URL filtering
        self.dementia_keywords = [
            'demens', 'dementia', 'alzheimer', 'alz', 'kognitiv', 'cognitive',
            'hukommelse', 'memory', 'glemsel', 'forgetfulness', 'hjernehelse',
            'brain-health', 'nevrologi', 'neurology', 'frontotemporal',
            'lewy-body', 'vaskulær', 'vascular'
        ]

    def _contains_dementia_keywords(self, url: str) -> bool:
        """Check if URL contains dementia-related keywords."""
        url_lower = url.lower()
        return any(keyword.lower() in url_lower for keyword in self.dementia_keywords)

    def discover_sitemaps(self, domain: str) -> List[str]:
        """
        Discover sitemap URLs for a domain.

        Args:
            domain: Domain to search for sitemaps

        Returns:
            List of discovered sitemap URLs
        """
        logger.info(f"🔍 Starting sitemap discovery for domain: {domain}")

        # Ensure domain doesn't have protocol
        domain = domain.replace('https://', '').replace('http://', '').rstrip('/')

        discovered_sitemaps = []

        # Try robots.txt first
        robots_sitemaps = self._check_robots_txt(domain)
        if robots_sitemaps:
            discovered_sitemaps.extend(robots_sitemaps)
            logger.info(f"   ✓ Found {len(robots_sitemaps)} sitemaps in robots.txt")

        # Try common sitemap locations
        common_sitemaps = self._check_common_locations(domain)
        for sitemap in common_sitemaps:
            if sitemap not in discovered_sitemaps:
                discovered_sitemaps.append(sitemap)
                logger.info(f"   ✓ Found sitemap at common location: {sitemap}")

        if not discovered_sitemaps:
            logger.warning(f"   ⚠️  No sitemaps found for {domain}")
        else:
            logger.info(f"   📋 Total sitemaps discovered: {len(discovered_sitemaps)}")

        return discovered_sitemaps

    def _check_robots_txt(self, domain: str) -> List[str]:
        """Check robots.txt for sitemap directives."""
        robots_url = f"https://www.{domain}/robots.txt"
        sitemaps = []

        try:
            response = requests.get(robots_url, timeout=10)
            if response.status_code == 200:
                content = response.text
                # Look for Sitemap: directives
                for line in content.split('\n'):
                    line = line.strip()
                    if line.lower().startswith('sitemap:'):
                        sitemap_url = line.split(':', 1)[1].strip()
                        sitemaps.append(sitemap_url)
            elif response.status_code == 404:
                # Try without www
                robots_url = f"https://{domain}/robots.txt"
                response = requests.get(robots_url, timeout=10)
                if response.status_code == 200:
                    content = response.text
                    for line in content.split('\n'):
                        line = line.strip()
                        if line.lower().startswith('sitemap:'):
                            sitemap_url = line.split(':', 1)[1].strip()
                            sitemaps.append(sitemap_url)
        except Exception as e:
            logger.warning(f"   ⚠️  Could not fetch robots.txt: {e}")

        return sitemaps

    def _check_common_locations(self, domain: str) -> List[str]:
        """Check common sitemap locations."""
        common_paths = [
            "/sitemap.xml",
            "/sitemap_index.xml",
            "/sitemap-index.xml",
            "/sitemaps.xml"
        ]

        found_sitemaps = []

        for path in common_paths:
            for subdomain in [f"www.{domain}", domain]:
                sitemap_url = f"https://{subdomain}{path}"
                if self._validate_sitemap(sitemap_url):
                    found_sitemaps.append(sitemap_url)
                    break  # Found one, no need to try other subdomains

                time.sleep(0.5)  # Be respectful

        return found_sitemaps

    def _validate_sitemap(self, sitemap_url: str) -> bool:
        """Validate that a sitemap URL is accessible and contains XML."""
        try:
            response = requests.get(sitemap_url, timeout=10)
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '').lower()
                if 'xml' in content_type or response.text.strip().startswith('<?xml'):
                    return True
        except Exception:
            pass
        return False

    def collect_urls_from_sitemap(self, job_id: str, sitemap_url: str,
                                  domain: str, path_filter: Optional[str] = None,
                                  enable_keyword_filter: bool = True) -> int:
        """
        Collect URLs from a sitemap and store in database.

        Args:
            job_id: Job ID for tracking
            sitemap_url: URL of the sitemap
            domain: Domain being processed
            path_filter: Optional path filter to limit URLs

        Returns:
            Number of URLs collected
        """
        logger.info(f"📄 Starting URL collection from: {sitemap_url}")

        all_urls = []
        processed_sitemaps: Set[str] = set()
        total_urls_found = 0
        filtered_out_by_path = 0
        filtered_out_by_keywords = 0

        def process_sitemap(url: str, depth: int = 0) -> None:
            nonlocal total_urls_found, filtered_out_by_path, filtered_out_by_keywords
            if url in processed_sitemaps or depth > 2:  # Prevent infinite loops
                return

            processed_sitemaps.add(url)
            content = self._fetch_sitemap(url)
            if not content:
                return

            urls = self._parse_sitemap_xml(content)

            for url_data in urls:
                if url_data.get('type') == 'sitemap_index':
                    # This is a reference to another sitemap
                    logger.info(f"   🔗 Found nested sitemap: {url_data['url']}")
                    process_sitemap(url_data['url'], depth + 1)
                else:
                    # This is a regular URL
                    total_urls_found += 1
                    url_path = urlparse(url_data['url']).path
                    url_full = url_data['url']

                    # Apply path filter if specified
                    if path_filter and not url_path.startswith(path_filter):
                        filtered_out_by_path += 1
                        continue

                    # Apply dementia keyword filter if enabled
                    if enable_keyword_filter and not self._contains_dementia_keywords(url_full):
                        filtered_out_by_keywords += 1
                        continue

                    all_urls.append(url_data)

        # Start processing from the main sitemap
        process_sitemap(sitemap_url)

        # Log filtering statistics
        filtered_urls = len(all_urls)
        logger.info(f"   📊 URL Processing Summary:")
        logger.info(f"       Total URLs found: {total_urls_found}")
        logger.info(f"       Filtered by path: {filtered_out_by_path}")
        logger.info(f"       Filtered by keywords: {filtered_out_by_keywords}")
        logger.info(f"       URLs passed filtering: {filtered_urls}")

        if not all_urls:
            logger.warning(f"   ⚠️  No URLs passed filtering")
            return 0

        # Convert to UrlCreate objects and store in database
        url_creates = []
        for url_data in all_urls:
            url_create = UrlCreate(
                url=url_data['url'],
                domain=domain,
                sitemap_url=sitemap_url,
                priority=url_data.get('priority'),
                lastmod=url_data.get('lastmod'),
                changefreq=url_data.get('changefreq'),
                path_filter=path_filter
            )
            url_creates.append(url_create)

        # Store URLs in batches
        batch_size = 100
        stored_count = 0

        for i in range(0, len(url_creates), batch_size):
            batch = url_creates[i:i + batch_size]
            try:
                count = self.db.add_urls_batch(batch)
                stored_count += count
                logger.info(f"   ⏳ Stored batch {i//batch_size + 1}: {count} URLs")

                # Update job progress
                self.db.update_job_progress(job_id, stored_count, 0)

            except Exception as e:
                logger.error(f"   ❌ Failed to store URL batch: {e}")

        logger.info(f"   ✅ Successfully stored {stored_count} URLs")

        # Update domain's total_urls_found count
        try:
            domain_record = self.db.get_domain_by_name(domain)
            if domain_record:
                old_count = domain_record.total_urls_found
                self.db._update_domain_url_count(domain_record.id, stored_count)
                new_total = old_count + stored_count

                if stored_count > 0:
                    logger.info(f"   📊 Added {stored_count} URLs to domain {domain} (now {new_total} total)")
                else:
                    logger.info(f"   📊 No new URLs added to domain {domain} (still {old_count} total, {stored_count} duplicates skipped)")
        except Exception as e:
            logger.warning(f"   ⚠️  Failed to update domain URL count: {e}")

        return stored_count

    def _fetch_sitemap(self, sitemap_url: str) -> Optional[str]:
        """Fetch sitemap content from URL."""
        try:
            logger.info(f"   📥 Fetching: {sitemap_url}")
            response = requests.get(sitemap_url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"   ❌ Error fetching sitemap: {e}")
            return None

    def _parse_sitemap_xml(self, xml_content: str) -> List[Dict]:
        """Parse XML sitemap content and extract URLs with metadata."""
        urls = []

        try:
            root = ET.fromstring(xml_content)

            # Handle different XML namespaces
            namespaces = {
                'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9',
                '': 'http://www.sitemaps.org/schemas/sitemap/0.9'
            }

            # Check if this is a sitemap index file
            sitemap_elements = root.findall('.//sitemap:sitemap', namespaces) or root.findall('.//sitemap', namespaces)
            if sitemap_elements:
                logger.info(f"   📂 Sitemap index with {len(sitemap_elements)} sitemaps")
                for sitemap_elem in sitemap_elements:
                    loc_elem = sitemap_elem.find('.//sitemap:loc', namespaces) or sitemap_elem.find('.//loc', namespaces)
                    if loc_elem is not None:
                        urls.append({
                            'url': loc_elem.text.strip(),
                            'type': 'sitemap_index',
                            'priority': None,
                            'lastmod': None,
                            'changefreq': None
                        })
                return urls

            # Parse regular sitemap with URL entries
            url_elements = root.findall('.//sitemap:url', namespaces) or root.findall('.//url', namespaces)

            for url_elem in url_elements:
                loc_elem = url_elem.find('.//sitemap:loc', namespaces) or url_elem.find('.//loc', namespaces)
                if loc_elem is None:
                    continue

                url = loc_elem.text.strip() if loc_elem.text else None
                if not url:
                    continue

                # Extract optional metadata
                priority_elem = url_elem.find('.//sitemap:priority', namespaces) or url_elem.find('.//priority', namespaces)
                lastmod_elem = url_elem.find('.//sitemap:lastmod', namespaces) or url_elem.find('.//lastmod', namespaces)
                changefreq_elem = url_elem.find('.//sitemap:changefreq', namespaces) or url_elem.find('.//changefreq', namespaces)

                urls.append({
                    'url': url,
                    'priority': float(priority_elem.text) if priority_elem is not None and priority_elem.text else None,
                    'lastmod': lastmod_elem.text.strip() if lastmod_elem is not None and lastmod_elem.text else None,
                    'changefreq': changefreq_elem.text.strip() if changefreq_elem is not None and changefreq_elem.text else None
                })

        except ET.ParseError as e:
            logger.error(f"   ❌ Error parsing XML: {e}")
            return []
        except Exception as e:
            logger.error(f"   ❌ Unexpected error parsing sitemap: {e}")
            return []

        return urls

    def discover_and_collect(self, domain: str, path_filter: Optional[str] = None,
                           enable_keyword_filter: bool = True) -> Dict:
        """
        Complete discovery and collection workflow for a domain.

        Args:
            domain: Domain to process
            path_filter: Optional path filter

        Returns:
            Dictionary with results and job info
        """
        # Generate job ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        job_id = f"discover_{domain}_{timestamp}"

        # Create job in database
        self.db.create_job(job_id, domain, JobType.DISCOVER)

        try:
            # Discover sitemaps
            sitemaps = self.discover_sitemaps(domain)

            if not sitemaps:
                self.db.complete_job(job_id, JobStatus.FAILED, "No sitemaps found")
                return {
                    "job_id": job_id,
                    "domain": domain,
                    "sitemap_url": None,
                    "urls_found": 0,
                    "status": JobStatus.FAILED,
                    "error": "No sitemaps found"
                }

            # Use the first sitemap found
            sitemap_url = sitemaps[0]

            # Collect URLs
            urls_found = self.collect_urls_from_sitemap(job_id, sitemap_url, domain, path_filter, enable_keyword_filter)

            # Update job with final counts
            self.db.update_job_progress(job_id, urls_found, 0)
            self.db.complete_job(job_id, JobStatus.COMPLETED)

            return {
                "job_id": job_id,
                "domain": domain,
                "sitemap_url": sitemap_url,
                "urls_found": urls_found,
                "status": JobStatus.COMPLETED
            }

        except Exception as e:
            logger.error(f"❌ Discovery failed for {domain}: {e}")
            self.db.complete_job(job_id, JobStatus.FAILED, str(e))
            return {
                "job_id": job_id,
                "domain": domain,
                "sitemap_url": None,
                "urls_found": 0,
                "status": JobStatus.FAILED,
                "error": str(e)
            }


def get_discovery_service() -> DiscoveryService:
    """Get discovery service instance."""
    return DiscoveryService()