#!/usr/bin/env python3
"""
Database service for trusted sources with job tracking and content storage.
"""

import os
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, text, and_, or_
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import re
from models.trusted_sources import (
    Base, DomainRecord, UrlRecord, ScrapeJob, RawContent, CleanContent,
    ExtractedContent, MarkdownContent,
    UrlStatus, JobStatus, JobType, DomainStatus,
    UrlCreate, UrlResponse, JobResponse, ContentResponse, DomainStats,
    DomainCreate, DomainUpdate, DomainResponse,
    RawContentResponse, RawContentListItem, RawContentHeadersResponse,
    ContentComparisonResponse, RawContentStatsResponse,
    CleanedContentResponse, CleanedContentListItem, CleanedContentStatsResponse,
    CleanedContentSearchResponse
)


class TrustedSourcesDatabase:
    """Database service for trusted sources with job tracking and content storage."""

    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._is_initialized = False

    @staticmethod
    def normalize_domain(domain: str) -> str:
        """Normalize domain by removing protocol and www prefix."""
        if not domain:
            return domain

        # Remove protocol (http://, https://)
        domain = re.sub(r'^https?://', '', domain)

        # Remove www prefix
        domain = re.sub(r'^www\.', '', domain)

        # Remove trailing slash
        domain = domain.rstrip('/')

        return domain.lower().strip()

    def initialize(self):
        """Initialize database connection."""
        if self._is_initialized:
            return

        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            database_url = "postgresql://johanjosok@localhost:5432/trusted_sources"
            print("⚠️  No DATABASE_URL found, using default local database")

        try:
            self.engine = create_engine(database_url)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                print("✅ Database connection successful")

            self._is_initialized = True

        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            raise

    def create_tables(self):
        """Create all database tables."""
        if not self._is_initialized:
            self.initialize()

        try:
            Base.metadata.create_all(bind=self.engine)
            print("✅ Database tables created successfully")
        except Exception as e:
            print(f"❌ Failed to create tables: {e}")
            raise

    def get_session(self) -> Session:
        """Get a database session."""
        if not self._is_initialized:
            self.initialize()
        return self.SessionLocal()

    # URL Management
    def add_url(self, url_data: UrlCreate) -> UrlResponse:
        """Add a single URL to the database."""
        with self.get_session() as session:
            try:
                # Get or create domain
                domain_response = self.get_or_create_domain(url_data.domain)

                # Create URL record with domain_id
                url_dict = url_data.model_dump()
                url_dict['domain_id'] = domain_response.id
                del url_dict['domain']  # Remove domain string field

                db_url = UrlRecord(**url_dict)
                session.add(db_url)
                session.commit()
                session.refresh(db_url)

                return self._url_to_response(db_url)
            except Exception as e:
                session.rollback()
                raise e

    def add_urls_batch(self, urls_data: List[UrlCreate]) -> int:
        """Add multiple URLs to the database in a batch, skipping duplicates."""
        with self.get_session() as session:
            try:
                db_urls = []
                # Group URLs by domain for efficiency
                domain_cache = {}

                # Get existing URLs to check for duplicates
                existing_urls = set()
                if urls_data:
                    url_strings = [url_data.url for url_data in urls_data]
                    existing_records = session.query(UrlRecord.url).filter(UrlRecord.url.in_(url_strings)).all()
                    existing_urls = {record.url for record in existing_records}

                for url_data in urls_data:
                    # Skip if URL already exists
                    if url_data.url in existing_urls:
                        continue

                    # Get or cache domain
                    domain_name = url_data.domain
                    if domain_name not in domain_cache:
                        domain_response = self.get_or_create_domain(domain_name)
                        domain_cache[domain_name] = domain_response.id

                    # Create URL record with domain_id
                    url_dict = url_data.model_dump()
                    url_dict['domain_id'] = domain_cache[domain_name]
                    del url_dict['domain']  # Remove domain string field

                    db_urls.append(UrlRecord(**url_dict))

                if db_urls:
                    session.add_all(db_urls)
                    session.commit()

                return len(db_urls)
            except Exception as e:
                session.rollback()
                raise e

    def get_urls(self, domain: Optional[str] = None, status: Optional[UrlStatus] = None,
                 limit: int = 100, offset: int = 0) -> List[UrlResponse]:
        """Get URLs from database with optional filtering."""
        with self.get_session() as session:
            query = session.query(UrlRecord).join(DomainRecord)

            if domain:
                query = query.filter(DomainRecord.domain == domain)
            if status:
                query = query.filter(UrlRecord.status == status)

            urls = query.offset(offset).limit(limit).all()
            return [self._url_to_response(url) for url in urls]

    def get_url_by_url(self, url: str) -> Optional[UrlResponse]:
        """Get a specific URL record by exact URL match."""
        with self.get_session() as session:
            url_record = session.query(UrlRecord).filter(UrlRecord.url == url).first()
            if url_record:
                return self._url_to_response(url_record)
            return None

    def update_url_status(self, url_id: int, status: UrlStatus, error_message: Optional[str] = None):
        """Update URL status and optional error message."""
        with self.get_session() as session:
            try:
                url_record = session.query(UrlRecord).filter(UrlRecord.id == url_id).first()
                if url_record:
                    url_record.status = status
                    if status == UrlStatus.SCRAPED:
                        url_record.scraped_at = datetime.utcnow()
                    if error_message:
                        url_record.error_message = error_message
                    session.commit()
            except Exception as e:
                session.rollback()
                raise e

    def count_urls(self, domain: Optional[str] = None, status: Optional[UrlStatus] = None) -> int:
        """Count URLs in database with optional filtering."""
        with self.get_session() as session:
            query = session.query(UrlRecord)

            if domain:
                query = query.join(DomainRecord).filter(DomainRecord.domain == domain)
            if status:
                query = query.filter(UrlRecord.status == status)

            return query.count()

    def get_url_by_id(self, url_id: int) -> Optional[UrlResponse]:
        """Get a single URL record by ID."""
        with self.get_session() as session:
            url_record = session.query(UrlRecord).filter(UrlRecord.id == url_id).first()
            if url_record:
                return self._url_to_response(url_record)
            return None

    def get_raw_content_by_url_id(self, url_id: int) -> Optional[RawContentResponse]:
        """Get raw content for a specific URL ID."""
        with self.get_session() as session:
            # Get the raw content that matches this URL ID
            raw_content = session.query(RawContent)\
                .filter(RawContent.url_id == url_id)\
                .first()

            if raw_content:
                # Get the URL record for additional context
                url_record = session.query(UrlRecord)\
                    .filter(UrlRecord.id == url_id)\
                    .first()

                if url_record:
                    # Get domain name through relationship
                    domain = session.query(DomainRecord).filter(DomainRecord.id == url_record.domain_id).first()
                    domain_name = domain.domain if domain else "unknown"

                    # Parse headers if they exist
                    headers_dict = None
                    if raw_content.headers:
                        try:
                            import json
                            headers_dict = json.loads(raw_content.headers)
                        except:
                            headers_dict = None

                    return RawContentResponse(
                        id=raw_content.id,
                        url=url_record.url,
                        domain=domain_name,
                        html=raw_content.html,
                        headers=headers_dict,
                        scraped_at=raw_content.scraped_at,
                        size_bytes=raw_content.size_bytes,
                        content_type=headers_dict.get('content-type') if headers_dict else None
                    )
            return None

    def get_cleaned_content_by_url_id(self, url_id: int) -> Optional[CleanedContentResponse]:
        """Get cleaned content for a specific URL ID."""
        with self.get_session() as session:
            # Get the cleaned content that matches this URL ID via raw content
            cleaned_content = session.query(CleanContent, RawContent, UrlRecord)\
                .join(RawContent, CleanContent.raw_content_id == RawContent.id)\
                .join(UrlRecord, RawContent.url_id == UrlRecord.id)\
                .filter(UrlRecord.id == url_id)\
                .first()

            if cleaned_content:
                clean_record, raw_record, url_record = cleaned_content

                # Get domain name through relationship
                domain = session.query(DomainRecord).filter(DomainRecord.id == url_record.domain_id).first()
                domain_name = domain.domain if domain else "unknown"

                return CleanedContentResponse(
                    id=clean_record.id,
                    url=url_record.url,
                    domain=domain_name,
                    title=clean_record.title,
                    text=clean_record.text,
                    cleaned_at=clean_record.cleaned_at,
                    text_length=clean_record.text_length,
                    raw_content_id=clean_record.raw_content_id
                )
            return None

    # Domain Management
    def add_domain(self, domain_data: DomainCreate) -> DomainResponse:
        """Add a new domain to the database."""
        with self.get_session() as session:
            try:
                # Convert path filters to JSON string if provided
                path_filters_json = None
                if domain_data.default_path_filters:
                    import json
                    path_filters_json = json.dumps(domain_data.default_path_filters)

                db_domain = DomainRecord(
                    domain=domain_data.domain,
                    status=domain_data.status,
                    sitemap_url=domain_data.sitemap_url,
                    default_path_filters=path_filters_json,
                    crawl_frequency_days=domain_data.crawl_frequency_days,
                    rate_limit_seconds=domain_data.rate_limit_seconds
                )
                session.add(db_domain)
                session.commit()
                session.refresh(db_domain)

                # Convert back to response model
                return self._domain_to_response(db_domain)
            except Exception as e:
                session.rollback()
                raise e

    def get_domains(self, status: Optional[DomainStatus] = None,
                   limit: int = 100, offset: int = 0) -> List[DomainResponse]:
        """Get domains with optional filtering."""
        with self.get_session() as session:
            query = session.query(DomainRecord)

            if status:
                query = query.filter(DomainRecord.status == status)

            domains = query.order_by(DomainRecord.created_at.desc()).offset(offset).limit(limit).all()
            return [self._domain_to_response(domain) for domain in domains]

    def get_domain_by_name(self, domain_name: str) -> Optional[DomainResponse]:
        """Get a domain by its name."""
        with self.get_session() as session:
            domain = session.query(DomainRecord).filter(DomainRecord.domain == domain_name).first()
            if domain:
                return self._domain_to_response(domain)
            return None

    def get_domain_by_id(self, domain_id: int) -> Optional[DomainResponse]:
        """Get a domain by its ID."""
        with self.get_session() as session:
            domain = session.query(DomainRecord).filter(DomainRecord.id == domain_id).first()
            if domain:
                return self._domain_to_response(domain)
            return None

    def update_domain(self, domain_id: int, domain_data: DomainUpdate) -> Optional[DomainResponse]:
        """Update a domain."""
        with self.get_session() as session:
            try:
                domain = session.query(DomainRecord).filter(DomainRecord.id == domain_id).first()
                if not domain:
                    return None

                # Update fields that are provided
                if domain_data.status is not None:
                    domain.status = domain_data.status
                if domain_data.sitemap_url is not None:
                    domain.sitemap_url = domain_data.sitemap_url
                if domain_data.default_path_filters is not None:
                    import json
                    domain.default_path_filters = json.dumps(domain_data.default_path_filters)
                if domain_data.crawl_frequency_days is not None:
                    domain.crawl_frequency_days = domain_data.crawl_frequency_days
                if domain_data.rate_limit_seconds is not None:
                    domain.rate_limit_seconds = domain_data.rate_limit_seconds

                domain.updated_at = datetime.utcnow()
                session.commit()
                session.refresh(domain)

                return self._domain_to_response(domain)
            except Exception as e:
                session.rollback()
                raise e

    def get_or_create_domain(self, domain_name: str) -> DomainResponse:
        """Get existing domain or create new one if it doesn't exist."""
        # Normalize domain name
        normalized_domain = self.normalize_domain(domain_name)

        existing = self.get_domain_by_name(normalized_domain)
        if existing:
            return existing

        # Create new domain
        domain_data = DomainCreate(
            domain=normalized_domain,
            status=DomainStatus.ACTIVE
        )
        return self.add_domain(domain_data)

    def delete_domain(self, domain_id: int) -> bool:
        """Delete a domain and all its associated URLs, jobs, and content."""
        with self.get_session() as session:
            try:
                # Get all URL IDs for this domain first (to delete content later)
                url_ids = [row.id for row in session.query(UrlRecord.id).filter(UrlRecord.domain_id == domain_id)]

                # Delete clean content that references raw content that references these URLs
                if url_ids:
                    raw_content_ids = [row.id for row in session.query(RawContent.id).filter(RawContent.url_id.in_(url_ids))]
                    if raw_content_ids:
                        session.query(CleanContent).filter(CleanContent.raw_content_id.in_(raw_content_ids)).delete()

                    # Delete raw content for these URLs
                    session.query(RawContent).filter(RawContent.url_id.in_(url_ids)).delete()

                # Delete all scrape jobs for this domain
                session.query(ScrapeJob).filter(ScrapeJob.domain_id == domain_id).delete()

                # Delete all URLs for this domain
                session.query(UrlRecord).filter(UrlRecord.domain_id == domain_id).delete()

                # Finally delete the domain
                domain = session.query(DomainRecord).filter(DomainRecord.id == domain_id).first()
                if domain:
                    session.delete(domain)
                    session.commit()
                    return True
                return False
            except Exception as e:
                session.rollback()
                raise e

    def _domain_to_response(self, domain: DomainRecord) -> DomainResponse:
        """Convert DomainRecord to DomainResponse."""
        # Parse path filters from JSON
        default_path_filters = None
        if domain.default_path_filters:
            try:
                import json
                default_path_filters = json.loads(domain.default_path_filters)
            except:
                default_path_filters = None

        return DomainResponse(
            id=domain.id,
            domain=domain.domain,
            status=domain.status,
            sitemap_url=domain.sitemap_url,
            last_crawled_at=domain.last_crawled_at,
            last_successful_crawl=domain.last_successful_crawl,
            total_urls_found=domain.total_urls_found,
            default_path_filters=default_path_filters,
            crawl_frequency_days=domain.crawl_frequency_days,
            rate_limit_seconds=domain.rate_limit_seconds,
            created_at=domain.created_at,
            updated_at=domain.updated_at
        )

    def _update_domain_url_count(self, domain_id: int, additional_count: int):
        """Update domain's total_urls_found by adding additional URLs found."""
        with self.get_session() as session:
            try:
                domain = session.query(DomainRecord).filter(DomainRecord.id == domain_id).first()
                if domain:
                    domain.total_urls_found = (domain.total_urls_found or 0) + additional_count
                    domain.last_crawled_at = datetime.utcnow()
                    domain.updated_at = datetime.utcnow()
                    session.commit()
            except Exception as e:
                session.rollback()
                raise e

    def _url_to_response(self, url: UrlRecord) -> UrlResponse:
        """Convert UrlRecord to UrlResponse with domain name and cleaned content status."""
        with self.get_session() as session:
            domain = session.query(DomainRecord).filter(DomainRecord.id == url.domain_id).first()
            domain_name = domain.domain if domain else "unknown"

            # Check if cleaned content exists for this URL
            has_cleaned = session.query(CleanContent)\
                .join(RawContent, CleanContent.raw_content_id == RawContent.id)\
                .filter(RawContent.url_id == url.id)\
                .first() is not None

            return UrlResponse(
                id=url.id,
                url=url.url,
                domain=domain_name,
                sitemap_url=url.sitemap_url,
                priority=url.priority,
                lastmod=url.lastmod,
                changefreq=url.changefreq,
                collected_at=url.collected_at,
                path_filter=url.path_filter,
                status=url.status,
                scraped_at=url.scraped_at,
                error_message=url.error_message,
                has_cleaned_content=has_cleaned
            )

    def _job_to_response(self, job: ScrapeJob) -> JobResponse:
        """Convert ScrapeJob to JobResponse with domain name."""
        with self.get_session() as session:
            domain = session.query(DomainRecord).filter(DomainRecord.id == job.domain_id).first()
            domain_name = domain.domain if domain else "unknown"

            return JobResponse(
                id=job.id,
                domain=domain_name,
                job_type=job.job_type,
                status=job.status,
                total_urls=job.total_urls,
                processed_count=job.processed_count,
                failed_count=job.failed_count,
                started_at=job.started_at,
                completed_at=job.completed_at,
                limit=job.limit,
                error_message=job.error_message
            )

    # Job Management
    def create_job(self, job_id: str, domain: str, job_type: JobType,
                   total_urls: Optional[int] = None, limit: Optional[int] = None) -> ScrapeJob:
        """Create a new background job."""
        with self.get_session() as session:
            try:
                # Get or create domain and use its ID
                domain_response = self.get_or_create_domain(domain)

                job = ScrapeJob(
                    id=job_id,
                    domain_id=domain_response.id,
                    job_type=job_type,
                    total_urls=total_urls,
                    limit=limit
                )
                session.add(job)
                session.commit()
                session.refresh(job)
                return job
            except Exception as e:
                session.rollback()
                raise e

    def get_job(self, job_id: str) -> Optional[JobResponse]:
        """Get job by ID."""
        with self.get_session() as session:
            job = session.query(ScrapeJob).filter(ScrapeJob.id == job_id).first()
            if job:
                return self._job_to_response(job)
            return None

    def get_jobs(self, domain: Optional[str] = None, limit: int = 50) -> List[JobResponse]:
        """Get jobs with optional domain filtering."""
        with self.get_session() as session:
            query = session.query(ScrapeJob).order_by(ScrapeJob.started_at.desc())

            if domain:
                query = query.join(DomainRecord).filter(DomainRecord.domain == domain)

            jobs = query.limit(limit).all()
            return [self._job_to_response(job) for job in jobs]

    def update_job_progress(self, job_id: str, processed_count: int, failed_count: int):
        """Update job progress counters."""
        with self.get_session() as session:
            try:
                job = session.query(ScrapeJob).filter(ScrapeJob.id == job_id).first()
                if job:
                    job.processed_count = processed_count
                    job.failed_count = failed_count
                    session.commit()
            except Exception as e:
                session.rollback()
                raise e

    def complete_job(self, job_id: str, status: JobStatus, error_message: Optional[str] = None):
        """Mark job as completed or failed."""
        with self.get_session() as session:
            try:
                job = session.query(ScrapeJob).filter(ScrapeJob.id == job_id).first()
                if job:
                    job.status = status
                    job.completed_at = datetime.utcnow()
                    if error_message:
                        job.error_message = error_message
                    session.commit()
            except Exception as e:
                session.rollback()
                raise e

    # Content Management
    def add_raw_content(self, url_id: int, html: str, headers: Optional[str] = None) -> int:
        """Add raw HTML content for a URL."""
        with self.get_session() as session:
            try:
                content = RawContent(
                    url_id=url_id,
                    html=html,
                    headers=headers,
                    size_bytes=len(html.encode('utf-8'))
                )
                session.add(content)
                session.commit()
                session.refresh(content)
                return content.id
            except Exception as e:
                session.rollback()
                raise e

    def add_clean_content(self, raw_content_id: int, title: Optional[str], text: str) -> int:
        """Add cleaned text content."""
        with self.get_session() as session:
            try:
                content = CleanContent(
                    raw_content_id=raw_content_id,
                    title=title,
                    text=text,
                    text_length=len(text)
                )
                session.add(content)
                session.commit()
                session.refresh(content)
                return content.id
            except Exception as e:
                session.rollback()
                raise e

    def get_content(self, domain: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[ContentResponse]:
        """Get cleaned content with optional domain filtering."""
        with self.get_session() as session:
            query = session.query(CleanContent, RawContent, UrlRecord)\
                .join(RawContent, CleanContent.raw_content_id == RawContent.id)\
                .join(UrlRecord, RawContent.url_id == UrlRecord.id)

            if domain:
                query = query.join(DomainRecord, UrlRecord.domain_id == DomainRecord.id)\
                        .filter(DomainRecord.domain == domain)

            results = query.offset(offset).limit(limit).all()

            return [
                ContentResponse(
                    id=clean.id,
                    url=url.url,
                    title=clean.title,
                    text=clean.text,
                    cleaned_at=clean.cleaned_at,
                    text_length=clean.text_length
                )
                for clean, raw, url in results
            ]

    def get_raw_content(self, domain: Optional[str] = None, min_size: Optional[int] = None,
                       max_size: Optional[int] = None, scraped_after: Optional[datetime] = None,
                       scraped_before: Optional[datetime] = None, limit: int = 50, offset: int = 0) -> List[RawContentListItem]:
        """Get raw content with filtering and pagination (lightweight, no HTML)."""
        with self.get_session() as session:
            query = session.query(RawContent, UrlRecord, DomainRecord)\
                .join(UrlRecord, RawContent.url_id == UrlRecord.id)\
                .join(DomainRecord, UrlRecord.domain_id == DomainRecord.id)

            # Apply filters
            if domain:
                query = query.filter(DomainRecord.domain == domain)
            if min_size:
                query = query.filter(RawContent.size_bytes >= min_size)
            if max_size:
                query = query.filter(RawContent.size_bytes <= max_size)
            if scraped_after:
                query = query.filter(RawContent.scraped_at >= scraped_after)
            if scraped_before:
                query = query.filter(RawContent.scraped_at <= scraped_before)

            results = query.order_by(RawContent.scraped_at.desc()).offset(offset).limit(limit).all()

            return [
                RawContentListItem(
                    id=raw.id,
                    url=url.url,
                    domain=domain_record.domain,
                    scraped_at=raw.scraped_at,
                    size_bytes=raw.size_bytes,
                    content_type=self._extract_content_type(raw.headers),
                    has_headers=bool(raw.headers)
                )
                for raw, url, domain_record in results
            ]

    def get_raw_content_by_id(self, content_id: int, include_html: bool = True) -> Optional[RawContentResponse]:
        """Get specific raw content by ID."""
        with self.get_session() as session:
            result = session.query(RawContent, UrlRecord)\
                .join(UrlRecord, RawContent.url_id == UrlRecord.id)\
                .filter(RawContent.id == content_id).first()

            if not result:
                return None

            raw, url = result
            return RawContentResponse(
                id=raw.id,
                url=url.url,
                domain=url.domain,
                html=raw.html if include_html else None,
                headers=self._parse_headers(raw.headers) if raw.headers else None,
                scraped_at=raw.scraped_at,
                size_bytes=raw.size_bytes,
                content_type=self._extract_content_type(raw.headers)
            )

    def get_raw_content_headers(self, content_id: int) -> Optional[RawContentHeadersResponse]:
        """Get headers for specific raw content."""
        with self.get_session() as session:
            result = session.query(RawContent, UrlRecord)\
                .join(UrlRecord, RawContent.url_id == UrlRecord.id)\
                .filter(RawContent.id == content_id).first()

            if not result:
                return None

            raw, url = result
            return RawContentHeadersResponse(
                id=raw.id,
                url=url.url,
                headers=self._parse_headers(raw.headers) if raw.headers else None,
                scraped_at=raw.scraped_at,
                content_type=self._extract_content_type(raw.headers)
            )

    def get_content_comparison(self, content_id: int) -> Optional[ContentComparisonResponse]:
        """Get comparison between raw and cleaned content."""
        with self.get_session() as session:
            # Get raw content with URL
            raw_result = session.query(RawContent, UrlRecord)\
                .join(UrlRecord, RawContent.url_id == UrlRecord.id)\
                .filter(RawContent.id == content_id).first()

            if not raw_result:
                return None

            raw, url = raw_result

            # Get cleaned content if available
            clean = session.query(CleanContent)\
                .filter(CleanContent.raw_content_id == content_id).first()

            # Calculate comparison stats
            raw_size = raw.size_bytes or len(raw.html.encode('utf-8'))
            clean_size = len(clean.text.encode('utf-8')) if clean else 0
            compression_ratio = clean_size / raw_size if raw_size > 0 else 0

            return ContentComparisonResponse(
                url=url.url,
                domain=url.domain,
                raw_content={
                    "id": raw.id,
                    "html": raw.html,
                    "size_bytes": raw_size,
                    "scraped_at": raw.scraped_at.isoformat(),
                    "headers": self._parse_headers(raw.headers) if raw.headers else None
                },
                cleaned_content={
                    "id": clean.id,
                    "title": clean.title,
                    "text": clean.text,
                    "text_length": clean.text_length,
                    "cleaned_at": clean.cleaned_at.isoformat()
                } if clean else None,
                comparison_stats={
                    "original_size_bytes": raw_size,
                    "cleaned_size_bytes": clean_size,
                    "compression_ratio": compression_ratio,
                    "size_reduction_percent": ((raw_size - clean_size) / raw_size * 100) if raw_size > 0 else 0,
                    "has_cleaned_version": bool(clean)
                }
            )

    def get_raw_content_stats(self, domain: Optional[str] = None) -> RawContentStatsResponse:
        """Get statistics for raw content."""
        with self.get_session() as session:
            # Build base query
            base_query = session.query(RawContent).join(UrlRecord, RawContent.url_id == UrlRecord.id)

            if domain:
                base_query = base_query.join(DomainRecord, UrlRecord.domain_id == DomainRecord.id)\
                            .filter(DomainRecord.domain == domain)

            # Get basic stats
            total_count = base_query.count()

            if total_count == 0:
                return RawContentStatsResponse(
                    total_count=0,
                    total_size_bytes=0,
                    average_size_bytes=0,
                    size_distribution={},
                    domains={},
                    oldest_content=None,
                    newest_content=None
                )

            # Size stats
            size_result = session.execute(text(f"""
                SELECT
                    SUM(r.size_bytes) as total_size,
                    AVG(r.size_bytes) as avg_size,
                    MIN(r.scraped_at) as oldest,
                    MAX(r.scraped_at) as newest
                FROM raw_content r
                JOIN urls u ON r.url_id = u.id
                {'WHERE u.domain = :domain' if domain else ''}
            """), {"domain": domain} if domain else {})

            size_row = size_result.first()

            # Size distribution
            distribution_result = session.execute(text(f"""
                SELECT
                    CASE
                        WHEN r.size_bytes < 50000 THEN 'under_50kb'
                        WHEN r.size_bytes < 100000 THEN '50kb_to_100kb'
                        WHEN r.size_bytes < 500000 THEN '100kb_to_500kb'
                        ELSE 'over_500kb'
                    END as size_bucket,
                    COUNT(*) as count
                FROM raw_content r
                JOIN urls u ON r.url_id = u.id
                {'WHERE u.domain = :domain' if domain else ''}
                GROUP BY size_bucket
            """), {"domain": domain} if domain else {})

            size_distribution = {row.size_bucket: row.count for row in distribution_result}

            # Domain distribution (only if not filtering by domain)
            domains = {}
            if not domain:
                domain_result = session.execute(text("""
                    SELECT u.domain, COUNT(r.id) as count
                    FROM raw_content r
                    JOIN urls u ON r.url_id = u.id
                    GROUP BY u.domain
                    ORDER BY count DESC
                """))
                domains = {row.domain: row.count for row in domain_result}

            return RawContentStatsResponse(
                total_count=total_count,
                total_size_bytes=int(size_row.total_size or 0),
                average_size_bytes=int(size_row.avg_size or 0),
                size_distribution=size_distribution,
                domains=domains,
                oldest_content=size_row.oldest,
                newest_content=size_row.newest
            )

    def _extract_content_type(self, headers_str: Optional[str]) -> Optional[str]:
        """Extract content-type from headers string."""
        if not headers_str:
            return None
        try:
            import json
            headers = json.loads(headers_str)
            return headers.get('content-type') or headers.get('Content-Type')
        except:
            return None

    def _parse_headers(self, headers_str: Optional[str]) -> Optional[Dict[str, Any]]:
        """Parse headers from JSON string."""
        if not headers_str:
            return None
        try:
            import json
            return json.loads(headers_str)
        except:
            return None

    def get_cleaned_content(self, domain: Optional[str] = None, title_search: Optional[str] = None,
                           min_length: Optional[int] = None, max_length: Optional[int] = None,
                           cleaned_after: Optional[datetime] = None, cleaned_before: Optional[datetime] = None,
                           limit: int = 50, offset: int = 0) -> List[CleanedContentListItem]:
        """Get cleaned content with comprehensive filtering and pagination."""
        with self.get_session() as session:
            query = session.query(CleanContent, RawContent, UrlRecord)\
                .join(RawContent, CleanContent.raw_content_id == RawContent.id)\
                .join(UrlRecord, RawContent.url_id == UrlRecord.id)

            # Apply filters
            if domain:
                query = query.join(DomainRecord, UrlRecord.domain_id == DomainRecord.id)\
                        .filter(DomainRecord.domain == domain)
            if title_search:
                query = query.filter(CleanContent.title.ilike(f"%{title_search}%"))
            if min_length:
                query = query.filter(CleanContent.text_length >= min_length)
            if max_length:
                query = query.filter(CleanContent.text_length <= max_length)
            if cleaned_after:
                query = query.filter(CleanContent.cleaned_at >= cleaned_after)
            if cleaned_before:
                query = query.filter(CleanContent.cleaned_at <= cleaned_before)

            results = query.order_by(CleanContent.cleaned_at.desc()).offset(offset).limit(limit).all()

            return [
                CleanedContentListItem(
                    id=clean.id,
                    url=url.url,
                    domain=url.domain,
                    title=clean.title,
                    cleaned_at=clean.cleaned_at,
                    text_length=clean.text_length,
                    raw_content_id=clean.raw_content_id,
                    text_preview=clean.text[:200] + "..." if clean.text and len(clean.text) > 200 else clean.text
                )
                for clean, raw, url in results
            ]

    def get_cleaned_content_by_id(self, content_id: int, include_text: bool = True) -> Optional[CleanedContentResponse]:
        """Get specific cleaned content by ID."""
        with self.get_session() as session:
            result = session.query(CleanContent, RawContent, UrlRecord)\
                .join(RawContent, CleanContent.raw_content_id == RawContent.id)\
                .join(UrlRecord, RawContent.url_id == UrlRecord.id)\
                .filter(CleanContent.id == content_id).first()

            if not result:
                return None

            clean, raw, url = result
            return CleanedContentResponse(
                id=clean.id,
                url=url.url,
                domain=url.domain,
                title=clean.title,
                text=clean.text if include_text else None,
                cleaned_at=clean.cleaned_at,
                text_length=clean.text_length,
                raw_content_id=clean.raw_content_id
            )

    def count_cleaned_content(self, domain: Optional[str] = None, title_search: Optional[str] = None,
                             min_length: Optional[int] = None, max_length: Optional[int] = None,
                             cleaned_after: Optional[datetime] = None, cleaned_before: Optional[datetime] = None) -> int:
        """Count cleaned content with optional filtering."""
        with self.get_session() as session:
            query = session.query(CleanContent)\
                .join(RawContent, CleanContent.raw_content_id == RawContent.id)\
                .join(UrlRecord, RawContent.url_id == UrlRecord.id)

            # Apply same filters as get_cleaned_content
            if domain:
                query = query.join(DomainRecord, UrlRecord.domain_id == DomainRecord.id)\
                        .filter(DomainRecord.domain == domain)
            if title_search:
                query = query.filter(CleanContent.title.ilike(f"%{title_search}%"))
            if min_length:
                query = query.filter(CleanContent.text_length >= min_length)
            if max_length:
                query = query.filter(CleanContent.text_length <= max_length)
            if cleaned_after:
                query = query.filter(CleanContent.cleaned_at >= cleaned_after)
            if cleaned_before:
                query = query.filter(CleanContent.cleaned_at <= cleaned_before)

            return query.count()

    def search_cleaned_content(self, search_query: str, domain: Optional[str] = None,
                              limit: int = 50, offset: int = 0) -> List[CleanedContentSearchResponse]:
        """Search cleaned content by title and text content."""
        with self.get_session() as session:
            # Use basic text search with ILIKE for title and content
            query = session.query(CleanContent, RawContent, UrlRecord)\
                .join(RawContent, CleanContent.raw_content_id == RawContent.id)\
                .join(UrlRecord, RawContent.url_id == UrlRecord.id)

            # Search in title and text content
            search_filter = or_(
                CleanContent.title.ilike(f"%{search_query}%"),
                CleanContent.text.ilike(f"%{search_query}%")
            )
            query = query.filter(search_filter)

            if domain:
                query = query.join(DomainRecord, UrlRecord.domain_id == DomainRecord.id)\
                        .filter(DomainRecord.domain == domain)

            results = query.order_by(CleanContent.cleaned_at.desc()).offset(offset).limit(limit).all()

            search_results = []
            for clean, raw, url in results:
                # Create snippet with search term highlighted
                snippet = self._create_search_snippet(clean.text or "", search_query)

                # Simple relevance scoring (title match gets higher score)
                relevance = 1.0
                if clean.title and search_query.lower() in clean.title.lower():
                    relevance = 2.0

                search_results.append(CleanedContentSearchResponse(
                    id=clean.id,
                    url=url.url,
                    domain=url.domain,
                    title=clean.title,
                    text_snippet=snippet,
                    cleaned_at=clean.cleaned_at,
                    text_length=clean.text_length,
                    raw_content_id=clean.raw_content_id,
                    relevance_score=relevance
                ))

            return search_results

    def get_cleaned_content_stats(self, domain: Optional[str] = None) -> CleanedContentStatsResponse:
        """Get comprehensive statistics for cleaned content."""
        with self.get_session() as session:
            # Build base query
            base_query = session.query(CleanContent)\
                .join(RawContent, CleanContent.raw_content_id == RawContent.id)\
                .join(UrlRecord, RawContent.url_id == UrlRecord.id)

            if domain:
                base_query = base_query.join(DomainRecord, UrlRecord.domain_id == DomainRecord.id)\
                            .filter(DomainRecord.domain == domain)

            # Get basic stats
            total_count = base_query.count()

            if total_count == 0:
                return CleanedContentStatsResponse(
                    total_count=0,
                    total_text_length=0,
                    average_text_length=0,
                    length_distribution={},
                    domains={},
                    oldest_content=None,
                    newest_content=None,
                    content_with_titles=0,
                    title_completion_rate=0.0
                )

            # Length and title stats
            stats_result = session.execute(text(f"""
                SELECT
                    SUM(c.text_length) as total_length,
                    AVG(c.text_length) as avg_length,
                    MIN(c.cleaned_at) as oldest,
                    MAX(c.cleaned_at) as newest,
                    COUNT(CASE WHEN c.title IS NOT NULL AND c.title != '' THEN 1 END) as with_titles
                FROM clean_content c
                JOIN raw_content r ON c.raw_content_id = r.id
                JOIN urls u ON r.url_id = u.id
                {'WHERE u.domain = :domain' if domain else ''}
            """), {"domain": domain} if domain else {})

            stats_row = stats_result.first()

            # Length distribution
            distribution_result = session.execute(text(f"""
                SELECT
                    CASE
                        WHEN c.text_length < 1000 THEN 'under_1k'
                        WHEN c.text_length < 5000 THEN '1k_to_5k'
                        WHEN c.text_length < 10000 THEN '5k_to_10k'
                        ELSE 'over_10k'
                    END as length_bucket,
                    COUNT(*) as count
                FROM clean_content c
                JOIN raw_content r ON c.raw_content_id = r.id
                JOIN urls u ON r.url_id = u.id
                {'WHERE u.domain = :domain' if domain else ''}
                GROUP BY length_bucket
            """), {"domain": domain} if domain else {})

            length_distribution = {row.length_bucket: row.count for row in distribution_result}

            # Domain distribution (only if not filtering by domain)
            domains = {}
            if not domain:
                domain_result = session.execute(text("""
                    SELECT u.domain, COUNT(c.id) as count
                    FROM clean_content c
                    JOIN raw_content r ON c.raw_content_id = r.id
                    JOIN urls u ON r.url_id = u.id
                    GROUP BY u.domain
                    ORDER BY count DESC
                """))
                domains = {row.domain: row.count for row in domain_result}

            # Calculate title completion rate
            content_with_titles = int(stats_row.with_titles or 0)
            title_completion_rate = (content_with_titles / total_count * 100) if total_count > 0 else 0

            return CleanedContentStatsResponse(
                total_count=total_count,
                total_text_length=int(stats_row.total_length or 0),
                average_text_length=int(stats_row.avg_length or 0),
                length_distribution=length_distribution,
                domains=domains,
                oldest_content=stats_row.oldest,
                newest_content=stats_row.newest,
                content_with_titles=content_with_titles,
                title_completion_rate=title_completion_rate
            )

    def _create_search_snippet(self, text: str, search_query: str, snippet_length: int = 300) -> str:
        """Create a text snippet highlighting search terms."""
        if not text:
            return ""

        # Find the position of the search query (case insensitive)
        query_lower = search_query.lower()
        text_lower = text.lower()
        pos = text_lower.find(query_lower)

        if pos == -1:
            # Search query not found, return beginning of text
            return text[:snippet_length] + ("..." if len(text) > snippet_length else "")

        # Calculate snippet boundaries
        start = max(0, pos - snippet_length // 2)
        end = min(len(text), start + snippet_length)

        # Adjust start if we're near the end
        if end == len(text):
            start = max(0, end - snippet_length)

        snippet = text[start:end]

        # Add ellipsis if needed
        if start > 0:
            snippet = "..." + snippet
        if end < len(text):
            snippet = snippet + "..."

        return snippet

    # Statistics
    def get_domain_stats(self) -> List[DomainStats]:
        """Get comprehensive domain statistics."""
        with self.get_session() as session:
            # Get URL counts by status
            result = session.execute(text("""
                SELECT
                    domain,
                    COUNT(*) as total_urls,
                    COUNT(CASE WHEN status = 'scraped' THEN 1 END) as scraped_count,
                    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_count,
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_count,
                    MAX(collected_at) as last_activity
                FROM urls
                GROUP BY domain
                ORDER BY total_urls DESC
            """))

            # Get clean content counts
            content_result = session.execute(text("""
                SELECT u.domain, COUNT(c.id) as clean_count
                FROM urls u
                LEFT JOIN raw_content r ON u.id = r.url_id
                LEFT JOIN clean_content c ON r.id = c.raw_content_id
                GROUP BY u.domain
            """))

            content_counts = {row.domain: row.clean_count for row in content_result}

            return [
                DomainStats(
                    domain=row.domain,
                    total_urls=row.total_urls,
                    scraped_count=row.scraped_count,
                    failed_count=row.failed_count,
                    pending_count=row.pending_count,
                    clean_content_count=content_counts.get(row.domain, 0),
                    last_activity=row.last_activity
                )
                for row in result
            ]

    # Extracted Content Methods
    def add_extracted_content(self, raw_content_id: int, title: Optional[str], content: str,
                            has_tables: bool = False, has_lists: bool = False,
                            has_headings: bool = False, has_links: bool = False,
                            structure_score: Optional[float] = None) -> int:
        """Add extracted content to the database."""
        with self.get_session() as session:
            from models.trusted_sources import ExtractedContent

            extracted_content = ExtractedContent(
                raw_content_id=raw_content_id,
                title=title,
                content=content,
                content_length=len(content) if content else None,
                has_tables=has_tables,
                has_lists=has_lists,
                has_headings=has_headings,
                has_links=has_links,
                structure_score=structure_score
            )

            session.add(extracted_content)
            session.commit()
            return extracted_content.id

    def add_markdown_content(self, extracted_content_id: int, title: Optional[str], markdown: str,
                           chunk_count: Optional[int] = None, has_metadata: bool = False,
                           content_metadata: Optional[str] = None) -> int:
        """Add markdown content to the database."""
        with self.get_session() as session:
            from models.trusted_sources import MarkdownContent

            markdown_content = MarkdownContent(
                extracted_content_id=extracted_content_id,
                title=title,
                markdown=markdown,
                markdown_length=len(markdown) if markdown else None,
                chunk_count=chunk_count,
                has_metadata=has_metadata,
                content_metadata=content_metadata
            )

            session.add(markdown_content)
            session.commit()
            return markdown_content.id

    def update_url_status(self, url_id: int, status: str) -> bool:
        """Update URL status."""
        with self.get_session() as session:
            url_record = session.query(UrlRecord).filter(UrlRecord.id == url_id).first()
            if url_record:
                url_record.status = status
                session.commit()
                return True
            return False

    def get_extracted_content_by_url_id(self, url_id: int):
        """Get extracted content for a specific URL ID."""
        with self.get_session() as session:
            from models.trusted_sources import ExtractedContent, RawContent

            return session.query(ExtractedContent)\
                .join(RawContent, ExtractedContent.raw_content_id == RawContent.id)\
                .filter(RawContent.url_id == url_id)\
                .first()

    def get_markdown_content_by_url_id(self, url_id: int):
        """Get markdown content for a specific URL ID."""
        with self.get_session() as session:
            from models.trusted_sources import MarkdownContent, ExtractedContent, RawContent

            return session.query(MarkdownContent)\
                .join(ExtractedContent, MarkdownContent.extracted_content_id == ExtractedContent.id)\
                .join(RawContent, ExtractedContent.raw_content_id == RawContent.id)\
                .filter(RawContent.url_id == url_id)\
                .first()


# Global database instance
_db_service = None


def get_trusted_sources_db() -> TrustedSourcesDatabase:
    """Get singleton database service instance."""
    global _db_service
    if _db_service is None:
        _db_service = TrustedSourcesDatabase()
    return _db_service