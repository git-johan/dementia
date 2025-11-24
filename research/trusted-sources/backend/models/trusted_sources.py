#!/usr/bin/env python3
"""
Trusted Sources domain models for URLs, jobs, and content.
"""

import enum
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, text, Column, Integer, String, Text, DateTime, Float, Boolean, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import datetime
from pydantic import BaseModel


# SQLAlchemy Base
Base = declarative_base()


# Enums for status tracking
class UrlStatus(str, enum.Enum):
    PENDING = "pending"
    SCRAPED = "scraped"
    EXTRACTED = "extracted"
    CONVERTED = "converted"
    FAILED = "failed"


class JobType(str, enum.Enum):
    DISCOVER = "discover"
    SCRAPE = "scrape"
    EXTRACT = "extract"
    CONVERT = "convert"
    PROCESS = "process"  # For batch processing pipeline


class JobStatus(str, enum.Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class DomainStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLOCKED = "blocked"




# Database Models
class DomainRecord(Base):
    """Domain record with metadata and crawl configuration."""
    __tablename__ = "domains"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String(255), nullable=False, unique=True, index=True)
    status = Column(Enum(DomainStatus), default=DomainStatus.ACTIVE, nullable=False)

    # Crawl metadata
    sitemap_url = Column(String(500), nullable=True)
    last_crawled_at = Column(DateTime, nullable=True)
    last_successful_crawl = Column(DateTime, nullable=True)
    total_urls_found = Column(Integer, default=0)

    # Crawl configuration
    default_path_filters = Column(Text, nullable=True)  # JSON string: ["/dementia/*", "/research/*"]
    crawl_frequency_days = Column(Integer, default=7)  # How often to re-crawl
    rate_limit_seconds = Column(Float, default=2.0)    # Respectful crawling delay

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    urls = relationship("UrlRecord", back_populates="domain_ref")
    jobs = relationship("ScrapeJob", back_populates="domain_ref")


class UrlRecord(Base):
    """URL record with status tracking for scraping pipeline."""
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(Text, nullable=False, index=True)
    domain_id = Column(Integer, ForeignKey("domains.id"), nullable=False, index=True)
    sitemap_url = Column(Text, nullable=True)
    priority = Column(Float, nullable=True)
    lastmod = Column(String(255), nullable=True)  # Store as string to preserve original format
    changefreq = Column(String(50), nullable=True)
    collected_at = Column(DateTime, default=datetime.utcnow)
    path_filter = Column(String(255), nullable=True)

    # Status tracking
    status = Column(Enum(UrlStatus), default=UrlStatus.PENDING, nullable=False, index=True)
    scraped_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)

    # Relationships
    domain_ref = relationship("DomainRecord", back_populates="urls")


class ScrapeJob(Base):
    """Background job tracking for discovery, scraping, and cleaning operations."""
    __tablename__ = "scrape_jobs"

    id = Column(String(100), primary_key=True)  # e.g., "scrape_456", "discover_123"
    domain_id = Column(Integer, ForeignKey("domains.id"), nullable=False, index=True)
    job_type = Column(Enum(JobType), nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.RUNNING, nullable=False)

    # Progress tracking
    total_urls = Column(Integer, nullable=True)  # Total URLs to process
    processed_count = Column(Integer, default=0)  # URLs processed (success + failed)
    failed_count = Column(Integer, default=0)  # Failed URLs

    # Timing
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Additional metadata
    limit = Column(Integer, nullable=True)  # For test mode
    error_message = Column(Text, nullable=True)

    # Relationships
    domain_ref = relationship("DomainRecord", back_populates="jobs")


class RawContent(Base):
    """Downloaded HTML content from scraped URLs."""
    __tablename__ = "raw_content"

    id = Column(Integer, primary_key=True, index=True)
    url_id = Column(Integer, nullable=False, index=True)  # FK to urls.id
    html = Column(Text, nullable=False)
    headers = Column(Text, nullable=True)  # JSON string of HTTP headers
    scraped_at = Column(DateTime, default=datetime.utcnow)
    size_bytes = Column(Integer, nullable=True)


class CleanContent(Base):
    """Processed and cleaned text content."""
    __tablename__ = "clean_content"

    id = Column(Integer, primary_key=True, index=True)
    raw_content_id = Column(Integer, nullable=False, index=True)  # FK to raw_content.id
    title = Column(Text, nullable=True)
    text = Column(Text, nullable=False)
    cleaned_at = Column(DateTime, default=datetime.utcnow)
    text_length = Column(Integer, nullable=True)


