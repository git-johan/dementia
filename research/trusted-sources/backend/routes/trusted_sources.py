#!/usr/bin/env python3
"""
Minimal Trusted Sources API routes for content pipeline validation.
Ultra-streamlined version with only essential endpoints.
"""

from typing import List, Optional
from datetime import datetime
import logging
from fastapi import APIRouter, HTTPException, Query, Depends, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request

from models.trusted_sources import (
    ScrapeRequest, ScrapeResponse,
    CleanRequest, CleanResponse,
    ExtractRequest, ExtractResponse,
    ConvertRequest, ConvertResponse,
    ProcessRequest, ProcessResponse,
    CrawlRequest, CrawlResponse,
    UrlsCreate, UrlCreate, UrlResponse,
    JobResponse,
    DomainCreate, DomainUpdate, DomainResponse,
    DomainStatus
)
from services.database import get_trusted_sources_db, TrustedSourcesDatabase
from services.scraper import get_scraper_service, ScraperService
from services.cleaner import get_cleaner_service, CleanerService
from services.extraction import get_extraction_service, ExtractionService
from services.markdown_converter import get_markdown_converter_service, MarkdownConverterService
from services.discovery import get_discovery_service, DiscoveryService


# Setup logging
logger = logging.getLogger(__name__)

# Create router
trusted_sources_router = APIRouter()

# Setup templates
templates = Jinja2Templates(directory="templates")


def get_db() -> TrustedSourcesDatabase:
    """Dependency to get database service."""
    return get_trusted_sources_db()


def get_scraper() -> ScraperService:
    """Dependency to get scraper service."""
    return get_scraper_service()


def get_cleaner() -> CleanerService:
    """Dependency to get cleaner service."""
    return get_cleaner_service()


def get_discovery() -> DiscoveryService:
    """Dependency to get discovery service."""
    return get_discovery_service()


def get_extraction() -> ExtractionService:
    """Dependency to get extraction service."""
    return get_extraction_service()


def get_markdown_converter() -> MarkdownConverterService:
    """Dependency to get markdown converter service."""
    return get_markdown_converter_service()


# ============================================================================
# Domain Management Endpoints
# ============================================================================

@trusted_sources_router.get("/domains", response_model=List[DomainResponse])
async def get_domains(
    status: Optional[DomainStatus] = Query(None, description="Filter by domain status"),
    limit: int = Query(100, ge=1, le=500, description="Number of domains to return"),
    offset: int = Query(0, ge=0, description="Number of domains to skip"),
    db: TrustedSourcesDatabase = Depends(get_db)
):
    """Get all domains with optional filtering."""
    try:
        domains = db.get_domains(
            status=status,
            limit=limit,
            offset=offset
        )
        return domains
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get domains: {str(e)}")


@trusted_sources_router.post("/domains", response_model=DomainResponse)
async def create_domain(
    domain_data: DomainCreate,
    db: TrustedSourcesDatabase = Depends(get_db),
    discovery: DiscoveryService = Depends(get_discovery)
):
    """Create a new domain with automatic sitemap discovery."""
    try:
        # Check if domain already exists
        existing = db.get_domain_by_name(domain_data.domain)
        if existing:
            raise HTTPException(status_code=400, detail=f"Domain {domain_data.domain} already exists")

        # Create the domain
        domain_response = db.add_domain(domain_data)

        # Always discover sitemap automatically
        try:
            # Use discovery service to find sitemap
            sitemap_urls = discovery.discover_sitemaps(domain_data.domain)

            if sitemap_urls:
                # Update domain with the first discovered sitemap URL
                update_data = DomainUpdate(sitemap_url=sitemap_urls[0])
                domain_response = db.update_domain(domain_response.id, update_data)

                logger.info(f"✅ Domain {domain_data.domain} created with sitemap: {sitemap_urls[0]}")
            else:
                logger.warning(f"⚠️  Domain {domain_data.domain} created but no sitemap found")

        except Exception as discovery_error:
            # Don't fail domain creation if sitemap discovery fails
            logger.warning(f"⚠️  Domain {domain_data.domain} created but sitemap discovery failed: {discovery_error}")

        return domain_response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create domain {domain_data.domain}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create domain: {str(e)}")


@trusted_sources_router.get("/domains/{domain_name}", response_model=DomainResponse)
async def get_domain(
    domain_name: str,
    db: TrustedSourcesDatabase = Depends(get_db)
):
    """Get a specific domain by name."""
    try:
        domain = db.get_domain_by_name(domain_name)
        if not domain:
            raise HTTPException(status_code=404, detail=f"Domain {domain_name} not found")
        return domain
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get domain: {str(e)}")


@trusted_sources_router.put("/domains/{domain_name}", response_model=DomainResponse)
async def update_domain(
    domain_name: str,
    domain_data: DomainUpdate,
    db: TrustedSourcesDatabase = Depends(get_db)
):
    """Update a domain."""
    try:
        # Get domain by name first
        domain = db.get_domain_by_name(domain_name)
        if not domain:
            raise HTTPException(status_code=404, detail=f"Domain {domain_name} not found")

        # Update using domain ID
        updated_domain = db.update_domain(domain.id, domain_data)
        if not updated_domain:
            raise HTTPException(status_code=404, detail=f"Failed to update domain {domain_name}")

        return updated_domain
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update domain: {str(e)}")


