#!/usr/bin/env python3
"""
ExtractionService for intelligent content extraction with structure preservation.
Replaces basic CleanerService with LLM-optimized content processing.
Supports domain-specific extractors for higher quality results.
"""

import time
import threading
import re
from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime
import logging

from models.trusted_sources import JobType, JobStatus, UrlStatus
from services.database import get_trusted_sources_db
from services.extractors.domain_router import DomainRouter


logger = logging.getLogger(__name__)


class ExtractionService:
    """Service for extracting structured content from raw HTML with background job support."""

    def __init__(self):
        self.db = get_trusted_sources_db()
        self.domain_router = DomainRouter()
        logger.info(f"Initialized domain router with support for: {list(self.domain_router.get_supported_domains().keys())}")

    def start_extraction_job(self, domain: Optional[str] = None, url_id: Optional[int] = None, limit: Optional[int] = None) -> str:
        """
        Start a background extraction job for raw content.

        Args:
            domain: Domain to extract content for (batch mode)
            url_id: Single URL ID to extract content for (single mode)
            limit: Optional limit for test mode

        Returns:
            Job ID for tracking
        """
        # Generate job ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if url_id:
            job_id = f"extract_{url_id}_{timestamp}"
        else:
            job_id = f"extract_{domain}_{timestamp}"

        # Get raw content to extract
        if url_id:
            # Single URL mode
            raw_content_list = self._get_single_raw_content(url_id)
            domain = raw_content_list[0][2].domain if raw_content_list else "unknown"
        else:
            # Batch mode
            raw_content_list = self._get_raw_content_to_extract(domain, limit or 1000)

        if not raw_content_list:
            logger.warning(f"⚠️  No raw content found to extract for domain: {domain}")
            # Create a failed job
            self.db.create_job(job_id, domain, JobType.EXTRACT, 0, limit)
            self.db.complete_job(job_id, JobStatus.FAILED, "No raw content found to extract")
            return job_id

        # Apply test mode limit
        total_content = len(raw_content_list)
        if limit and limit < total_content:
            raw_content_list = raw_content_list[:limit]
            total_content = limit
            logger.info(f"🧪 TEST MODE: Limited to {limit} content items out of {len(raw_content_list)} available")

        # Create job in database
        self.db.create_job(job_id, domain, JobType.EXTRACT, total_content, limit)

        # Start background thread
        thread = threading.Thread(
            target=self._extract_content_background,
            args=(job_id, domain, raw_content_list),
            daemon=True
        )
        thread.start()

        logger.info(f"🔍 Started extraction job {job_id} for {domain} with {total_content} content items")

        return job_id

    def _get_single_raw_content(self, url_id: int) -> List:
        """Get single raw content for URL ID."""
        with self.db.get_session() as session:
            from models.trusted_sources import RawContent, ExtractedContent, UrlRecord, DomainRecord

            query = session.query(RawContent, UrlRecord, DomainRecord)\
                .join(UrlRecord, RawContent.url_id == UrlRecord.id)\
                .join(DomainRecord, UrlRecord.domain_id == DomainRecord.id)\
                .outerjoin(ExtractedContent, RawContent.id == ExtractedContent.raw_content_id)\
                .filter(UrlRecord.id == url_id)\
                .filter(ExtractedContent.id == None)

            return query.all()

    def _get_raw_content_to_extract(self, domain: str, limit: int) -> List:
        """Get raw content that needs extraction for a domain."""
        with self.db.get_session() as session:
            from models.trusted_sources import RawContent, ExtractedContent, UrlRecord, DomainRecord

            query = session.query(RawContent, UrlRecord)\
                .join(UrlRecord, RawContent.url_id == UrlRecord.id)\
                .join(DomainRecord, UrlRecord.domain_id == DomainRecord.id)\
                .outerjoin(ExtractedContent, RawContent.id == ExtractedContent.raw_content_id)\
                .filter(DomainRecord.domain == domain)\
                .filter(ExtractedContent.id == None)\
                .limit(limit)

            return query.all()

    def _extract_content_background(self, job_id: str, domain: str, raw_content_list: List) -> None:
        """Background worker for extracting content with structure preservation."""
        logger.info(f"🔍 Background extraction started: {job_id}")

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

                # Extract structured content from HTML
                extraction_result = self._extract_structured_content(raw_content.html, url_record.url)

                extract_time = time.time() - start_time

                if extraction_result["content"]:
                    # Store extracted content
                    extracted_content_id = self.db.add_extracted_content(
                        raw_content_id=raw_content.id,
                        title=extraction_result["title"],
                        content=extraction_result["content"],
                        has_tables=extraction_result["has_tables"],
                        has_lists=extraction_result["has_lists"],
                        has_headings=extraction_result["has_headings"],
                        has_links=extraction_result["has_links"],
                        structure_score=extraction_result["structure_score"]
                    )

                    # Update URL status to extracted
                    self.db.update_url_status(url_record.id, "extracted")

                    # Log success
                    content_length = len(extraction_result["content"])
                    logger.info(f"[SUCCESS] URL_EXTRACTED job_id={job_id} url={url_record.url} "
                               f"status=extracted content_length={content_length}chars "
                               f"structure_score={extraction_result['structure_score']:.2f} "
                               f"time={extract_time:.1f}s {progress_info}{test_mode_info}")

                else:
                    failed_count += 1

                    # Update URL status to failed
                    self.db.update_url_status(url_record.id, "failed")

                    # Log failure
                    logger.error(f"[ERROR] URL_FAILED job_id={job_id} url={url_record.url} "
                                f"status=failed error=\"{extraction_result['error']}\" "
                                f"time={extract_time:.1f}s {progress_info}{test_mode_info}")

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
                logger.error(f"❌ Error extracting content for URL {url_record.url}: {e}")
                failed_count += 1
                processed_count += 1

                # Update URL status to failed
                try:
                    self.db.update_url_status(url_record.id, "failed")
                except Exception:
                    pass

                # Update job progress
                self.db.update_job_progress(job_id, processed_count, failed_count)

        # Complete the job
        success_count = processed_count - failed_count
        success_rate = (success_count / total_content * 100) if total_content > 0 else 0

        if failed_count == total_content:
            # All failed
            self.db.complete_job(job_id, JobStatus.FAILED, f"All {total_content} content items failed")
            logger.error(f"[ERROR] JOB_FAILED job_id={job_id} domain={domain} reason=\"All content extraction failed\" "
                        f"progress={processed_count}/{total_content}(100%){test_mode_info}")
        else:
            # Completed successfully
            self.db.complete_job(job_id, JobStatus.COMPLETED)
            logger.info(f"[SUCCESS] JOB_COMPLETED job_id={job_id} domain={domain} total={total_content} "
                       f"extracted={success_count} failed={failed_count} success_rate={success_rate:.1f}%{test_mode_info}")

    def _extract_structured_content(self, html: str, url: str) -> Dict[str, Any]:
        """
        Extract structured content from HTML with quality metrics.

        Returns:
            Dict with keys: title, content, has_tables, has_lists, has_headings, has_links, structure_score, error
        """
        try:
            result = {
                "title": None,
                "content": None,
                "has_tables": False,
                "has_lists": False,
                "has_headings": False,
                "has_links": False,
                "structure_score": 0.0,
                "error": None
            }

            # Extract title
            result["title"] = self._extract_title(html)

            # Analyze structure before cleaning
            structure_analysis = self._analyze_html_structure(html)
            result.update(structure_analysis)

            # Remove unwanted elements but preserve structure
            cleaned_html = self._clean_html_preserve_structure(html)

            # Extract main content while preserving structure
            content = self._extract_main_content(cleaned_html)

            # Basic content validation
            if not content or len(content.strip()) < 100:
                result["error"] = "Content too short after extraction"
                return result

            # Check if content is mostly navigation/boilerplate
            if self._is_boilerplate(content):
                result["error"] = "Content appears to be boilerplate/navigation"
                return result

            result["content"] = content.strip()

            # Calculate overall structure score (0.0 to 1.0)
            score_components = []
            if result["has_tables"]: score_components.append(0.3)
            if result["has_lists"]: score_components.append(0.25)
            if result["has_headings"]: score_components.append(0.25)
            if result["has_links"]: score_components.append(0.2)

            # Base score for having content
            base_score = 0.3
            structure_bonus = sum(score_components)
            result["structure_score"] = min(1.0, base_score + structure_bonus)

            return result

        except Exception as e:
            return {
                "title": None,
                "content": None,
                "has_tables": False,
                "has_lists": False,
                "has_headings": False,
                "has_links": False,
                "structure_score": 0.0,
                "error": f"HTML extraction error: {str(e)}"
            }

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

    def _analyze_html_structure(self, html: str) -> Dict[str, bool]:
        """Analyze HTML structure to detect meaningful elements."""
        return {
            "has_tables": bool(re.search(r'<table[^>]*>.*?</table>', html, re.IGNORECASE | re.DOTALL)),
            "has_lists": bool(re.search(r'<(ul|ol)[^>]*>.*?</\1>', html, re.IGNORECASE | re.DOTALL)),
            "has_headings": bool(re.search(r'<h[1-6][^>]*>.*?</h[1-6]>', html, re.IGNORECASE | re.DOTALL)),
            "has_links": bool(re.search(r'<a[^>]*href[^>]*>.*?</a>', html, re.IGNORECASE | re.DOTALL))
        }

    def _clean_html_preserve_structure(self, html: str) -> str:
        """Clean HTML while preserving important structural elements."""
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

        return html

    def _extract_main_content(self, html: str) -> str:
        """Extract main content while preserving some structure markers."""
        # For now, use a simplified approach
        # TODO: Replace with BeautifulSoup4 for better parsing

        # Try to find main content areas
        main_patterns = [
            r'<main[^>]*>(.*?)</main>',
            r'<article[^>]*>(.*?)</article>',
            r'<div[^>]*class="[^"]*content[^"]*"[^>]*>(.*?)</div>',
            r'<div[^>]*id="[^"]*content[^"]*"[^>]*>(.*?)</div>'
        ]

        content = html
        for pattern in main_patterns:
            match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
            if match:
                content = match.group(1)
                break

        # Convert structural elements to markers for later markdown conversion
        # Tables: Keep table structure
        content = re.sub(r'<table[^>]*>', '\n[TABLE_START]\n', content, flags=re.IGNORECASE)
        content = re.sub(r'</table>', '\n[TABLE_END]\n', content, flags=re.IGNORECASE)
        content = re.sub(r'<tr[^>]*>', '[ROW]', content, flags=re.IGNORECASE)
        content = re.sub(r'</tr>', '[/ROW]\n', content, flags=re.IGNORECASE)
        content = re.sub(r'<t[hd][^>]*>', '[CELL]', content, flags=re.IGNORECASE)
        content = re.sub(r'</t[hd]>', '[/CELL]', content, flags=re.IGNORECASE)

        # Lists: Keep list structure
        content = re.sub(r'<ul[^>]*>', '\n[LIST_START]\n', content, flags=re.IGNORECASE)
        content = re.sub(r'</ul>', '\n[LIST_END]\n', content, flags=re.IGNORECASE)
        content = re.sub(r'<ol[^>]*>', '\n[ORDERED_LIST_START]\n', content, flags=re.IGNORECASE)
        content = re.sub(r'</ol>', '\n[ORDERED_LIST_END]\n', content, flags=re.IGNORECASE)
        content = re.sub(r'<li[^>]*>', '[ITEM]', content, flags=re.IGNORECASE)
        content = re.sub(r'</li>', '[/ITEM]\n', content, flags=re.IGNORECASE)

        # Headings: Keep heading levels
        for i in range(1, 7):
            content = re.sub(f'<h{i}[^>]*>', f'[H{i}]', content, flags=re.IGNORECASE)
            content = re.sub(f'</h{i}>', f'[/H{i}]\n\n', content, flags=re.IGNORECASE)

        # Links: Preserve links with href
        content = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r'[LINK href="\1"]\2[/LINK]', content, flags=re.IGNORECASE)

        # Paragraphs: Add paragraph breaks
        content = re.sub(r'<p[^>]*>', '\n\n[P]', content, flags=re.IGNORECASE)
        content = re.sub(r'</p>', '[/P]\n\n', content, flags=re.IGNORECASE)

        # Remove remaining HTML tags
        content = re.sub(r'<[^>]+>', ' ', content)

        # Decode HTML entities
        content = self._decode_html_entities(content)

        # Clean up whitespace but preserve structure markers
        content = re.sub(r'[ \t]+', ' ', content)  # Multiple spaces/tabs to single space
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)  # Multiple newlines to double newline

        return content

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

    def extract_url_direct(self, url_id: int) -> dict:
        """
        Directly extract content from a single URL and store the result.
        Uses domain-specific extractors when available, falls back to generic extraction.

        Args:
            url_id: The URL ID to extract content from

        Returns:
            Dictionary with extraction result
        """
        # Get raw content for this URL
        raw_content = self.db.get_raw_content_by_url_id(url_id)
        if not raw_content:
            return {
                "success": False,
                "error": f"No raw content found for URL ID {url_id}",
                "url_id": url_id
            }

        # Try domain-specific extraction first
        domain_extractor = self.domain_router.get_extractor(raw_content.url)
        extraction_method = "domain_specific" if domain_extractor else "generic"

        try:
            if domain_extractor:
                logger.info(f"Using domain-specific extractor for {raw_content.url}")
                extraction_result = domain_extractor.extract_content(raw_content.html, raw_content.url)

                # Convert domain-specific result to expected format
                result_dict = {
                    "title": extraction_result.title,
                    "content": extraction_result.content,
                    "has_tables": extraction_result.has_tables,
                    "has_lists": extraction_result.has_lists,
                    "has_headings": extraction_result.has_headings,
                    "has_links": extraction_result.has_links,
                    "structure_score": extraction_result.structure_score,
                    "error": None
                }

                # Add domain-specific metadata
                if extraction_result.author:
                    result_dict["author"] = extraction_result.author
                if extraction_result.date_published:
                    result_dict["date_published"] = extraction_result.date_published

            else:
                logger.info(f"Using generic extractor for {raw_content.url}")
                result_dict = self._extract_structured_content(raw_content.html, raw_content.url)

        except Exception as e:
            logger.error(f"Domain-specific extraction failed for {raw_content.url}: {e}")
            logger.info("Falling back to generic extraction")
            result_dict = self._extract_structured_content(raw_content.html, raw_content.url)
            extraction_method = "generic_fallback"

        if result_dict.get("error"):
            # Update URL status to failed
            self.db.update_url_status(url_id, UrlStatus.FAILED, result_dict["error"])
            return {
                "success": False,
                "error": result_dict["error"],
                "url_id": url_id,
                "raw_content_id": raw_content.id,
                "extraction_method": extraction_method
            }

        # Check for quality
        if not result_dict.get("content"):
            error_msg = "No meaningful content extracted"
            self.db.update_url_status(url_id, UrlStatus.FAILED, error_msg)
            return {
                "success": False,
                "error": error_msg,
                "url_id": url_id,
                "raw_content_id": raw_content.id,
                "extraction_method": extraction_method
            }

        # Store extracted content
        extracted_id = self.db.add_extracted_content(
            raw_content_id=raw_content.id,
            title=result_dict.get("title"),
            content=result_dict["content"],
            has_tables=result_dict["has_tables"],
            has_lists=result_dict["has_lists"],
            has_headings=result_dict["has_headings"],
            has_links=result_dict["has_links"],
            structure_score=result_dict["structure_score"]
        )

        metadata = {
            "has_tables": result_dict["has_tables"],
            "has_lists": result_dict["has_lists"],
            "has_headings": result_dict["has_headings"],
            "has_links": result_dict["has_links"],
            "structure_score": result_dict["structure_score"],
            "extraction_method": extraction_method
        }

        # Add domain-specific metadata if available
        if domain_extractor and hasattr(domain_extractor, 'get_domain_patterns'):
            patterns = domain_extractor.get_domain_patterns()
            if patterns and result_dict.get("content"):
                metadata["domain_patterns"] = patterns.get("content_type_indicators", {})

        # Update URL status to extracted
        self.db.update_url_status(url_id, UrlStatus.EXTRACTED)

        return {
            "success": True,
            "url_id": url_id,
            "raw_content_id": raw_content.id,
            "extracted_content_id": extracted_id,
            "title": result_dict.get("title"),
            "content": result_dict["content"],
            "content_length": len(result_dict["content"]),
            "structure_score": result_dict["structure_score"],
            "metadata": metadata,
            "extraction_method": extraction_method
        }


def get_extraction_service() -> ExtractionService:
    """Get extraction service instance."""
    return ExtractionService()