class ExtractedContent(Base):
    """Extracted and filtered content ready for markdown conversion."""
    __tablename__ = "extracted_content"

    id = Column(Integer, primary_key=True, index=True)
    raw_content_id = Column(Integer, nullable=False, index=True)  # FK to raw_content.id
    title = Column(Text, nullable=True)
    content = Column(Text, nullable=False)  # Structured content with preserved HTML elements
    extracted_at = Column(DateTime, default=datetime.utcnow)
    content_length = Column(Integer, nullable=True)

    # Quality metrics
    has_tables = Column(Boolean, default=False)
    has_lists = Column(Boolean, default=False)
    has_headings = Column(Boolean, default=False)
    has_links = Column(Boolean, default=False)
    structure_score = Column(Float, nullable=True)  # Overall content structure quality score


class MarkdownContent(Base):
    """Final LLM-ready markdown content."""
    __tablename__ = "markdown_content"

    id = Column(Integer, primary_key=True, index=True)
    extracted_content_id = Column(Integer, nullable=False, index=True)  # FK to extracted_content.id
    title = Column(Text, nullable=True)
    markdown = Column(Text, nullable=False)  # Final markdown content
    converted_at = Column(DateTime, default=datetime.utcnow)
    markdown_length = Column(Integer, nullable=True)

    # LLM optimization metadata
    chunk_count = Column(Integer, nullable=True)  # Number of semantic chunks for embeddings
    has_metadata = Column(Boolean, default=False)  # Whether metadata was extracted
    content_metadata = Column(Text, nullable=True)  # JSON string of extracted metadata (author, date, etc.)


# Pydantic Models for API

# Request Models
class DiscoverRequest(BaseModel):
    domain: str
    path_filter: Optional[str] = None


class ScrapeRequest(BaseModel):
    domain: str
    limit: Optional[int] = None  # For test mode - limit URLs to process


class CleanRequest(BaseModel):
    domain: str
    limit: Optional[int] = None  # For test mode - limit content to process


class RetryRequest(BaseModel):
    urls: Optional[List[str]] = None
    domain: Optional[str] = None
    status: Optional[UrlStatus] = UrlStatus.FAILED


class ExtractRequest(BaseModel):
    """Request model for extracting content from raw HTML."""
    domain: Optional[str] = None
    url_id: Optional[int] = None  # For single URL extraction
    limit: Optional[int] = None  # For test mode - limit URLs to process


class ConvertRequest(BaseModel):
    """Request model for converting extracted content to markdown."""
    domain: Optional[str] = None
    url_id: Optional[int] = None  # For single URL conversion
    limit: Optional[int] = None  # For test mode - limit URLs to process


class ProcessRequest(BaseModel):
    """Request model for full pipeline processing (scrape → extract → convert)."""
    domain: str
    limit: Optional[int] = None  # For test mode - limit URLs to process
    skip_existing: bool = True  # Skip URLs that already have processed content


class UrlCreate(BaseModel):
    url: str
    domain: str
    sitemap_url: Optional[str] = None
    priority: Optional[float] = None
    lastmod: Optional[str] = None
    changefreq: Optional[str] = None
    path_filter: Optional[str] = None


class UrlsCreate(BaseModel):
    urls: List[str]


# Domain Management Models
class DomainCreate(BaseModel):
    domain: str
    status: DomainStatus = DomainStatus.ACTIVE
    sitemap_url: Optional[str] = None
    default_path_filters: Optional[List[str]] = None
    crawl_frequency_days: int = 7
    rate_limit_seconds: float = 2.0


class DomainUpdate(BaseModel):
    status: Optional[DomainStatus] = None
    sitemap_url: Optional[str] = None
    default_path_filters: Optional[List[str]] = None
    crawl_frequency_days: Optional[int] = None
    rate_limit_seconds: Optional[float] = None


# Response Models
class DomainResponse(BaseModel):
    id: int
    domain: str
    status: DomainStatus
    sitemap_url: Optional[str]
    last_crawled_at: Optional[datetime]
    last_successful_crawl: Optional[datetime]
    total_urls_found: int
    default_path_filters: Optional[List[str]]
    crawl_frequency_days: int
    rate_limit_seconds: float
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
class UrlResponse(BaseModel):
    id: int
    url: str
    domain: str  # Will be populated from domain_ref.domain in the database layer
    sitemap_url: Optional[str]
    priority: Optional[float]
    lastmod: Optional[str]
    changefreq: Optional[str]
    collected_at: datetime
    path_filter: Optional[str]
    status: UrlStatus
    scraped_at: Optional[datetime]
    error_message: Optional[str]
    has_cleaned_content: bool = False  # Whether cleaned content exists for this URL

    class Config:
        from_attributes = True


class JobResponse(BaseModel):
    id: str
    domain: str  # Will be populated from domain_ref.domain in the database layer
    job_type: JobType
    status: JobStatus
    total_urls: Optional[int]
    processed_count: int
    failed_count: int
    started_at: datetime
    completed_at: Optional[datetime]
    limit: Optional[int]  # Test mode indicator
    error_message: Optional[str]

    class Config:
        from_attributes = True


