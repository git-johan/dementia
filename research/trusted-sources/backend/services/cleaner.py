#!/usr/bin/env python3
"""
Cleaner service for processing HTML content into clean text with background jobs and test mode.
"""

import time
import threading
from typing import Optional, List
from datetime import datetime
import logging
import re

from models.trusted_sources import JobType, JobStatus
from services.database import get_trusted_sources_db


logger = logging.getLogger(__name__)


class CleanerService:
    """Service for cleaning HTML content with background job support."""

    def __init__(self):
        self.db = get_trusted_sources_db()

    def start_cleaning_job(self, domain: str, limit: Optional[int] = None) -> str:
        """
        Start a background cleaning job for raw content.

        Args:
            domain: Domain to clean content for
            limit: Optional limit for test mode

        Returns:
            Job ID for tracking
        """
        # Generate job ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        job_id = f"clean_{domain}_{timestamp}"

        # Get raw content to clean
        raw_content_list = self._get_raw_content_to_clean(domain, limit or 1000)

        if not raw_content_list:
            logger.warning(f"⚠️  No raw content found to clean for domain: {domain}")
            # Create a failed job
            self.db.create_job(job_id, domain, JobType.CLEAN, 0, limit)
            self.db.complete_job(job_id, JobStatus.FAILED, "No raw content found to clean")
            return job_id

        # Apply test mode limit
        total_content = len(raw_content_list)
        if limit and limit < total_content:
            raw_content_list = raw_content_list[:limit]
            total_content = limit
            logger.info(f"🧪 TEST MODE: Limited to {limit} content items out of {len(raw_content_list)} available")

        # Create job in database
        self.db.create_job(job_id, domain, JobType.CLEAN, total_content, limit)

        # Start background thread
        thread = threading.Thread(
            target=self._clean_content_background,
            args=(job_id, domain, raw_content_list),
            daemon=True
        )
        thread.start()

        logger.info(f"🧼 Started cleaning job {job_id} for {domain} with {total_content} content items")

        return job_id

    def _get_raw_content_to_clean(self, domain: str, limit: int) -> List:
        """Get raw content that needs cleaning."""
        with self.db.get_session() as session:
            # Get raw content that doesn't have corresponding clean content
            from models.trusted_sources import RawContent, CleanContent, UrlRecord, DomainRecord

            query = session.query(RawContent, UrlRecord)\
                .join(UrlRecord, RawContent.url_id == UrlRecord.id)\
                .join(DomainRecord, UrlRecord.domain_id == DomainRecord.id)\
                .outerjoin(CleanContent, RawContent.id == CleanContent.raw_content_id)\
                .filter(DomainRecord.domain == domain)\
                .filter(CleanContent.id == None)\
                .limit(limit)

            return query.all()

    def _clean_content_background(self, job_id: str, domain: str, raw_content_list: List) -> None:
        """Background worker for cleaning content."""
        logger.info(f"🧽 Background cleaning started: {job_id}")

        total_content = len(raw_content_list)
        processed_count = 0
        failed_count = 0

        # Get job info for test mode detection
        job = self.db.get_job(job_id)
        test_mode = job and job.limit is not None

        for raw_content, url_record in raw_content_list:
            try:
                # Log progress with URL-level detail
                progress_info = f"progress={processed_count + 1}/{total_content} remaining={total_content - processed_count - 1}"
                test_mode_info = " (TEST_MODE)" if test_mode else ""

                start_time = time.time()

                # Clean the HTML content
                title, clean_text, error = self._clean_html(raw_content.html, url_record.url)

                clean_time = time.time() - start_time

                if clean_text:
                    # Store clean content
                    clean_content_id = self.db.add_clean_content(
                        raw_content_id=raw_content.id,
                        title=title,
                        text=clean_text
                    )

                    # Log success
                    text_length = len(clean_text)
                    logger.info(f"[SUCCESS] URL_CLEANED job_id={job_id} url={url_record.url} "
                               f"status=cleaned text_length={text_length}chars time={clean_time:.1f}s {progress_info}{test_mode_info}")

                else:
                    failed_count += 1

                    # Log failure
                    logger.error(f"[ERROR] URL_FAILED job_id={job_id} url={url_record.url} "
                                f"status=failed error=\"{error}\" time={clean_time:.1f}s {progress_info}{test_mode_info}")

                processed_count += 1

                # Update job progress
                self.db.update_job_progress(job_id, processed_count, failed_count)

                # Log batch progress every 5 items
                if processed_count % 5 == 0:
                    success_count = processed_count - failed_count
                    logger.info(f"[INFO] JOB_PROGRESS job_id={job_id} completed={processed_count}/{total_content}({processed_count/total_content*100:.1f}%) "
                               f"remaining={total_content-processed_count} success={success_count} failed={failed_count}{test_mode_info}")

                # Small delay between processing
                time.sleep(0.1)

            except Exception as e:
                logger.error(f"❌ Error cleaning content for URL {url_record.url}: {e}")
                failed_count += 1
                processed_count += 1

                # Update job progress
                self.db.update_job_progress(job_id, processed_count, failed_count)

        # Complete the job
        success_count = processed_count - failed_count
        success_rate = (success_count / total_content * 100) if total_content > 0 else 0

        if failed_count == total_content:
            # All failed
            self.db.complete_job(job_id, JobStatus.FAILED, f"All {total_content} content items failed")
            logger.error(f"[ERROR] JOB_FAILED job_id={job_id} domain={domain} reason=\"All content cleaning failed\" "
                        f"progress={processed_count}/{total_content}(100%){test_mode_info}")
        else:
            # Completed successfully
            self.db.complete_job(job_id, JobStatus.COMPLETED)
            logger.info(f"[SUCCESS] JOB_COMPLETED job_id={job_id} domain={domain} total={total_content} "
                       f"cleaned={success_count} failed={failed_count} success_rate={success_rate:.1f}%{test_mode_info}")

    def _clean_html(self, html: str, url: str) -> tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Clean HTML content to extract title and main text.

        Returns:
            Tuple of (title, clean_text, error_message)
        """
        try:
            # Basic HTML cleaning without external dependencies

            # Extract title
            title = self._extract_title(html)

            # Remove script and style elements
            html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
            html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)

            # Remove HTML comments
            html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)

            # Remove common navigation and footer elements
            html = re.sub(r'<nav[^>]*>.*?</nav>', '', html, flags=re.DOTALL | re.IGNORECASE)
            html = re.sub(r'<footer[^>]*>.*?</footer>', '', html, flags=re.DOTALL | re.IGNORECASE)
            html = re.sub(r'<header[^>]*>.*?</header>', '', html, flags=re.DOTALL | re.IGNORECASE)

            # Remove form elements
            html = re.sub(r'<form[^>]*>.*?</form>', '', html, flags=re.DOTALL | re.IGNORECASE)

            # Remove all remaining HTML tags
            text = re.sub(r'<[^>]+>', ' ', html)

            # Decode HTML entities
            text = self._decode_html_entities(text)

            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()

            # Basic content validation
            if len(text) < 100:
                return None, None, "Content too short after cleaning"

            # Check if content is mostly navigation/boilerplate
            if self._is_boilerplate(text):
                return None, None, "Content appears to be boilerplate/navigation"

            return title, text, None

        except Exception as e:
            return None, None, f"HTML cleaning error: {str(e)}"

    def _extract_title(self, html: str) -> Optional[str]:
        """Extract title from HTML."""
        try:
            title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
            if title_match:
                title = title_match.group(1)
                title = re.sub(r'<[^>]+>', '', title)  # Remove any tags within title
                title = self._decode_html_entities(title)
                title = re.sub(r'\s+', ' ', title).strip()
                return title if title else None
        except Exception:
            pass
        return None

    def _decode_html_entities(self, text: str) -> str:
        """Decode common HTML entities."""
        entities = {
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&apos;': "'",
            '&nbsp;': ' ',
            '&copy;': '©',
            '&reg;': '®',
            '&trade;': '™',
            '&ndash;': '–',
            '&mdash;': '—',
            '&hellip;': '…',
            '&laquo;': '«',
            '&raquo;': '»'
        }

        for entity, replacement in entities.items():
            text = text.replace(entity, replacement)

        # Handle numeric entities
        text = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), text)
        text = re.sub(r'&#x([0-9a-fA-F]+);', lambda m: chr(int(m.group(1), 16)), text)

        return text

    def _is_boilerplate(self, text: str) -> bool:
        """Check if content is likely boilerplate/navigation."""
        # Convert to lowercase for checking
        lower_text = text.lower()

        # Common boilerplate indicators
        boilerplate_indicators = [
            'cookie', 'privacy policy', 'terms of service',
            'navigation menu', 'breadcrumb', 'footer',
            'skip to main content', 'accessibility',
            'search', 'login', 'register', 'subscribe'
        ]

        # Count boilerplate indicators
        indicator_count = sum(1 for indicator in boilerplate_indicators if indicator in lower_text)

        # If more than 30% of content matches boilerplate indicators, consider it boilerplate
        word_count = len(text.split())
        if word_count > 0 and (indicator_count / word_count) > 0.3:
            return True

        # Very short content is likely boilerplate
        if word_count < 50:
            return True

        return False


def get_cleaner_service() -> CleanerService:
    """Get cleaner service instance."""
    return CleanerService()