@trusted_sources_router.delete("/domains/{domain_id}")
async def delete_domain(
    domain_id: int,
    db: TrustedSourcesDatabase = Depends(get_db)
):
    """Delete a domain and all its associated URLs."""
    try:
        # Check if domain exists first
        domain = db.get_domain_by_id(domain_id)
        if not domain:
            raise HTTPException(status_code=404, detail=f"Domain with ID {domain_id} not found")

        success = db.delete_domain(domain_id)
        if success:
            return {"message": f"Successfully deleted domain '{domain.domain}' (ID: {domain_id}) and all associated URLs"}
        else:
            raise HTTPException(status_code=500, detail=f"Failed to delete domain with ID {domain_id}")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete domain: {str(e)}")


# ============================================================================
# Core Pipeline Endpoints (7 essential endpoints)
# ============================================================================

@trusted_sources_router.post("/urls", response_model=dict)
async def add_urls(
    urls_data: UrlsCreate,
    db: TrustedSourcesDatabase = Depends(get_db)
):
    """Add multiple URLs to the pipeline for scraping."""
    try:
        added_count = 0
        duplicate_count = 0

        for url in urls_data.urls:
            # Check if URL already exists
            existing_url = db.get_url_by_url(url)
            if existing_url:
                duplicate_count += 1
                continue

            # Extract domain from URL
            from urllib.parse import urlparse
            domain = urlparse(url).netloc

            # Create URL record
            url_data = UrlCreate(url=url, domain=domain)
            db.add_url(url_data)
            added_count += 1

        return {
            "message": f"Processed {len(urls_data.urls)} URLs",
            "added": added_count,
            "duplicates": duplicate_count,
            "urls": urls_data.urls
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add URLs: {str(e)}")


@trusted_sources_router.post("/crawl", response_model=CrawlResponse)
async def start_crawling(
    crawl_data: CrawlRequest,
    discovery: DiscoveryService = Depends(get_discovery),
    db: TrustedSourcesDatabase = Depends(get_db)
):
    """Start unlimited background crawling job to discover and collect ALL URLs from sitemap."""
    try:
        # Check if domain exists
        domain_record = db.get_domain_by_name(crawl_data.domain)
        if not domain_record:
            raise HTTPException(status_code=404, detail=f"Domain {crawl_data.domain} not found. Create domain first.")

        # WARNING: Ignore max_urls limit for complete sitemap discovery
        if crawl_data.max_urls:
            logger.warning(f"⚠️  max_urls limit ({crawl_data.max_urls}) specified but will be ignored for complete discovery")

        # Enhanced discovery with unlimited collection
        result = discovery.discover_and_collect(
            domain=crawl_data.domain,
            path_filter=crawl_data.path_filters[0] if crawl_data.path_filters else None
        )

        # Update domain with crawl results
        if result.get("sitemap_url") and domain_record.sitemap_url != result["sitemap_url"]:
            update_data = DomainUpdate(
                sitemap_url=result["sitemap_url"],
                total_urls_found=result.get("urls_found", 0),
                last_crawled_at=datetime.utcnow()
            )
            db.update_domain(domain_record.id, update_data)

        logger.info(f"🕷️  Unlimited crawl started for {crawl_data.domain}: {result.get('urls_found', 0)} URLs discovered")

        return CrawlResponse(
            job_id=result["job_id"],
            domain=crawl_data.domain,
            sitemap_url=result.get("sitemap_url"),
            status=result.get("status", "running"),
            total_urls_found=result.get("urls_found"),
            path_filters=crawl_data.path_filters
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start unlimited crawling for domain {crawl_data.domain}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to start crawling: {str(e)}")


@trusted_sources_router.post("/scrape", response_model=ScrapeResponse)
async def start_scraping(
    scrape_data: ScrapeRequest,
    scraper: ScraperService = Depends(get_scraper)
):
    """Start background scraping job for a domain."""
    try:
        job_id = scraper.start_scraping_job(scrape_data.domain, scrape_data.limit)

        # Count URLs for this domain
        db = get_trusted_sources_db()
        total_urls = db.count_urls(domain=scrape_data.domain, status="pending")

        return ScrapeResponse(
            job_id=job_id,
            domain=scrape_data.domain,
            total_urls=total_urls,
            status="running",
            test_mode=bool(scrape_data.limit)
        )
    except Exception as e:
        logger.error(f"Failed to start scraping for domain {scrape_data.domain}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to start scraping: {str(e)}")


@trusted_sources_router.post("/clean", response_model=CleanResponse)
async def start_cleaning(
    clean_data: CleanRequest,
    cleaner: CleanerService = Depends(get_cleaner)
):
    """Start background cleaning job for raw content."""
    try:
        job_id = cleaner.start_cleaning_job(clean_data.domain, clean_data.limit)

        # Count raw content for this domain
        db = get_trusted_sources_db()
        # This is a simplified count - in real implementation would count raw content to be cleaned
        total_raw_content = 10  # Placeholder

        return CleanResponse(
            job_id=job_id,
            domain=clean_data.domain,
            total_raw_content=total_raw_content,
            status="running",
            test_mode=bool(clean_data.limit)
        )
    except Exception as e:
        logger.error(f"Failed to start cleaning for domain {clean_data.domain}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to start cleaning: {str(e)}")


# ============================================================================
# Single URL Pipeline Endpoints (NEW)
# ============================================================================

@trusted_sources_router.post("/scrape/{url_id}")
async def scrape_single_url(
    url_id: int,
    scraper: ScraperService = Depends(get_scraper)
):
    """Scrape a single URL by ID - synchronous operation."""
    try:
        result = scraper.scrape_url_direct(url_id)

        if result["success"]:
            logger.info(f"✅ Successfully scraped URL ID {url_id}: {result['content_size']} bytes")
            return {
                "success": True,
                "url_id": url_id,
                "url": result["url"],
                "raw_content_id": result["raw_content_id"],
                "content_size": result["content_size"],
                "status": "completed",
                "message": f"Successfully scraped {result['content_size']} bytes from URL ID {url_id}"
            }
        else:
            logger.error(f"❌ Failed to scrape URL ID {url_id}: {result['error']}")
            raise HTTPException(status_code=400, detail=result["error"])

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to scrape URL ID {url_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to scrape URL: {str(e)}")


@trusted_sources_router.post("/extract/{url_id}")
async def extract_single_url(
    url_id: int,
    extraction: ExtractionService = Depends(get_extraction)
):
    """Extract content from a single URL by ID - synchronous operation."""
    try:
        result = extraction.extract_url_direct(url_id)

        if result["success"]:
            logger.info(f"✅ Successfully extracted URL ID {url_id}: {result['content_length']} chars, score: {result['structure_score']:.2f}")
            return {
                "success": True,
                "url_id": url_id,
                "raw_content_id": result["raw_content_id"],
                "extracted_content_id": result["extracted_content_id"],
                "title": result["title"],
                "content_length": result["content_length"],
                "structure_score": result["structure_score"],
                "metadata": result["metadata"],
                "status": "completed",
                "message": f"Successfully extracted {result['content_length']} characters from URL ID {url_id}"
            }
        else:
            logger.error(f"❌ Failed to extract URL ID {url_id}: {result['error']}")
            raise HTTPException(status_code=400, detail=result["error"])

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to extract URL ID {url_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to extract URL: {str(e)}")


@trusted_sources_router.post("/convert/{url_id}")
async def convert_single_url(
    url_id: int,
    converter: MarkdownConverterService = Depends(get_markdown_converter)
):
    """Convert extracted content to markdown for a single URL by ID - synchronous operation."""
    try:
        result = converter.convert_url_direct(url_id)

        if result["success"]:
            logger.info(f"✅ Successfully converted URL ID {url_id}: {result['markdown_length']} chars, {result['chunk_count']} chunks")
            return {
                "success": True,
                "url_id": url_id,
                "extracted_content_id": result["extracted_content_id"],
                "markdown_content_id": result["markdown_content_id"],
                "title": result["title"],
                "markdown_length": result["markdown_length"],
                "chunk_count": result["chunk_count"],
                "metadata": result["metadata"],
                "status": "completed",
                "message": f"Successfully converted to {result['markdown_length']} characters markdown with {result['chunk_count']} chunks"
            }
        else:
            logger.error(f"❌ Failed to convert URL ID {url_id}: {result['error']}")
            raise HTTPException(status_code=400, detail=result["error"])

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to convert URL ID {url_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to convert URL: {str(e)}")


# ============================================================================
# Batch Processing Pipeline (NEW)
# ============================================================================

@trusted_sources_router.post("/process", response_model=ProcessResponse)
async def start_processing_pipeline(
    process_data: ProcessRequest,
    scraper: ScraperService = Depends(get_scraper),
    extraction: ExtractionService = Depends(get_extraction),
    converter: MarkdownConverterService = Depends(get_markdown_converter),
    db: TrustedSourcesDatabase = Depends(get_db)
):
    """Start full pipeline processing (scrape → extract → convert) for a domain."""
    try:
        # Check if domain exists
        domain = db.get_domain_by_name(process_data.domain)
        if not domain:
            raise HTTPException(status_code=404, detail=f"Domain {process_data.domain} not found")

        # Generate master job ID for the pipeline
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pipeline_job_id = f"pipeline_{process_data.domain}_{timestamp}"

        # Count URLs to process
        total_urls = db.count_urls(domain=process_data.domain, status="pending")

        if total_urls == 0:
            raise HTTPException(status_code=400, detail=f"No pending URLs found for domain {process_data.domain}")

        # Apply limit if in test mode
        actual_total = min(total_urls, process_data.limit) if process_data.limit else total_urls
        test_mode = bool(process_data.limit)

        # Create pipeline job record
        db.create_job(pipeline_job_id, process_data.domain, JobType.PROCESS, actual_total, process_data.limit)

        # Start the pipeline (scraping first, then extract and convert will be triggered by job completion)
        scraping_job_id = scraper.start_scraping_job(process_data.domain, process_data.limit)

        logger.info(f"🚀 Started processing pipeline {pipeline_job_id} for {process_data.domain} with {actual_total} URLs")

        return ProcessResponse(
            job_id=pipeline_job_id,
            domain=process_data.domain,
            total_urls=actual_total,
            status=JobStatus.RUNNING,
            pipeline_stages=["scrape", "extract", "convert"],
            test_mode=test_mode
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start processing pipeline for domain {process_data.domain}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to start processing pipeline: {str(e)}")


@trusted_sources_router.get("/urls", response_class=HTMLResponse)
async def get_urls_interface(
    request: Request,
    domain: Optional[str] = Query(None, description="Filter URLs by domain"),
    status: Optional[str] = Query(None, description="Filter URLs by status"),
    job_id: Optional[str] = Query(None, description="Show specific job details"),
    limit: int = Query(100, ge=1, le=500, description="Number of URLs to return"),
    offset: int = Query(0, ge=0, description="Number of URLs to skip"),
    db: TrustedSourcesDatabase = Depends(get_db)
):
    """Main interface showing all URLs with links to raw and cleaned content, plus job status."""
    try:
        urls = db.get_urls(
            domain=domain,
            status=status,
            limit=limit,
            offset=offset
        )

        # Get quick stats
        total_urls = db.count_urls(domain=domain, status=status)

        # Get recent/running jobs (last 20)
        recent_jobs = db.get_jobs(limit=20)

        # Get specific job details if requested
        specific_job = None
        if job_id:
            specific_job = db.get_job(job_id)

        # Get available domains for filter dropdown (only show domains with URLs)
        all_domains = db.get_domains(status=DomainStatus.ACTIVE, limit=100)
        available_domains = [d for d in all_domains if d.total_urls_found > 0]

        return templates.TemplateResponse("urls_interface.html", {
            "request": request,
            "urls": urls,
            "total_urls": total_urls,
            "recent_jobs": recent_jobs,
            "specific_job": specific_job,
            "available_domains": available_domains,
            "current_domain": domain,
            "current_status": status,
            "current_job_id": job_id,
            "limit": limit,
            "offset": offset
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get URLs: {str(e)}")


# ============================================================================
# Administrative Endpoints
# ============================================================================

@trusted_sources_router.delete("/admin/reset-database")
async def reset_entire_database(
    confirm: bool = Query(False, description="Set to true to confirm complete database reset"),
    db: TrustedSourcesDatabase = Depends(get_db)
):
    """
    ADMIN: DANGER - Completely reset the entire database.
    This deletes ALL data: domains, URLs, content, jobs.
    """
    if not confirm:
        return {
            "message": "⚠️  DANGER: This will DELETE ALL DATA from the database.",
            "warning": "Add ?confirm=true to the URL to proceed with COMPLETE RESET.",
            "affected_tables": ["domains", "urls", "raw_content", "clean_content", "extracted_content", "markdown_content", "scrape_jobs"],
            "recommendation": "Only use this for testing purposes"
        }

    try:
        with db.get_session() as session:
            from models.trusted_sources import (
                CleanContent, ExtractedContent, MarkdownContent,
                RawContent, UrlRecord, ScrapeJob, DomainRecord
            )

            # Count records before deletion
            counts_before = {
                "markdown_content": session.query(MarkdownContent).count(),
                "extracted_content": session.query(ExtractedContent).count(),
                "clean_content": session.query(CleanContent).count(),
                "raw_content": session.query(RawContent).count(),
                "scrape_jobs": session.query(ScrapeJob).count(),
                "urls": session.query(UrlRecord).count(),
                "domains": session.query(DomainRecord).count(),
            }

            # Delete in proper order (respecting foreign keys)
            session.query(MarkdownContent).delete()
            session.query(ExtractedContent).delete()
            session.query(CleanContent).delete()
            session.query(RawContent).delete()
            session.query(ScrapeJob).delete()
            session.query(UrlRecord).delete()
            session.query(DomainRecord).delete()
            session.commit()

            total_deleted = sum(counts_before.values())
            logger.info(f"🗑️  ADMIN: Complete database reset - deleted {total_deleted} records")

            return {
                "status": "success",
                "message": f"Successfully deleted ALL {total_deleted} records from database",
                "deleted_counts": counts_before,
                "next_steps": [
                    "1. Add domains from trusted_domains.json",
                    "2. Test crawling for each domain",
                    "3. Test pipeline stages systematically"
                ]
            }

    except Exception as e:
        logger.error(f"Failed to reset database: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to reset database: {str(e)}")


@trusted_sources_router.delete("/admin/reset-content")
async def reset_content_for_new_pipeline(
    confirm: bool = Query(False, description="Set to true to confirm deletion"),
    db: TrustedSourcesDatabase = Depends(get_db)
):
    """
    ADMIN: Delete all existing cleaned content for clean slate.
    This prepares the system for the new extraction/markdown pipeline.
    """
    if not confirm:
        return {
            "message": "This will DELETE ALL cleaned content from the database.",
            "warning": "Add ?confirm=true to the URL to proceed with deletion.",
            "affected_tables": ["clean_content"],
            "recommendation": "Use this endpoint to prepare for the new extraction/markdown pipeline"
        }

    try:
        with db.get_session() as session:
            from models.trusted_sources import CleanContent

            # Count existing records before deletion
            count_before = session.query(CleanContent).count()

            # Delete all cleaned content
            session.query(CleanContent).delete()
            session.commit()

            logger.info(f"🗑️  ADMIN: Deleted {count_before} cleaned content records for pipeline migration")

            return {
                "status": "success",
                "message": f"Successfully deleted {count_before} cleaned content records",
                "next_steps": [
                    "1. Test new extraction pipeline with POST /extract",
                    "2. Test new markdown conversion with POST /convert",
                    "3. Use POST /process for full pipeline processing"
                ]
            }

    except Exception as e:
        logger.error(f"Failed to reset content: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to reset content: {str(e)}")


@trusted_sources_router.get("/admin/pipeline-status")
async def get_pipeline_status(
    db: TrustedSourcesDatabase = Depends(get_db)
):
    """
    ADMIN: Get comprehensive pipeline status for migration monitoring.
    """
    try:
        with db.get_session() as session:
            from models.trusted_sources import (
                UrlRecord, RawContent, CleanContent,
                ExtractedContent, MarkdownContent, UrlStatus
            )

            # URL status distribution
            url_stats = session.execute(text("""
                SELECT status, COUNT(*) as count
                FROM urls
                GROUP BY status
                ORDER BY count DESC
            """)).fetchall()

            # Content processing stats
            content_stats = {
                "raw_content": session.query(RawContent).count(),
                "old_clean_content": session.query(CleanContent).count(),
                "new_extracted_content": session.query(ExtractedContent).count(),
                "new_markdown_content": session.query(MarkdownContent).count(),
            }

            # Recent job activity
            recent_jobs = db.get_jobs(limit=10)

            return {
                "url_status_distribution": [{"status": row.status, "count": row.count} for row in url_stats],
                "content_processing_stats": content_stats,
                "recent_jobs": [
                    {
                        "job_id": job.id,
                        "job_type": job.job_type,
                        "status": job.status,
                        "domain": job.domain,
                        "started_at": job.started_at,
                        "processed_count": job.processed_count,
                        "failed_count": job.failed_count
                    } for job in recent_jobs
                ],
                "pipeline_readiness": {
                    "extraction_ready": content_stats["raw_content"] > 0,
                    "conversion_ready": content_stats["new_extracted_content"] > 0,
                    "migration_recommended": content_stats["old_clean_content"] > 0
                }
            }

    except Exception as e:
        logger.error(f"Failed to get pipeline status: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get pipeline status: {str(e)}")


@trusted_sources_router.post("/admin/populate-domains")
async def populate_domains_from_config(
    db: TrustedSourcesDatabase = Depends(get_db),
    discovery: DiscoveryService = Depends(get_discovery)
):
    """
    ADMIN: Populate domains from trusted_domains.json configuration file.
    This adds all Norwegian health authorities and international sources.
    """
    try:
        import json
        import os

        # Load trusted domains configuration
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "trusted_domains.json")

        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        results = {
            "domains_added": [],
            "domains_failed": [],
            "sitemap_discovery": [],
            "total_processed": 0
        }

        # Process Norwegian health authorities
        for domain, info in config["norwegian_health_authorities"].items():
            try:
                results["total_processed"] += 1

                # Create domain
                domain_data = DomainCreate(
                    domain=domain,
                    status=DomainStatus.ACTIVE,
                    default_path_filters=info.get("path_filters", [])
                )

                # Check if domain already exists
                existing = db.get_domain_by_name(domain)
                if existing:
                    results["domains_failed"].append({
                        "domain": domain,
                        "error": "Domain already exists",
                        "info": info
                    })
                    continue

                # Add domain
                domain_response = db.add_domain(domain_data)

                # Try to discover sitemap
                sitemap_result = {"domain": domain, "sitemap_found": False}
                try:
                    sitemap_urls = discovery.discover_sitemaps(domain)
                    if sitemap_urls:
                        # Use the first discovered sitemap URL
                        sitemap_url = sitemap_urls[0]
                        update_data = DomainUpdate(sitemap_url=sitemap_url)
                        db.update_domain(domain_response.id, update_data)
                        sitemap_result["sitemap_found"] = True
                        sitemap_result["sitemap_url"] = sitemap_url
                        sitemap_result["total_sitemaps"] = len(sitemap_urls)
                except Exception as sitemap_error:
                    sitemap_result["sitemap_error"] = str(sitemap_error)

                results["sitemap_discovery"].append(sitemap_result)
                results["domains_added"].append({
                    "domain": domain,
                    "category": info.get("priority", "unknown"),
                    "description": info.get("description", ""),
                    "language": info.get("language", "norwegian"),
                    "focus": info.get("focus", "")
                })

                logger.info(f"✅ Added Norwegian domain: {domain}")

            except Exception as e:
                results["domains_failed"].append({
                    "domain": domain,
                    "error": str(e),
                    "info": info
                })
                logger.error(f"❌ Failed to add domain {domain}: {e}")

        # Process international sources
        for domain, info in config["international_sources"].items():
            try:
                results["total_processed"] += 1

                # Create domain
                domain_data = DomainCreate(
                    domain=domain,
                    status=DomainStatus.ACTIVE,
                    default_path_filters=info.get("path_filters", [])
                )

                # Check if domain already exists
                existing = db.get_domain_by_name(domain)
                if existing:
                    results["domains_failed"].append({
                        "domain": domain,
                        "error": "Domain already exists",
                        "info": info
                    })
                    continue

                # Add domain
                domain_response = db.add_domain(domain_data)

                # Try to discover sitemap
                sitemap_result = {"domain": domain, "sitemap_found": False}
                try:
                    sitemap_urls = discovery.discover_sitemaps(domain)
                    if sitemap_urls:
                        # Use the first discovered sitemap URL
                        sitemap_url = sitemap_urls[0]
                        update_data = DomainUpdate(sitemap_url=sitemap_url)
                        db.update_domain(domain_response.id, update_data)
                        sitemap_result["sitemap_found"] = True
                        sitemap_result["sitemap_url"] = sitemap_url
                        sitemap_result["total_sitemaps"] = len(sitemap_urls)
                except Exception as sitemap_error:
                    sitemap_result["sitemap_error"] = str(sitemap_error)

                results["sitemap_discovery"].append(sitemap_result)
                results["domains_added"].append({
                    "domain": domain,
                    "category": info.get("priority", "unknown"),
                    "description": info.get("description", ""),
                    "language": info.get("language", "english"),
                    "focus": info.get("focus", "")
                })

                logger.info(f"✅ Added international domain: {domain}")

            except Exception as e:
                results["domains_failed"].append({
                    "domain": domain,
                    "error": str(e),
                    "info": info
                })
                logger.error(f"❌ Failed to add domain {domain}: {e}")

        logger.info(f"📊 Domain population complete: {len(results['domains_added'])} added, {len(results['domains_failed'])} failed")

        return {
            "status": "completed",
            "summary": {
                "total_processed": results["total_processed"],
                "domains_added": len(results["domains_added"]),
                "domains_failed": len(results["domains_failed"]),
                "sitemaps_found": sum(1 for s in results["sitemap_discovery"] if s.get("sitemap_found", False))
            },
            "details": results,
            "next_steps": [
                "1. Check GET /domains to verify all domains are created",
                "2. Use POST /crawl for each domain to discover URLs",
                "3. Test pipeline stages on discovered URLs"
            ]
        }

    except Exception as e:
        logger.error(f"Failed to populate domains: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to populate domains: {str(e)}")


@trusted_sources_router.post("/admin/test-pipeline")
async def test_pipeline_systematically(
    domain: Optional[str] = Query(None, description="Test specific domain, or all if not specified"),
    urls_per_domain: int = Query(3, ge=1, le=10, description="Number of URLs to test per domain"),
    stages: List[str] = Query(["crawl", "scrape", "extract", "convert"], description="Pipeline stages to test"),
    db: TrustedSourcesDatabase = Depends(get_db),
    discovery: DiscoveryService = Depends(get_discovery),
    scraper: ScraperService = Depends(get_scraper),
    extraction: ExtractionService = Depends(get_extraction),
    converter: MarkdownConverterService = Depends(get_markdown_converter)
):
    """
    ADMIN: Systematically test the entire pipeline for domains.
    This will crawl URLs and test each stage of the pipeline.
    """
    try:
        import asyncio
        import time

        results = {
            "test_started_at": datetime.utcnow(),
            "domains_tested": [],
            "overall_stats": {
                "total_domains": 0,
                "crawl_success": 0,
                "scrape_success": 0,
                "extract_success": 0,
                "convert_success": 0
            },
            "detailed_results": {}
        }

        # Get domains to test
        if domain:
            # Test specific domain
            domain_record = db.get_domain_by_name(domain)
            if not domain_record:
                raise HTTPException(status_code=404, detail=f"Domain {domain} not found")
            domains_to_test = [domain_record]
        else:
            # Test all active domains
            domains_to_test = db.get_domains(status=DomainStatus.ACTIVE, limit=100)

        results["overall_stats"]["total_domains"] = len(domains_to_test)

        for domain_record in domains_to_test:
            domain_name = domain_record.domain
            domain_results = {
                "domain_info": {
                    "name": domain_name,
                    "category": domain_record.category,
                    "status": domain_record.status
                },
                "stages": {},
                "url_tests": [],
                "errors": []
            }

            logger.info(f"🧪 Testing domain: {domain_name}")

            # Stage 1: Crawl (if requested)
            if "crawl" in stages:
                try:
                    logger.info(f"🕷️  Crawling {domain_name}")
                    crawl_request = CrawlRequest(domain=domain_name, path_filters=[], overwrite_existing=True)
                    crawl_result = discovery.discover_and_collect(
                        domain=domain_name,
                        path_filter=None
                    )

                    domain_results["stages"]["crawl"] = {
                        "success": True,
                        "job_id": crawl_result.get("job_id"),
                        "urls_found": crawl_result.get("urls_found", 0),
                        "sitemap_url": crawl_result.get("sitemap_url")
                    }
                    results["overall_stats"]["crawl_success"] += 1

                    # Wait a bit for crawling to complete
                    await asyncio.sleep(2)

                except Exception as e:
                    domain_results["stages"]["crawl"] = {"success": False, "error": str(e)}
                    domain_results["errors"].append(f"Crawl failed: {str(e)}")

            # Get URLs to test for this domain
            domain_urls = db.get_urls(domain=domain_name, limit=urls_per_domain * 2, status="pending")
            if not domain_urls:
                domain_results["errors"].append("No URLs found for testing after crawl")
                results["detailed_results"][domain_name] = domain_results
                continue

            # Select test URLs
            test_urls = domain_urls[:urls_per_domain]

            for i, url_record in enumerate(test_urls):
                url_test_result = {
                    "url_id": url_record.id,
                    "url": url_record.url,
                    "stages": {}
                }

                logger.info(f"  🔗 Testing URL {i+1}/{len(test_urls)}: {url_record.url}")

                # Stage 2: Scrape (if requested)
                if "scrape" in stages:
                    try:
                        scrape_job_id = scraper.start_scraping_job(domain_name, limit=1)
                        url_test_result["stages"]["scrape"] = {
                            "success": True,
                            "job_id": scrape_job_id
                        }

                        # Wait for scraping
                        await asyncio.sleep(3)

                        # Check if raw content was created
                        raw_content = db.get_raw_content_by_url_id(url_record.id)
                        if raw_content:
                            url_test_result["stages"]["scrape"]["has_content"] = True
                            url_test_result["stages"]["scrape"]["content_size"] = len(raw_content.html) if raw_content.html else 0
                            results["overall_stats"]["scrape_success"] += 1
                        else:
                            url_test_result["stages"]["scrape"]["has_content"] = False

                    except Exception as e:
                        url_test_result["stages"]["scrape"] = {"success": False, "error": str(e)}

                # Stage 3: Extract (if requested)
                if "extract" in stages:
                    try:
                        extract_job_id = extraction.start_extraction_job(url_id=url_record.id)
                        url_test_result["stages"]["extract"] = {
                            "success": True,
                            "job_id": extract_job_id
                        }

                        # Wait for extraction
                        await asyncio.sleep(2)

                        # Check if extracted content was created
                        extracted_content = db.get_extracted_content_by_url_id(url_record.id)
                        if extracted_content:
                            url_test_result["stages"]["extract"]["has_content"] = True
                            url_test_result["stages"]["extract"]["structure_score"] = extracted_content.structure_score
                            url_test_result["stages"]["extract"]["has_tables"] = extracted_content.has_tables
                            url_test_result["stages"]["extract"]["has_lists"] = extracted_content.has_lists
                            results["overall_stats"]["extract_success"] += 1
                        else:
                            url_test_result["stages"]["extract"]["has_content"] = False

                    except Exception as e:
                        url_test_result["stages"]["extract"] = {"success": False, "error": str(e)}

                # Stage 4: Convert (if requested)
                if "convert" in stages:
                    try:
                        convert_job_id = converter.start_conversion_job(url_id=url_record.id)
                        url_test_result["stages"]["convert"] = {
                            "success": True,
                            "job_id": convert_job_id
                        }

                        # Wait for conversion
                        await asyncio.sleep(2)

                        # Check if markdown content was created
                        markdown_content = db.get_markdown_content_by_url_id(url_record.id)
                        if markdown_content:
                            url_test_result["stages"]["convert"]["has_content"] = True
                            url_test_result["stages"]["convert"]["chunk_count"] = markdown_content.chunk_count
                            url_test_result["stages"]["convert"]["has_metadata"] = markdown_content.has_metadata
                            results["overall_stats"]["convert_success"] += 1
                        else:
                            url_test_result["stages"]["convert"]["has_content"] = False

                    except Exception as e:
                        url_test_result["stages"]["convert"] = {"success": False, "error": str(e)}

                domain_results["url_tests"].append(url_test_result)

            results["detailed_results"][domain_name] = domain_results
            results["domains_tested"].append(domain_name)

        results["test_completed_at"] = datetime.utcnow()
        results["test_duration_seconds"] = (results["test_completed_at"] - results["test_started_at"]).total_seconds()

        logger.info(f"🎯 Pipeline testing complete: {len(results['domains_tested'])} domains tested")

        return results

    except Exception as e:
        logger.error(f"Failed to run pipeline test: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to run pipeline test: {str(e)}")


@trusted_sources_router.post("/admin/recreate-schema")
async def recreate_database_schema(
    confirm: bool = Query(False, description="Set to true to confirm schema recreation"),
    db: TrustedSourcesDatabase = Depends(get_db)
):
    """
    ADMIN: DANGER - Drop and recreate all database tables.
    This will create tables with the current model schema.
    """
    if not confirm:
        return {
            "message": "⚠️  DANGER: This will DROP and RECREATE all database tables.",
            "warning": "Add ?confirm=true to the URL to proceed with schema recreation.",
            "note": "This will create tables matching the current code models (without category)"
        }

    try:
        from models.trusted_sources import Base
        from sqlalchemy import text

        # Get the engine from the database service
        db.initialize()
        engine = db.engine

        # Drop all tables
        Base.metadata.drop_all(bind=engine)

        # Recreate all tables
        Base.metadata.create_all(bind=engine)

        logger.info("📊 ADMIN: Database schema recreated successfully")

        return {
            "status": "success",
            "message": "Database schema recreated successfully",
            "note": "All tables now match current model definitions (without category column)",
            "next_steps": [
                "1. Add domains from trusted_domains.json",
                "2. Test crawling and pipeline"
            ]
        }

    except Exception as e:
        logger.error(f"Failed to recreate schema: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to recreate schema: {str(e)}")


@trusted_sources_router.get("/health", response_model=dict)
async def health_check(
    db: TrustedSourcesDatabase = Depends(get_db)
):
    """Simple health check endpoint."""
    try:
        # Test database connection
        total_urls = db.count_urls()

        return {
            "status": "healthy",
            "timestamp": datetime.utcnow(),
            "database": "connected",
            "total_urls": total_urls
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow(),
            "error": str(e)
        }


# ============================================================================
# Content Viewer Endpoints (2 additional endpoints)
# ============================================================================

@trusted_sources_router.get("/urls/{url_id}/raw", response_class=HTMLResponse)
async def view_raw_content(
    request: Request,
    url_id: int,
    db: TrustedSourcesDatabase = Depends(get_db)
):
    """View raw scraped content for a specific URL."""
    try:
        # Get URL record
        url_record = db.get_url_by_id(url_id)
        if not url_record:
            raise HTTPException(status_code=404, detail="URL not found")

        # Get raw content for this URL
        raw_content = db.get_raw_content_by_url_id(url_id)
        if not raw_content:
            raise HTTPException(status_code=404, detail="No raw content found for this URL")

        return templates.TemplateResponse("raw_content.html", {
            "request": request,
            "url_record": url_record,
            "raw_content": raw_content
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get raw content: {str(e)}")


@trusted_sources_router.get("/urls/{url_id}/cleaned", response_class=HTMLResponse)
async def view_cleaned_content(
    request: Request,
    url_id: int,
    db: TrustedSourcesDatabase = Depends(get_db)
):
    """View cleaned content for a specific URL."""
    try:
        # Get URL record
        url_record = db.get_url_by_id(url_id)
        if not url_record:
            raise HTTPException(status_code=404, detail="URL not found")

        # Get cleaned content for this URL
        cleaned_content = db.get_cleaned_content_by_url_id(url_id)
        if not cleaned_content:
            raise HTTPException(status_code=404, detail="No cleaned content found for this URL")

        return templates.TemplateResponse("cleaned_content.html", {
            "request": request,
            "url_record": url_record,
            "cleaned_content": cleaned_content
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cleaned content: {str(e)}")


@trusted_sources_router.get("/urls/{url_id}/extracted", response_class=HTMLResponse)
async def view_extracted_content(
    request: Request,
    url_id: int,
    db: TrustedSourcesDatabase = Depends(get_db)
):
    """View extracted content for a specific URL."""
    try:
        # Get URL record
        url_record = db.get_url_by_id(url_id)
        if not url_record:
            raise HTTPException(status_code=404, detail="URL not found")

        # Get extracted content for this URL
        extracted_content = db.get_extracted_content_by_url_id(url_id)
        if not extracted_content:
            raise HTTPException(status_code=404, detail="No extracted content found for this URL")

        return templates.TemplateResponse("extracted_content.html", {
            "request": request,
            "url_record": url_record,
            "extracted_content": extracted_content
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get extracted content: {str(e)}")


@trusted_sources_router.get("/urls/{url_id}/markdown", response_class=HTMLResponse)
async def view_markdown_content(
    request: Request,
    url_id: int,
    db: TrustedSourcesDatabase = Depends(get_db)
):
    """View markdown content for a specific URL."""
    try:
        # Get URL record
        url_record = db.get_url_by_id(url_id)
        if not url_record:
            raise HTTPException(status_code=404, detail="URL not found")

        # Get markdown content for this URL
        markdown_content = db.get_markdown_content_by_url_id(url_id)
        if not markdown_content:
            raise HTTPException(status_code=404, detail="No markdown content found for this URL")

        return templates.TemplateResponse("markdown_content.html", {
            "request": request,
            "url_record": url_record,
            "markdown_content": markdown_content
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get markdown content: {str(e)}")