class JobProgress(BaseModel):
    """Real-time job progress for monitoring."""
    id: str
    status: JobStatus
    started_at: datetime
    processed_count: int
    failed_count: int
    total_urls: Optional[int]
    success_count: Optional[int] = None
    remaining_count: Optional[int] = None
    test_mode: bool = False

    @property
    def progress_percentage(self) -> Optional[float]:
        if self.total_urls and self.total_urls > 0:
            return (self.processed_count / self.total_urls) * 100
        return None


class ContentResponse(BaseModel):
    id: int
    url: str
    title: Optional[str]
    text: str
    cleaned_at: datetime
    text_length: Optional[int]

    class Config:
        from_attributes = True


class DomainStats(BaseModel):
    domain: str
    total_urls: int
    scraped_count: int
    failed_count: int
    pending_count: int
    clean_content_count: int
    last_activity: Optional[datetime]


class DiscoverResponse(BaseModel):
    job_id: str
    domain: str
    sitemap_url: Optional[str]
    urls_found: int
    status: JobStatus


class ScrapeResponse(BaseModel):
    job_id: str
    domain: str
    total_urls: int
    status: JobStatus
    test_mode: bool = False


class CleanResponse(BaseModel):
    job_id: str
    domain: str
    total_raw_content: int
    status: JobStatus
    test_mode: bool = False


class RetryResponse(BaseModel):
    retrying: int
    urls: List[str]


class ExtractResponse(BaseModel):
    """Response model for content extraction job."""
    job_id: str
    domain: str
    total_raw_content: int
    status: JobStatus
    test_mode: bool = False


class ConvertResponse(BaseModel):
    """Response model for markdown conversion job."""
    job_id: str
    domain: str
    total_extracted_content: int
    status: JobStatus
    test_mode: bool = False


class ProcessResponse(BaseModel):
    """Response model for full pipeline processing job."""
    job_id: str
    domain: str
    total_urls: int
    status: JobStatus
    pipeline_stages: List[str]  # ["scrape", "extract", "convert"]
    test_mode: bool = False


# Raw Content API Models
class RawContentResponse(BaseModel):
    """Response model for raw HTML content."""
    id: int
    url: str
    domain: str
    html: Optional[str] = None  # Optional for list responses to save bandwidth
    headers: Optional[Dict[str, Any]] = None  # HTTP headers as dict
    scraped_at: datetime
    size_bytes: Optional[int]
    content_type: Optional[str] = None  # Extracted from headers

    class Config:
        from_attributes = True


class RawContentListItem(BaseModel):
    """Lightweight response model for raw content lists (without full HTML)."""
    id: int
    url: str
    domain: str
    scraped_at: datetime
    size_bytes: Optional[int]
    content_type: Optional[str] = None
    has_headers: bool = False

    class Config:
        from_attributes = True


class RawContentHeadersResponse(BaseModel):
    """Response model for raw content headers only."""
    id: int
    url: str
    headers: Optional[Dict[str, Any]]
    scraped_at: datetime
    content_type: Optional[str] = None

    class Config:
        from_attributes = True


class ContentComparisonResponse(BaseModel):
    """Response model for comparing raw HTML vs cleaned content."""
    url: str
    domain: str
    raw_content: Dict[str, Any]  # Contains id, html, size_bytes, scraped_at
    cleaned_content: Optional[Dict[str, Any]]  # Contains id, title, text, cleaned_at, text_length
    comparison_stats: Dict[str, Any]  # Size reduction, compression ratio, etc.

    class Config:
        from_attributes = True


class RawContentStatsResponse(BaseModel):
    """Response model for raw content statistics."""
    total_count: int
    total_size_bytes: int
    average_size_bytes: int
    size_distribution: Dict[str, int]  # Size buckets and counts
    domains: Dict[str, int]  # Domain distribution
    oldest_content: Optional[datetime]
    newest_content: Optional[datetime]


# Cleaned Content API Models
class CleanedContentResponse(BaseModel):
    """Response model for cleaned content with full text."""
    id: int
    url: str
    domain: str
    title: Optional[str] = None
    text: Optional[str] = None  # Optional for list responses to save bandwidth
    cleaned_at: datetime
    text_length: Optional[int]
    raw_content_id: int  # Link back to raw content

    class Config:
        from_attributes = True


class CleanedContentListItem(BaseModel):
    """Lightweight response model for cleaned content lists (without full text)."""
    id: int
    url: str
    domain: str
    title: Optional[str] = None
    cleaned_at: datetime
    text_length: Optional[int]
    raw_content_id: int
    text_preview: Optional[str] = None  # First 200 characters

    class Config:
        from_attributes = True


