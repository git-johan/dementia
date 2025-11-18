"""
Content collector for trusted sources research
"""
import requests
import time
import hashlib
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from readability import Document

from .config import TrustedSourcesConfig
from .storage import TrustedSourcesStorage, CollectedContent


class ContentCollector:
    """Collects content from trusted domains"""

    def __init__(self, config: TrustedSourcesConfig, storage: TrustedSourcesStorage):
        self.config = config
        self.storage = storage
        self.logger = logging.getLogger("trusted-sources.collector")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Dementia Care Research Bot (Norwegian Health Information Collection)'
        })

    def collect_from_domain(self, domain: str, max_pages: int = None) -> Dict[str, Any]:
        """Collect content from a specific domain"""
        if not self.config.is_trusted_domain(domain):
            raise ValueError(f"Domain {domain} is not in trusted sources list")

        if max_pages is None:
            max_pages = self.config.get_max_pages_for_domain(domain)

        domain_info = self.config.get_domain_info(domain)
        self.logger.info(f"Starting collection from {domain} (max {max_pages} pages)")

        # Create collection job
        job_id = self.storage.create_collection_job(domain, max_pages)

        try:
            self.storage.update_collection_job(job_id, "running")

            # Discover pages
            pages = self._discover_pages(domain, max_pages)
            self.logger.info(f"Discovered {len(pages)} pages from {domain}")

            # Collect content from discovered pages
            collected_count = 0
            for page_url in pages:
                try:
                    content = self._collect_page_content(page_url, domain)
                    if content:
                        self.storage.store_content(content)
                        collected_count += 1
                        self.logger.info(f"Collected content from {page_url}")

                    # Respectful crawling delay
                    time.sleep(self.config.get_crawl_delay())

                except Exception as e:
                    self.logger.error(f"Failed to collect from {page_url}: {e}")
                    continue

            # Update job status
            self.storage.update_collection_job(job_id, "completed", collected_count)

            result = {
                "domain": domain,
                "pages_discovered": len(pages),
                "pages_collected": collected_count,
                "job_id": job_id,
                "status": "completed"
            }

            self.logger.info(f"Completed collection from {domain}: {collected_count}/{len(pages)} pages")
            return result

        except Exception as e:
            self.storage.update_collection_job(job_id, "failed", collected_count, str(e))
            self.logger.error(f"Collection from {domain} failed: {e}")
            return {
                "domain": domain,
                "status": "failed",
                "error": str(e),
                "job_id": job_id
            }

    def _discover_pages(self, domain: str, max_pages: int) -> List[str]:
        """Discover relevant pages on the domain"""
        # Simple implementation: start with domain root and common health paths
        base_urls = [
            f"https://{domain}",
            f"https://{domain}/demens",
            f"https://{domain}/demensomsorg",
            f"https://{domain}/alzheimer",
            f"https://{domain}/aldersdemens",
            f"https://{domain}/hukommelse"
        ]

        discovered_pages = set()
        domain_info = self.config.get_domain_info(domain)

        # Add path filters if specified
        path_filters = domain_info.get("path_filters", [])
        for path_filter in path_filters:
            base_urls.append(f"https://{domain}{path_filter}")

        for base_url in base_urls:
            if len(discovered_pages) >= max_pages:
                break

            try:
                pages = self._crawl_for_pages(base_url, domain, max_pages - len(discovered_pages))
                discovered_pages.update(pages)

            except Exception as e:
                self.logger.warning(f"Failed to discover pages from {base_url}: {e}")
                continue

        return list(discovered_pages)[:max_pages]

    def _crawl_for_pages(self, start_url: str, domain: str, max_pages: int) -> List[str]:
        """Crawl starting from a URL to discover relevant pages"""
        try:
            response = self.session.get(start_url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            found_pages = set([start_url])

            # Find links that might contain dementia-related content
            dementia_keywords = [
                'demens', 'demensomsorg', 'alzheimer', 'hukommelse',
                'aldersdemens', 'kognitiv', 'glemsomhet'
            ]

            for link in soup.find_all('a', href=True):
                if len(found_pages) >= max_pages:
                    break

                href = link.get('href')
                if not href:
                    continue

                # Convert relative URLs to absolute
                full_url = urljoin(start_url, href)
                parsed_url = urlparse(full_url)

                # Only include URLs from the same domain
                if parsed_url.netloc != domain:
                    continue

                # Check if URL or link text contains dementia keywords
                link_text = link.get_text().lower()
                url_path = parsed_url.path.lower()

                if any(keyword in link_text or keyword in url_path for keyword in dementia_keywords):
                    found_pages.add(full_url)

            return list(found_pages)

        except Exception as e:
            self.logger.error(f"Failed to crawl {start_url}: {e}")
            return []

    def _collect_page_content(self, url: str, domain: str) -> Optional[CollectedContent]:
        """Collect and process content from a single page"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()

            # Use readability to extract main content
            doc = Document(response.content)
            title = doc.title()
            main_content = doc.summary()

            # Parse with BeautifulSoup for additional processing
            soup = BeautifulSoup(main_content, 'html.parser')

            # Extract clean text
            text_content = soup.get_text()
            text_content = ' '.join(text_content.split())  # Clean whitespace

            # Content quality check
            content_filters = self.config.get_content_filters()
            if len(text_content) < content_filters["min_length"]:
                self.logger.debug(f"Content too short from {url}: {len(text_content)} chars")
                return None

            # Create content hash for deduplication
            content_hash = hashlib.md5(text_content.encode('utf-8')).hexdigest()

            # Check for duplicates
            if self.storage.check_duplicate_content(content_hash):
                self.logger.debug(f"Duplicate content found from {url}")
                return None

            # Calculate basic quality score
            quality_score = self._calculate_quality_score(text_content, title)

            # Create metadata
            metadata = {
                "url": url,
                "domain": domain,
                "content_length": len(text_content),
                "title_length": len(title),
                "collection_method": "readability",
                "response_status": response.status_code,
                "response_encoding": response.encoding
            }

            return CollectedContent(
                url=url,
                domain=domain,
                title=title,
                content=text_content,
                raw_html=response.text,
                metadata=metadata,
                collection_date=datetime.now().isoformat(),
                content_hash=content_hash,
                quality_score=quality_score
            )

        except Exception as e:
            self.logger.error(f"Failed to collect content from {url}: {e}")
            return None

    def _calculate_quality_score(self, content: str, title: str) -> float:
        """Calculate a basic quality score for content"""
        score = 0.0

        # Base score for having content
        if content and title:
            score += 0.3

        # Length scoring (prefer substantial content)
        content_length = len(content)
        if content_length > 1000:
            score += 0.3
        elif content_length > 500:
            score += 0.2
        else:
            score += 0.1

        # Norwegian dementia keyword bonus
        norwegian_keywords = [
            'demens', 'demensomsorg', 'alzheimer', 'hukommelse',
            'aldersdemens', 'kognitiv', 'pleie', 'omsorg'
        ]

        content_lower = content.lower()
        keyword_matches = sum(1 for keyword in norwegian_keywords if keyword in content_lower)
        keyword_score = min(keyword_matches * 0.05, 0.2)  # Up to 0.2 bonus
        score += keyword_score

        # Title quality (descriptive titles score higher)
        title_lower = title.lower()
        if any(keyword in title_lower for keyword in norwegian_keywords):
            score += 0.1

        # Structure bonus (look for structured content)
        if content.count('\n') > 5:  # Multiple paragraphs
            score += 0.1

        return min(score, 1.0)  # Cap at 1.0