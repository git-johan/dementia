#!/usr/bin/env python3
"""
Trusted Sources API routes for discovery, scraping, cleaning, and content management.
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, Depends, Response

from models.trusted_sources import (
    DiscoverRequest, DiscoverResponse,
    ScrapeRequest, ScrapeResponse,
    CleanRequest, CleanResponse,
    RetryRequest, RetryResponse,
    UrlCreate, UrlsCreate, UrlResponse,
    JobResponse, ContentResponse, DomainStats,
    UrlStatus, RawContentResponse, RawContentListItem,
    RawContentHeadersResponse, ContentComparisonResponse,
    RawContentStatsResponse, CleanedContentResponse,
    CleanedContentListItem, CleanedContentStatsResponse,
    CleanedContentSearchResponse
)
from services.database import get_trusted_sources_db, TrustedSourcesDatabase
from services.discovery import get_discovery_service, DiscoveryService
from services.scraper import get_scraper_service, ScraperService
from services.cleaner import get_cleaner_service, CleanerService


# Create router
trusted_sources_router = APIRouter()


def get_db() -> TrustedSourcesDatabase:
    """Dependency to get database service."""
    return get_trusted_sources_db()


def get_discovery() -> DiscoveryService:
    """Dependency to get discovery service."""
    return get_discovery_service()


def get_scraper() -> ScraperService:
    """Dependency to get scraper service."""
    return get_scraper_service()


def get_cleaner() -> CleanerService:
    """Dependency to get cleaner service."""
    return get_cleaner_service()


# Discovery & Collection Endpoints
@trusted_sources_router.post("/discover", response_model=DiscoverResponse)
async def discover_urls(
    request: DiscoverRequest,
    discovery: DiscoveryService = Depends(get_discovery)
):
    """Discover sitemap and collect URLs for a domain."""
    try:
        result = discovery.discover_and_collect(request.domain, request.path_filter)
        return DiscoverResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Discovery failed: {str(e)}")


@trusted_sources_router.get("/urls", response_model=List[UrlResponse])
async def get_urls(
    domain: Optional[str] = Query(None, description="Filter by domain"),
    status: Optional[UrlStatus] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=1000, description="Number of URLs to return"),
    offset: int = Query(0, ge=0, description="Number of URLs to skip"),
    db: TrustedSourcesDatabase = Depends(get_db)
):
    """Get URLs with optional filtering and pagination."""
    try:
        return db.get_urls(domain=domain, status=status, limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch URLs: {str(e)}")


@trusted_sources_router.post("/urls", response_model=UrlResponse)
async def create_url(
    url_data: UrlCreate,
    db: TrustedSourcesDatabase = Depends(get_db)
):
    """Create a single URL record."""
    try:
        return db.add_url(url_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create URL: {str(e)}")


@trusted_sources_router.post("/urls/batch", response_model=dict)
async def create_urls_batch(
    urls_data: UrlsCreate,
    db: TrustedSourcesDatabase = Depends(get_db)
):
    """Create multiple URLs from a list."""
    try:
        # Convert URLs to UrlCreate objects
        url_creates = []
        for url in urls_data.urls:
            # Extract domain from URL
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc

            url_create = UrlCreate(url=url, domain=domain)
            url_creates.append(url_create)

        count = db.add_urls_batch(url_creates)
        return {"message": f"Successfully created {count} URLs", "count": count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create URLs: {str(e)}")


# Content Pipeline Endpoints
@trusted_sources_router.post("/scrape", response_model=ScrapeResponse)
async def start_scraping(
    request: ScrapeRequest,
    scraper: ScraperService = Depends(get_scraper),
    db: TrustedSourcesDatabase = Depends(get_db)
):
    """Start background scraping job for a domain."""
    try:
        # Get URL count for the domain
        total_urls = db.count_urls(domain=request.domain, status=UrlStatus.PENDING)

        if total_urls == 0:
            raise HTTPException(
                status_code=404,
                detail=f"No pending URLs found for domain: {request.domain}"
            )

        # Start scraping job
        job_id = scraper.start_scraping_job(request.domain, request.limit)

        return ScrapeResponse(
            job_id=job_id,
            domain=request.domain,
            total_urls=min(total_urls, request.limit) if request.limit else total_urls,
            status="running",
            test_mode=request.limit is not None
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start scraping: {str(e)}")


@trusted_sources_router.post("/clean", response_model=CleanResponse)
async def start_cleaning(
    request: CleanRequest,
    cleaner: CleanerService = Depends(get_cleaner)
):
    """Start background cleaning job for raw content."""
    try:
        # Start cleaning job
        job_id = cleaner.start_cleaning_job(request.domain, request.limit)

        # Get job info to return proper response
        job = cleaner.db.get_job(job_id)

        return CleanResponse(
            job_id=job_id,
            domain=request.domain,
            total_raw_content=job.total_urls if job else 0,
            status="running",
            test_mode=request.limit is not None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start cleaning: {str(e)}")


@trusted_sources_router.post("/retry", response_model=RetryResponse)
async def retry_failed_urls(
    request: RetryRequest,
    scraper: ScraperService = Depends(get_scraper),
    db: TrustedSourcesDatabase = Depends(get_db)
):
    """Retry failed URLs for a domain or specific URLs."""
    try:
        if request.urls:
            # Retry specific URLs
            job_id = scraper.retry_failed_urls(request.domain, request.urls)
            return RetryResponse(retrying=len(request.urls), urls=request.urls)
        elif request.domain:
            # Retry all failed URLs for domain
            failed_count = db.count_urls(domain=request.domain, status=UrlStatus.FAILED)
            if failed_count == 0:
                raise HTTPException(
                    status_code=404,
                    detail=f"No failed URLs found for domain: {request.domain}"
                )

            job_id = scraper.retry_failed_urls(request.domain)
            failed_urls = db.get_urls(domain=request.domain, status=UrlStatus.FAILED, limit=failed_count)
            return RetryResponse(
                retrying=failed_count,
                urls=[url.url for url in failed_urls]
            )
        else:
            raise HTTPException(status_code=400, detail="Must specify either domain or specific URLs")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retry URLs: {str(e)}")


# Status & Monitoring Endpoints
@trusted_sources_router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job_status(
    job_id: str,
    db: TrustedSourcesDatabase = Depends(get_db)
):
    """Get job status and progress."""
    try:
        job = db.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return job
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job: {str(e)}")


@trusted_sources_router.get("/jobs", response_model=List[JobResponse])
async def get_jobs(
    domain: Optional[str] = Query(None, description="Filter by domain"),
    limit: int = Query(50, ge=1, le=100, description="Number of jobs to return"),
    db: TrustedSourcesDatabase = Depends(get_db)
):
    """Get list of jobs with optional domain filtering."""
    try:
        return db.get_jobs(domain=domain, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get jobs: {str(e)}")


# Content Access Endpoints
@trusted_sources_router.get("/content", response_model=List[ContentResponse])
async def get_content(
    domain: Optional[str] = Query(None, description="Filter by domain"),
    limit: int = Query(100, ge=1, le=1000, description="Number of content items to return"),
    offset: int = Query(0, ge=0, description="Number of content items to skip"),
    db: TrustedSourcesDatabase = Depends(get_db)
):
    """Get cleaned content with optional domain filtering."""
    try:
        return db.get_content(domain=domain, limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get content: {str(e)}")


@trusted_sources_router.get("/domains", response_model=List[DomainStats])
async def get_domains(
    db: TrustedSourcesDatabase = Depends(get_db)
):
    """Get domain statistics."""
    try:
        return db.get_domain_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get domain stats: {str(e)}")


# Raw Content Access Endpoints
@trusted_sources_router.get("/raw-content", response_model=List[RawContentListItem])
async def get_raw_content(
    domain: Optional[str] = Query(None, description="Filter by domain"),
    min_size: Optional[int] = Query(None, ge=0, description="Minimum size in bytes"),
    max_size: Optional[int] = Query(None, ge=0, description="Maximum size in bytes (default: 1MB limit)"),
    scraped_after: Optional[datetime] = Query(None, description="Filter content scraped after this date"),
    scraped_before: Optional[datetime] = Query(None, description="Filter content scraped before this date"),
    limit: int = Query(50, ge=1, le=100, description="Number of items to return (max 100)"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    db: TrustedSourcesDatabase = Depends(get_db)
):
    """Get raw content list with filtering and pagination (lightweight, no HTML content)."""
    try:
        # Apply safety limit
        if max_size is None:
            max_size = 1024 * 1024  # 1MB default limit

        return db.get_raw_content(
            domain=domain,
            min_size=min_size,
            max_size=max_size,
            scraped_after=scraped_after,
            scraped_before=scraped_before,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get raw content: {str(e)}")


@trusted_sources_router.get("/raw-content/stats", response_model=RawContentStatsResponse)
async def get_raw_content_stats(
    domain: Optional[str] = Query(None, description="Filter stats by domain"),
    db: TrustedSourcesDatabase = Depends(get_db)
):
    """Get statistics for raw content."""
    try:
        return db.get_raw_content_stats(domain=domain)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get raw content stats: {str(e)}")


@trusted_sources_router.get("/raw-content/{content_id}", response_model=RawContentResponse)
async def get_raw_content_by_id(
    content_id: int,
    response: Response,
    db: TrustedSourcesDatabase = Depends(get_db),
    format: str = Query("json", regex="^(json|html)$", description="Response format: json or html"),
    include_html: bool = Query(True, description="Include full HTML content in response")
):
    """Get specific raw content by ID."""
    try:
        content = db.get_raw_content_by_id(content_id, include_html=include_html)

        if not content:
            raise HTTPException(status_code=404, detail="Raw content not found")

        # Check size safety limit (1MB)
        if content.size_bytes and content.size_bytes > 1024 * 1024:
            if include_html:
                raise HTTPException(
                    status_code=413,
                    detail=f"Content too large ({content.size_bytes} bytes). Use include_html=false for metadata only."
                )

        if format == "html" and content.html:
            # Serve as plain text for security
            response.headers["Content-Type"] = "text/plain; charset=utf-8"
            response.headers["X-Content-Warning"] = "Raw HTML served as plain text for security"
            return Response(content=content.html, media_type="text/plain")

        return content

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get raw content: {str(e)}")


@trusted_sources_router.get("/raw-content/{content_id}/headers", response_model=RawContentHeadersResponse)
async def get_raw_content_headers(
    content_id: int,
    db: TrustedSourcesDatabase = Depends(get_db)
):
    """Get HTTP headers for specific raw content."""
    try:
        headers = db.get_raw_content_headers(content_id)

        if not headers:
            raise HTTPException(status_code=404, detail="Raw content not found")

        return headers

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get raw content headers: {str(e)}")


@trusted_sources_router.get("/raw-content/{raw_content_id}/compare", response_model=ContentComparisonResponse)
async def compare_raw_content(
    raw_content_id: int,
    db: TrustedSourcesDatabase = Depends(get_db)
):
    """Compare raw HTML vs cleaned content for a specific raw content item.

    This endpoint takes a raw content ID and shows the comparison between:
    - The original scraped HTML content
    - The cleaned text version (if it exists)
    - Size reduction statistics and compression ratios
    """
    try:
        comparison = db.get_content_comparison(raw_content_id)

        if not comparison:
            raise HTTPException(
                status_code=404,
                detail="Raw content not found or comparison data unavailable"
            )

        return comparison

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compare content: {str(e)}")


@trusted_sources_router.get("/cleaned-content/{cleaned_content_id}/raw", response_model=ContentComparisonResponse)
async def compare_cleaned_content(
    cleaned_content_id: int,
    db: TrustedSourcesDatabase = Depends(get_db)
):
    """Compare cleaned content vs raw HTML for a specific cleaned content item.

    This endpoint takes a cleaned content ID and shows the comparison between:
    - The cleaned text content
    - The original scraped HTML content
    - Size reduction statistics and compression ratios
    """
    try:
        # First get the cleaned content to find the raw content ID
        cleaned = db.get_cleaned_content_by_id(cleaned_content_id, include_text=False)
        if not cleaned:
            raise HTTPException(status_code=404, detail="Cleaned content not found")

        # Now get the comparison using the raw content ID
        comparison = db.get_content_comparison(cleaned.raw_content_id)

        if not comparison:
            raise HTTPException(
                status_code=404,
                detail="Comparison data unavailable for this cleaned content"
            )

        return comparison

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compare content: {str(e)}")


# Cleaned Content Access Endpoints
@trusted_sources_router.get("/cleaned-content", response_model=List[CleanedContentListItem])
async def get_cleaned_content(
    domain: Optional[str] = Query(None, description="Filter by domain"),
    title_search: Optional[str] = Query(None, description="Search in titles"),
    min_length: Optional[int] = Query(None, ge=0, description="Minimum text length"),
    max_length: Optional[int] = Query(None, ge=0, description="Maximum text length"),
    cleaned_after: Optional[datetime] = Query(None, description="Filter content cleaned after this date"),
    cleaned_before: Optional[datetime] = Query(None, description="Filter content cleaned before this date"),
    limit: int = Query(50, ge=1, le=100, description="Number of items to return (max 100)"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    db: TrustedSourcesDatabase = Depends(get_db)
):
    """Get cleaned content list with comprehensive filtering and pagination (lightweight, no full text)."""
    try:
        return db.get_cleaned_content(
            domain=domain,
            title_search=title_search,
            min_length=min_length,
            max_length=max_length,
            cleaned_after=cleaned_after,
            cleaned_before=cleaned_before,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cleaned content: {str(e)}")


@trusted_sources_router.get("/cleaned-content/stats", response_model=CleanedContentStatsResponse)
async def get_cleaned_content_stats(
    domain: Optional[str] = Query(None, description="Filter stats by domain"),
    db: TrustedSourcesDatabase = Depends(get_db)
):
    """Get comprehensive statistics for cleaned content."""
    try:
        return db.get_cleaned_content_stats(domain=domain)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cleaned content stats: {str(e)}")


@trusted_sources_router.get("/cleaned-content/count", response_model=dict)
async def count_cleaned_content(
    domain: Optional[str] = Query(None, description="Filter by domain"),
    title_search: Optional[str] = Query(None, description="Search in titles"),
    min_length: Optional[int] = Query(None, ge=0, description="Minimum text length"),
    max_length: Optional[int] = Query(None, ge=0, description="Maximum text length"),
    cleaned_after: Optional[datetime] = Query(None, description="Filter content cleaned after this date"),
    cleaned_before: Optional[datetime] = Query(None, description="Filter content cleaned before this date"),
    db: TrustedSourcesDatabase = Depends(get_db)
):
    """Count cleaned content with optional filtering."""
    try:
        count = db.count_cleaned_content(
            domain=domain,
            title_search=title_search,
            min_length=min_length,
            max_length=max_length,
            cleaned_after=cleaned_after,
            cleaned_before=cleaned_before
        )
        return {
            "count": count,
            "filters": {
                "domain": domain,
                "title_search": title_search,
                "min_length": min_length,
                "max_length": max_length,
                "cleaned_after": cleaned_after.isoformat() if cleaned_after else None,
                "cleaned_before": cleaned_before.isoformat() if cleaned_before else None
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to count cleaned content: {str(e)}")


@trusted_sources_router.get("/cleaned-content/search", response_model=List[CleanedContentSearchResponse])
async def search_cleaned_content(
    q: str = Query(..., description="Search query for titles and content"),
    domain: Optional[str] = Query(None, description="Filter by domain"),
    limit: int = Query(50, ge=1, le=100, description="Number of results to return (max 100)"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: TrustedSourcesDatabase = Depends(get_db)
):
    """Search cleaned content by title and text content with highlighting."""
    try:
        if len(q.strip()) < 2:
            raise HTTPException(status_code=400, detail="Search query must be at least 2 characters long")

        return db.search_cleaned_content(
            search_query=q.strip(),
            domain=domain,
            limit=limit,
            offset=offset
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search cleaned content: {str(e)}")


@trusted_sources_router.get("/cleaned-content/{content_id}", response_model=CleanedContentResponse)
async def get_cleaned_content_by_id(
    content_id: int,
    response: Response,
    db: TrustedSourcesDatabase = Depends(get_db),
    include_text: bool = Query(True, description="Include full text content in response"),
    format: str = Query("json", regex="^(json|text)$", description="Response format: json or text")
):
    """Get specific cleaned content by ID."""
    try:
        content = db.get_cleaned_content_by_id(content_id, include_text=include_text)

        if not content:
            raise HTTPException(status_code=404, detail="Cleaned content not found")

        if format == "text" and content.text:
            # Serve as plain text
            response.headers["Content-Type"] = "text/plain; charset=utf-8"
            response.headers["X-Content-Title"] = content.title or "No title"
            response.headers["X-Content-URL"] = content.url
            return Response(content=content.text, media_type="text/plain")

        return content

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cleaned content: {str(e)}")


# Health & Setup Endpoints
@trusted_sources_router.get("/health", response_model=dict)
async def health_check(
    db: TrustedSourcesDatabase = Depends(get_db)
):
    """Health check for trusted sources service."""
    try:
        # Test database connection
        total_urls = db.count_urls()
        domains = db.get_domain_stats()

        return {
            "status": "healthy",
            "database": "connected",
            "total_urls": total_urls,
            "total_domains": len(domains),
            "services": ["discovery", "scraper", "cleaner"]
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@trusted_sources_router.post("/setup", response_model=dict)
async def setup_database(
    db: TrustedSourcesDatabase = Depends(get_db)
):
    """Initialize database tables. Use with caution."""
    try:
        db.initialize()
        db.create_tables()
        return {
            "message": "Database setup completed successfully",
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database setup failed: {str(e)}")


# URL Count Endpoint
@trusted_sources_router.get("/urls/count", response_model=dict)
async def count_urls(
    domain: Optional[str] = Query(None, description="Filter by domain"),
    status: Optional[UrlStatus] = Query(None, description="Filter by status"),
    db: TrustedSourcesDatabase = Depends(get_db)
):
    """Count URLs with optional filtering."""
    try:
        count = db.count_urls(domain=domain, status=status)
        return {"count": count, "domain": domain, "status": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to count URLs: {str(e)}")