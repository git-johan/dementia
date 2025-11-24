#!/usr/bin/env python3
"""
MarkdownConverterService for converting extracted content to LLM-optimized markdown.
Focuses on preserving structure and creating content suitable for vector databases.
"""

import time
import threading
import re
import json
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
import logging

from models.trusted_sources import JobType, JobStatus
from services.database import get_trusted_sources_db


logger = logging.getLogger(__name__)


class MarkdownConverterService:
    """Service for converting extracted content to LLM-ready markdown with background job support."""

    def __init__(self):
        self.db = get_trusted_sources_db()

    def start_conversion_job(self, domain: Optional[str] = None, url_id: Optional[int] = None, limit: Optional[int] = None) -> str:
        """
        Start a background conversion job for extracted content.

        Args:
            domain: Domain to convert content for (batch mode)
            url_id: Single URL ID to convert content for (single mode)
            limit: Optional limit for test mode

        Returns:
            Job ID for tracking
        """
        # Generate job ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if url_id:
            job_id = f"convert_{url_id}_{timestamp}"
        else:
            job_id = f"convert_{domain}_{timestamp}"

        # Get extracted content to convert
        if url_id:
            # Single URL mode
            extracted_content_list = self._get_single_extracted_content(url_id)
            domain = self._get_domain_for_url_id(url_id) if extracted_content_list else "unknown"
        else:
            # Batch mode
            extracted_content_list = self._get_extracted_content_to_convert(domain, limit or 1000)

        if not extracted_content_list:
            logger.warning(f"⚠️  No extracted content found to convert for domain: {domain}")
            # Create a failed job
            self.db.create_job(job_id, domain, JobType.CONVERT, 0, limit)
            self.db.complete_job(job_id, JobStatus.FAILED, "No extracted content found to convert")
            return job_id

        # Apply test mode limit
        total_content = len(extracted_content_list)
        if limit and limit < total_content:
            extracted_content_list = extracted_content_list[:limit]
            total_content = limit
            logger.info(f"🧪 TEST MODE: Limited to {limit} content items out of {len(extracted_content_list)} available")

        # Create job in database
        self.db.create_job(job_id, domain, JobType.CONVERT, total_content, limit)

        # Start background thread
        thread = threading.Thread(
            target=self._convert_content_background,
            args=(job_id, domain, extracted_content_list),
            daemon=True
        )
        thread.start()

        logger.info(f"📝 Started conversion job {job_id} for {domain} with {total_content} content items")

        return job_id

    def _get_single_extracted_content(self, url_id: int) -> List:
        """Get single extracted content for URL ID."""
        with self.db.get_session() as session:
            from models.trusted_sources import ExtractedContent, MarkdownContent, UrlRecord, RawContent

            query = session.query(ExtractedContent, UrlRecord)\
                .join(RawContent, ExtractedContent.raw_content_id == RawContent.id)\
                .join(UrlRecord, RawContent.url_id == UrlRecord.id)\
                .outerjoin(MarkdownContent, ExtractedContent.id == MarkdownContent.extracted_content_id)\
                .filter(UrlRecord.id == url_id)\
                .filter(MarkdownContent.id == None)

            return query.all()

    def _get_domain_for_url_id(self, url_id: int) -> str:
        """Get domain name for URL ID."""
        with self.db.get_session() as session:
            from models.trusted_sources import UrlRecord, DomainRecord

            result = session.query(DomainRecord.domain)\
                .join(UrlRecord, DomainRecord.id == UrlRecord.domain_id)\
                .filter(UrlRecord.id == url_id)\
                .first()

            return result.domain if result else "unknown"

    def _get_extracted_content_to_convert(self, domain: str, limit: int) -> List:
        """Get extracted content that needs conversion for a domain."""
        with self.db.get_session() as session:
            from models.trusted_sources import ExtractedContent, MarkdownContent, UrlRecord, RawContent, DomainRecord

            query = session.query(ExtractedContent, UrlRecord)\
                .join(RawContent, ExtractedContent.raw_content_id == RawContent.id)\
                .join(UrlRecord, RawContent.url_id == UrlRecord.id)\
                .join(DomainRecord, UrlRecord.domain_id == DomainRecord.id)\
                .outerjoin(MarkdownContent, ExtractedContent.id == MarkdownContent.extracted_content_id)\
                .filter(DomainRecord.domain == domain)\
                .filter(MarkdownContent.id == None)\
                .limit(limit)

            return query.all()

    def _convert_content_background(self, job_id: str, domain: str, extracted_content_list: List) -> None:
        """Background worker for converting content to markdown."""
        logger.info(f"📝 Background conversion started: {job_id}")

        total_content = len(extracted_content_list)
        processed_count = 0
        failed_count = 0

        # Get job info for test mode detection
        job = self.db.get_job(job_id)
        test_mode = job and job.limit is not None

        for extracted_content, url_record in extracted_content_list:
            try:
                # Log progress with URL-level detail
                progress_info = f"progress={processed_count + 1}/{total_content} remaining={total_content - processed_count - 1}"
                test_mode_info = " (TEST_MODE)" if test_mode else ""

                start_time = time.time()

                # Convert extracted content to markdown
                conversion_result = self._convert_to_markdown(
                    extracted_content.content,
                    extracted_content.title,
                    url_record.url
                )

                convert_time = time.time() - start_time

                if conversion_result["markdown"]:
                    # Store markdown content
                    markdown_content_id = self.db.add_markdown_content(
                        extracted_content_id=extracted_content.id,
                        title=conversion_result["title"],
                        markdown=conversion_result["markdown"],
                        chunk_count=conversion_result["chunk_count"],
                        has_metadata=conversion_result["has_metadata"],
                        content_metadata=json.dumps(conversion_result["metadata"]) if conversion_result["metadata"] else None
                    )

                    # Update URL status to converted
                    self.db.update_url_status(url_record.id, "converted")

                    # Log success
                    markdown_length = len(conversion_result["markdown"])
                    logger.info(f"[SUCCESS] URL_CONVERTED job_id={job_id} url={url_record.url} "
                               f"status=converted markdown_length={markdown_length}chars "
                               f"chunks={conversion_result['chunk_count']} "
                               f"metadata={conversion_result['has_metadata']} "
                               f"time={convert_time:.1f}s {progress_info}{test_mode_info}")

                else:
                    failed_count += 1

                    # Log failure
                    logger.error(f"[ERROR] URL_FAILED job_id={job_id} url={url_record.url} "
                                f"status=failed error=\"{conversion_result['error']}\" "
                                f"time={convert_time:.1f}s {progress_info}{test_mode_info}")

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
                logger.error(f"❌ Error converting content for URL {url_record.url}: {e}")
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
            logger.error(f"[ERROR] JOB_FAILED job_id={job_id} domain={domain} reason=\"All content conversion failed\" "
                        f"progress={processed_count}/{total_content}(100%){test_mode_info}")
        else:
            # Completed successfully
            self.db.complete_job(job_id, JobStatus.COMPLETED)
            logger.info(f"[SUCCESS] JOB_COMPLETED job_id={job_id} domain={domain} total={total_content} "
                       f"converted={success_count} failed={failed_count} success_rate={success_rate:.1f}%{test_mode_info}")

    def _convert_to_markdown(self, content: str, title: Optional[str], url: str) -> Dict[str, Any]:
        """
        Convert extracted content with structure markers to LLM-optimized markdown.

        Returns:
            Dict with keys: title, markdown, chunk_count, has_metadata, metadata, error
        """
        try:
            result = {
                "title": title,
                "markdown": None,
                "chunk_count": 0,
                "has_metadata": False,
                "metadata": None,
                "error": None
            }

            if not content or len(content.strip()) < 50:
                result["error"] = "Content too short for conversion"
                return result

            # Extract metadata from content
            metadata = self._extract_metadata(content, url)
            if metadata:
                result["has_metadata"] = True
                result["metadata"] = metadata

            # Convert structure markers to markdown
            markdown_content = self._process_structure_markers(content)

            # Clean up markdown formatting
            markdown_content = self._clean_markdown(markdown_content)

            # Create semantic chunks for LLM consumption
            chunks = self._create_semantic_chunks(markdown_content)
            result["chunk_count"] = len(chunks)

            # Reassemble content with chunk boundaries marked
            final_markdown = self._assemble_chunked_markdown(chunks, title, metadata)

            result["markdown"] = final_markdown.strip()

            return result

        except Exception as e:
            return {
                "title": title,
                "markdown": None,
                "chunk_count": 0,
                "has_metadata": False,
                "metadata": None,
                "error": f"Markdown conversion error: {str(e)}"
            }

    def _extract_metadata(self, content: str, url: str) -> Optional[Dict[str, Any]]:
        """Extract metadata from content (authors, dates, etc.)."""
        metadata = {"url": url}

        # Look for date patterns
        date_patterns = [
            r'(\d{1,2}[./]\d{1,2}[./]\d{4})',  # MM/DD/YYYY or MM.DD.YYYY
            r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',  # YYYY-MM-DD or YYYY/MM/DD
            r'(\w+\s+\d{1,2},?\s+\d{4})',      # Month DD, YYYY
        ]

        for pattern in date_patterns:
            match = re.search(pattern, content)
            if match:
                metadata["date"] = match.group(1)
                break

        # Look for author patterns
        author_patterns = [
            r'(?:av|by|author|forfatter|skrevet av)\s*:?\s*([A-ZÆØÅ][a-zæøå]+(?:\s+[A-ZÆØÅ][a-zæøå]+)*)',
            r'([A-ZÆØÅ][a-zæøå]+\s+[A-ZÆØÅ][a-zæøå]+)(?:\s*,\s*forfatter|\s*,\s*author)',
        ]

        for pattern in author_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                author = match.group(1).strip()
                if len(author) > 3 and len(author) < 50:  # Reasonable author name length
                    metadata["author"] = author
                    break

        # Return metadata only if we found something useful
        return metadata if len(metadata) > 1 else None

    def _process_structure_markers(self, content: str) -> str:
        """Convert structure markers to proper markdown."""
        # Convert tables
        content = re.sub(r'\[TABLE_START\]\s*', '\n\n', content)
        content = re.sub(r'\[TABLE_END\]\s*', '\n\n', content)
        content = re.sub(r'\[ROW\]', '|', content)
        content = re.sub(r'\[/ROW\]', '|\n', content)
        content = re.sub(r'\[CELL\]', '', content)
        content = re.sub(r'\[/CELL\]', ' |', content)

        # Convert lists
        content = re.sub(r'\[LIST_START\]\s*', '\n\n', content)
        content = re.sub(r'\[LIST_END\]\s*', '\n\n', content)
        content = re.sub(r'\[ORDERED_LIST_START\]\s*', '\n\n', content)
        content = re.sub(r'\[ORDERED_LIST_END\]\s*', '\n\n', content)

        # Convert list items (detect if ordered or unordered by context)
        lines = content.split('\n')
        in_ordered_list = False
        ordered_counter = 1

        for i, line in enumerate(lines):
            if '[ITEM]' in line:
                # Check if we're in an ordered list context
                if i > 0 and ('ORDERED_LIST' in lines[i-1] or in_ordered_list):
                    lines[i] = re.sub(r'\[ITEM\](.*?)\[/ITEM\]', f'{ordered_counter}. \\1', line)
                    ordered_counter += 1
                    in_ordered_list = True
                else:
                    lines[i] = re.sub(r'\[ITEM\](.*?)\[/ITEM\]', '- \\1', line)
                    in_ordered_list = False
                    ordered_counter = 1
            elif '[LIST_END]' in line or '[ORDERED_LIST_END]' in line:
                in_ordered_list = False
                ordered_counter = 1

        content = '\n'.join(lines)

        # Convert headings
        for level in range(1, 7):
            content = re.sub(f'\\[H{level}\\](.*?)\\[/H{level}\\]', f'{"#" * level} \\1', content)

        # Convert links
        content = re.sub(r'\[LINK href="([^"]*)"](.*?)\[/LINK\]', r'[\2](\1)', content)

        # Convert paragraphs
        content = re.sub(r'\[P\](.*?)\[/P\]', '\\1\n\n', content)

        return content

    def _clean_markdown(self, content: str) -> str:
        """Clean up markdown formatting."""
        # Fix multiple newlines
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)

        # Fix heading spacing
        content = re.sub(r'(#{1,6}\s+[^\n]+)\n{1,2}([^\n#])', r'\1\n\n\2', content)

        # Fix list spacing
        content = re.sub(r'(\n[-*]\s+[^\n]+)\n([^\n-*])', r'\1\n\n\2', content)
        content = re.sub(r'(\n\d+\.\s+[^\n]+)\n([^\n\d])', r'\1\n\n\2', content)

        # Clean up table formatting
        lines = content.split('\n')
        in_table = False
        table_lines = []

        for line in lines:
            if line.strip().startswith('|') and line.strip().endswith('|'):
                if not in_table:
                    # First table row, add header separator
                    in_table = True
                    table_lines.append(line)
                    # Add separator row (assume all columns are text)
                    separator = re.sub(r'\|[^|]*', '|---', line)
                    table_lines.append(separator)
                else:
                    table_lines.append(line)
            else:
                if in_table:
                    in_table = False
                    table_lines.append('')  # Add spacing after table
                table_lines.append(line)

        content = '\n'.join(table_lines)

        # Final cleanup
        content = content.strip()

        return content

    def _create_semantic_chunks(self, content: str) -> List[str]:
        """Create semantic chunks for LLM consumption."""
        # Simple chunking strategy - can be enhanced with more sophisticated methods

        # Split by major sections (double newlines)
        sections = re.split(r'\n\n+', content)

        chunks = []
        current_chunk = []
        current_length = 0
        max_chunk_length = 2000  # Target chunk size for LLMs

        for section in sections:
            section = section.strip()
            if not section:
                continue

            section_length = len(section)

            # If adding this section would exceed max length, finalize current chunk
            if current_length + section_length > max_chunk_length and current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = []
                current_length = 0

            # If section itself is too long, split it further
            if section_length > max_chunk_length:
                # Split long sections by sentences
                sentences = re.split(r'(?<=[.!?])\s+', section)
                for sentence in sentences:
                    sentence = sentence.strip()
                    if not sentence:
                        continue

                    if current_length + len(sentence) > max_chunk_length and current_chunk:
                        chunks.append('\n\n'.join(current_chunk))
                        current_chunk = []
                        current_length = 0

                    current_chunk.append(sentence)
                    current_length += len(sentence)
            else:
                current_chunk.append(section)
                current_length += section_length

        # Add final chunk
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))

        return chunks

    def _assemble_chunked_markdown(self, chunks: List[str], title: Optional[str], metadata: Optional[Dict[str, Any]]) -> str:
        """Assemble final markdown with metadata and chunk boundaries."""
        parts = []

        # Add title if available
        if title:
            parts.append(f"# {title}\n")

        # Add metadata if available
        if metadata:
            parts.append("---")
            if "author" in metadata:
                parts.append(f"Author: {metadata['author']}")
            if "date" in metadata:
                parts.append(f"Date: {metadata['date']}")
            if "url" in metadata:
                parts.append(f"Source: {metadata['url']}")
            parts.append("---\n")

        # Add chunks with boundaries for LLM processing
        for i, chunk in enumerate(chunks):
            if i > 0:
                parts.append(f"\n<!-- Chunk {i+1} -->\n")
            parts.append(chunk)

        return '\n'.join(parts)

    def convert_url_direct(self, url_id: int) -> dict:
        """
        Directly convert extracted content to markdown for a single URL and store the result.

        Args:
            url_id: The URL ID to convert content for

        Returns:
            Dictionary with conversion result
        """
        # Get extracted content for this URL
        extracted_content = self.db.get_extracted_content_by_url_id(url_id)
        if not extracted_content:
            return {
                "success": False,
                "error": f"No extracted content found for URL ID {url_id}",
                "url_id": url_id
            }

        # Get URL record for context
        url_record = self.db.get_url_by_id(url_id)
        if not url_record:
            return {
                "success": False,
                "error": f"URL record not found for URL ID {url_id}",
                "url_id": url_id
            }

        # Convert to markdown
        conversion_result = self._convert_to_markdown(
            content=extracted_content.content,
            title=extracted_content.title,
            url=url_record.url
        )

        if conversion_result.get("error"):
            # Update URL status to failed
            from models.trusted_sources import UrlStatus
            self.db.update_url_status(url_id, UrlStatus.FAILED, conversion_result["error"])
            return {
                "success": False,
                "error": conversion_result["error"],
                "url_id": url_id,
                "extracted_content_id": extracted_content.id
            }

        # Store markdown content
        import json
        metadata_json = json.dumps(conversion_result["metadata"]) if conversion_result["metadata"] else None

        markdown_content_id = self.db.add_markdown_content(
            extracted_content_id=extracted_content.id,
            title=conversion_result["title"],
            markdown=conversion_result["markdown"],
            chunk_count=conversion_result["chunk_count"],
            content_metadata=metadata_json
        )

        # Update URL status to converted
        from models.trusted_sources import UrlStatus
        self.db.update_url_status(url_id, UrlStatus.CONVERTED)

        return {
            "success": True,
            "url_id": url_id,
            "extracted_content_id": extracted_content.id,
            "markdown_content_id": markdown_content_id,
            "title": conversion_result["title"],
            "markdown_length": len(conversion_result["markdown"]),
            "chunk_count": conversion_result["chunk_count"],
            "metadata": conversion_result["metadata"]
        }


def get_markdown_converter_service() -> MarkdownConverterService:
    """Get markdown converter service instance."""
    return MarkdownConverterService()