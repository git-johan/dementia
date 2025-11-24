#!/usr/bin/env python3
"""
Scraper service for downloading HTML content with background jobs and test mode.
"""

import time
import json
import threading
from typing import Optional, List
from datetime import datetime
import requests
import logging

from models.trusted_sources import JobType, JobStatus, UrlStatus
from services.database import get_trusted_sources_db


logger = logging.getLogger(__name__)


class ScraperService:
    """Service for downloading HTML content with background job support."""

    def __init__(self):
        self.db = get_trusted_sources_db()

    def start_scraping_job(self, domain: str, limit: Optional[int] = None) -> str:
        """
        Start a background scraping job for a domain.

        Args:
            domain: Domain to scrape
            limit: Optional limit for test mode

        Returns:
            Job ID for tracking
        """
        # Generate job ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        job_id = f"scrape_{domain}_{timestamp}"

        # Get URLs to scrape
        urls = self.db.get_urls(domain=domain, status=UrlStatus.PENDING, limit=1000)  # Get all pending

        if not urls:
            logger.warning(f"⚠️  No pending URLs found for domain: {domain}")
            # Create a failed job
            self.db.create_job(job_id, domain, JobType.SCRAPE, 0, limit)
            self.db.complete_job(job_id, JobStatus.FAILED, "No pending URLs found")
            return job_id

        # Apply test mode limit
        total_urls = len(urls)
        if limit and limit < total_urls:
            urls = urls[:limit]
            total_urls = limit
            logger.info(f"🧪 TEST MODE: Limited to {limit} URLs out of {len(urls)} available")

        # Create job in database
        self.db.create_job(job_id, domain, JobType.SCRAPE, total_urls, limit)

        # Start background thread
        thread = threading.Thread(
            target=self._scrape_urls_background,
            args=(job_id, domain, urls),
            daemon=True
        )
        thread.start()

        logger.info(f"🚀 Started scraping job {job_id} for {domain} with {total_urls} URLs")

        return job_id

    def _scrape_urls_background(self, job_id: str, domain: str, urls: List) -> None:
        """Background worker for scraping URLs."""
        logger.info(f"🔧 Background scraping started: {job_id}")

        total_urls = len(urls)
        processed_count = 0
        failed_count = 0

        # Get job info for test mode detection
        job = self.db.get_job(job_id)
        test_mode = job and job.limit is not None

        for i, url_record in enumerate(urls):
            try:
                # Log progress with URL-level detail
                progress_info = f"progress={processed_count + 1}/{total_urls} remaining={total_urls - processed_count - 1}"
                test_mode_info = " (TEST_MODE)" if test_mode else ""

                start_time = time.time()

                # Download HTML content
                html, headers, error = self._download_url(url_record.url)

                scrape_time = time.time() - start_time

                if html:
                    # Store raw content
                    content_id = self.db.add_raw_content(
                        url_id=url_record.id,
                        html=html,
                        headers=json.dumps(headers) if headers else None
                    )

                    # Update URL status
                    self.db.update_url_status(url_record.id, UrlStatus.SCRAPED)

                    # Log success
                    size_kb = len(html.encode('utf-8')) // 1024
                    logger.info(f"[SUCCESS] URL_SCRAPED job_id={job_id} url={url_record.url} "
                               f"status=scraped size={size_kb}kb time={scrape_time:.1f}s {progress_info}{test_mode_info}")

                else:
                    # Update URL as failed
                    self.db.update_url_status(url_record.id, UrlStatus.FAILED, error)
                    failed_count += 1

                    # Log failure
                    logger.error(f"[ERROR] URL_FAILED job_id={job_id} url={url_record.url} "
                                f"status=failed error=\"{error}\" time={scrape_time:.1f}s {progress_info}{test_mode_info}")

                processed_count += 1

                # Update job progress
                self.db.update_job_progress(job_id, processed_count, failed_count)

                # Log batch progress every 10 URLs
                if processed_count % 10 == 0:
                    success_count = processed_count - failed_count
                    logger.info(f"[INFO] JOB_PROGRESS job_id={job_id} completed={processed_count}/{total_urls}({processed_count/total_urls*100:.1f}%) "
                               f"remaining={total_urls-processed_count} success={success_count} failed={failed_count}{test_mode_info}")

                # Be respectful - delay between requests
                time.sleep(1.5)

            except Exception as e:
                logger.error(f"❌ Error processing URL {url_record.url}: {e}")
                failed_count += 1
                processed_count += 1

                # Update URL and job
                self.db.update_url_status(url_record.id, UrlStatus.FAILED, str(e))
                self.db.update_job_progress(job_id, processed_count, failed_count)

        # Complete the job
        success_count = processed_count - failed_count
        success_rate = (success_count / total_urls * 100) if total_urls > 0 else 0

        if failed_count == total_urls:
            # All failed
            self.db.complete_job(job_id, JobStatus.FAILED, f"All {total_urls} URLs failed")
            logger.error(f"[ERROR] JOB_FAILED job_id={job_id} domain={domain} reason=\"All URLs failed\" "
                        f"progress={processed_count}/{total_urls}(100%){test_mode_info}")
        else:
            # Completed successfully
            self.db.complete_job(job_id, JobStatus.COMPLETED)
            job_time = datetime.now()
            logger.info(f"[SUCCESS] JOB_COMPLETED job_id={job_id} domain={domain} total={total_urls} "
                       f"scraped={success_count} failed={failed_count} success_rate={success_rate:.1f}%{test_mode_info}")

    def _download_url(self, url: str) -> tuple[Optional[str], Optional[dict], Optional[str]]:
        """
        Download HTML content from a URL.

        Returns:
            Tuple of (html_content, headers_dict, error_message)
        """
        try:
            headers = {
                'User-Agent': 'TrustedSources/1.0 (Norwegian dementia care research; respectful crawler)',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'no,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Cache-Control': 'no-cache'
            }

            response = requests.get(
                url,
                headers=headers,
                timeout=30,
                allow_redirects=True,
                verify=True
            )

            if response.status_code == 200:
                content_type = response.headers.get('content-type', '').lower()
                if 'html' in content_type:
                    return response.text, dict(response.headers), None
                else:
                    return None, None, f"Non-HTML content type: {content_type}"
            else:
                return None, None, f"HTTP {response.status_code}"

        except requests.exceptions.Timeout:
            return None, None, "Connection timeout"
        except requests.exceptions.ConnectionError:
            return None, None, "Connection error"
        except requests.exceptions.RequestException as e:
            return None, None, f"Request error: {str(e)}"
        except Exception as e:
            return None, None, f"Unexpected error: {str(e)}"

    def retry_failed_urls(self, domain: str, urls: Optional[List[str]] = None) -> str:
        """
        Retry failed URLs for a domain.

        Args:
            domain: Domain to retry
            urls: Specific URLs to retry (optional)

        Returns:
            Job ID for the retry operation
        """
        # Generate job ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        job_id = f"retry_{domain}_{timestamp}"

        if urls:
            # Retry specific URLs
            # Get URL records for the specified URLs
            url_records = []
            with self.db.get_session() as session:
                for url in urls:
                    record = session.query(self.db.UrlRecord).filter_by(url=url, domain=domain).first()
                    if record:
                        # Reset status to pending
                        record.status = UrlStatus.PENDING
                        record.error_message = None
                        url_records.append(record)
                session.commit()
        else:
            # Retry all failed URLs for domain
            url_records = self.db.get_urls(domain=domain, status=UrlStatus.FAILED, limit=1000)

        if not url_records:
            logger.warning(f"⚠️  No failed URLs found to retry for domain: {domain}")
            self.db.create_job(job_id, domain, JobType.SCRAPE, 0)
            self.db.complete_job(job_id, JobStatus.FAILED, "No failed URLs to retry")
            return job_id

        total_urls = len(url_records)
        self.db.create_job(job_id, domain, JobType.SCRAPE, total_urls)

        # Start background thread for retry
        thread = threading.Thread(
            target=self._scrape_urls_background,
            args=(job_id, domain, url_records),
            daemon=True
        )
        thread.start()

        logger.info(f"🔄 Started retry job {job_id} for {domain} with {total_urls} failed URLs")

        return job_id

    def scrape_url_direct(self, url_id: int) -> dict:
        """
        Directly scrape a single URL and store the result.

        Args:
            url_id: The URL ID to scrape

        Returns:
            Dictionary with scraping result
        """
        # Get the URL record
        url_record = self.db.get_url_by_id(url_id)
        if not url_record:
            return {
                "success": False,
                "error": f"URL with ID {url_id} not found",
                "url_id": url_id
            }

        # Download the content
        html_content, headers, error = self._download_url(url_record.url)

        if error:
            # Update URL status to failed
            self.db.update_url_status(url_id, UrlStatus.FAILED, error)
            return {
                "success": False,
                "error": error,
                "url_id": url_id,
                "url": url_record.url
            }

        if not html_content:
            error_msg = "No HTML content received"
            self.db.update_url_status(url_id, UrlStatus.FAILED, error_msg)
            return {
                "success": False,
                "error": error_msg,
                "url_id": url_id,
                "url": url_record.url
            }

        # Store the raw content
        import json
        headers_json = json.dumps(headers) if headers else None
        raw_content_id = self.db.add_raw_content(url_id, html_content, headers_json)

        # Update URL status to scraped
        self.db.update_url_status(url_id, UrlStatus.SCRAPED)

        return {
            "success": True,
            "url_id": url_id,
            "url": url_record.url,
            "raw_content_id": raw_content_id,
            "content_size": len(html_content),
            "headers": headers
        }


def get_scraper_service() -> ScraperService:
    """Get scraper service instance."""
    return ScraperService()