class CleanedContentStatsResponse(BaseModel):
    """Response model for cleaned content statistics."""
    total_count: int
    total_text_length: int
    average_text_length: int
    length_distribution: Dict[str, int]  # Length buckets and counts
    domains: Dict[str, int]  # Domain distribution
    oldest_content: Optional[datetime]
    newest_content: Optional[datetime]
    content_with_titles: int  # Count of content that has titles
    title_completion_rate: float  # Percentage with titles


class CleanedContentSearchResponse(BaseModel):
    """Response model for search results in cleaned content."""
    id: int
    url: str
    domain: str
    title: Optional[str] = None
    text_snippet: str  # Highlighted text snippet with search terms
    cleaned_at: datetime
    text_length: Optional[int]
    raw_content_id: int
    relevance_score: Optional[float] = None  # Search relevance

    class Config:
        from_attributes = True


# Extracted Content API Models
class ExtractedContentResponse(BaseModel):
    """Response model for extracted content with structure preservation."""
    id: int
    url: str
    domain: str
    title: Optional[str] = None
    content: Optional[str] = None  # Optional for list responses to save bandwidth
    extracted_at: datetime
    content_length: Optional[int]
    raw_content_id: int
    has_tables: bool
    has_lists: bool
    has_headings: bool
    has_links: bool
    structure_score: Optional[float]

    class Config:
        from_attributes = True


class ExtractedContentListItem(BaseModel):
    """Lightweight response model for extracted content lists (without full content)."""
    id: int
    url: str
    domain: str
    title: Optional[str] = None
    extracted_at: datetime
    content_length: Optional[int]
    raw_content_id: int
    content_preview: Optional[str] = None  # First 200 characters
    has_tables: bool
    has_lists: bool
    has_headings: bool
    has_links: bool
    structure_score: Optional[float]

    class Config:
        from_attributes = True


class ExtractedContentStatsResponse(BaseModel):
    """Response model for extracted content statistics."""
    total_count: int
    total_content_length: int
    average_content_length: int
    length_distribution: Dict[str, int]  # Length buckets and counts
    domains: Dict[str, int]  # Domain distribution
    oldest_content: Optional[datetime]
    newest_content: Optional[datetime]
    content_with_titles: int  # Count of content that has titles
    title_completion_rate: float  # Percentage with titles
    structure_stats: Dict[str, int]  # Count of content with tables, lists, etc.
    average_structure_score: Optional[float]


# Markdown Content API Models
class MarkdownContentResponse(BaseModel):
    """Response model for final LLM-ready markdown content."""
    id: int
    url: str
    domain: str
    title: Optional[str] = None
    markdown: Optional[str] = None  # Optional for list responses to save bandwidth
    converted_at: datetime
    markdown_length: Optional[int]
    extracted_content_id: int
    chunk_count: Optional[int]
    has_metadata: bool
    content_metadata: Optional[Dict[str, Any]] = None  # Parsed metadata dict

    class Config:
        from_attributes = True


class MarkdownContentListItem(BaseModel):
    """Lightweight response model for markdown content lists (without full markdown)."""
    id: int
    url: str
    domain: str
    title: Optional[str] = None
    converted_at: datetime
    markdown_length: Optional[int]
    extracted_content_id: int
    markdown_preview: Optional[str] = None  # First 200 characters
    chunk_count: Optional[int]
    has_metadata: bool

    class Config:
        from_attributes = True


class MarkdownContentStatsResponse(BaseModel):
    """Response model for markdown content statistics."""
    total_count: int
    total_markdown_length: int
    average_markdown_length: int
    length_distribution: Dict[str, int]  # Length buckets and counts
    domains: Dict[str, int]  # Domain distribution
    oldest_content: Optional[datetime]
    newest_content: Optional[datetime]
    content_with_titles: int  # Count of content that has titles
    title_completion_rate: float  # Percentage with titles
    content_with_metadata: int  # Count of content with metadata
    metadata_completion_rate: float  # Percentage with metadata
    average_chunk_count: Optional[float]


# ============================================================================
# Crawl API Models
# ============================================================================

class CrawlRequest(BaseModel):
    """Request model for crawling a domain's sitemap."""
    domain: str
    path_filters: Optional[List[str]] = None  # e.g., ["/dementia/*", "/research/*"]
    overwrite_existing: bool = True
    max_urls: Optional[int] = None  # Safety limit


class CrawlResponse(BaseModel):
    """Response model for crawl job initiation."""
    job_id: str
    domain: str
    sitemap_url: Optional[str] = None
    status: str = "running"
    total_urls_found: Optional[int] = None
    path_filters: Optional[List[str]] = None