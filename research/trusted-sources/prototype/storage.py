"""
Simple SQLite storage for trusted sources research
"""
import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class CollectedContent:
    """Data class for collected content"""
    url: str
    domain: str
    title: str
    content: str
    raw_html: str
    metadata: Dict[str, Any]
    collection_date: str
    content_hash: str
    quality_score: float = 0.0


class TrustedSourcesStorage:
    """SQLite storage for research data"""

    def __init__(self, db_path: Path = None):
        if db_path is None:
            db_path = Path(__file__).parent.parent / "data" / "research.db"

        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger("trusted-sources.storage")

        self._initialize_database()

    def _initialize_database(self):
        """Initialize SQLite database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Content table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS collected_content (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL UNIQUE,
                    domain TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    raw_html TEXT,
                    metadata TEXT,  -- JSON string
                    collection_date TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    quality_score REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Collection jobs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS collection_jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    domain TEXT NOT NULL,
                    status TEXT NOT NULL,  -- pending, running, completed, failed
                    pages_collected INTEGER DEFAULT 0,
                    total_pages INTEGER,
                    start_time TEXT,
                    end_time TEXT,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Quality metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS quality_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_id INTEGER NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (content_id) REFERENCES collected_content (id)
                )
            """)

            conn.commit()
            self.logger.info(f"Database initialized at {self.db_path}")

    def store_content(self, content: CollectedContent) -> int:
        """Store collected content, return content ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            try:
                cursor.execute("""
                    INSERT INTO collected_content (
                        url, domain, title, content, raw_html, metadata,
                        collection_date, content_hash, quality_score
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    content.url,
                    content.domain,
                    content.title,
                    content.content,
                    content.raw_html,
                    json.dumps(content.metadata),
                    content.collection_date,
                    content.content_hash,
                    content.quality_score
                ))

                content_id = cursor.lastrowid
                self.logger.info(f"Stored content from {content.url} with ID {content_id}")
                return content_id

            except sqlite3.IntegrityError:
                # URL already exists, update instead
                cursor.execute("""
                    UPDATE collected_content
                    SET title = ?, content = ?, raw_html = ?, metadata = ?,
                        collection_date = ?, content_hash = ?, quality_score = ?
                    WHERE url = ?
                """, (
                    content.title, content.content, content.raw_html,
                    json.dumps(content.metadata), content.collection_date,
                    content.content_hash, content.quality_score, content.url
                ))

                cursor.execute("SELECT id FROM collected_content WHERE url = ?", (content.url,))
                content_id = cursor.fetchone()[0]
                self.logger.info(f"Updated existing content from {content.url} with ID {content_id}")
                return content_id

    def get_content_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """Get all content for a specific domain"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM collected_content
                WHERE domain = ?
                ORDER BY collection_date DESC
            """, (domain,))

            return [dict(row) for row in cursor.fetchall()]

    def get_content_by_quality(self, min_quality: float = 0.7) -> List[Dict[str, Any]]:
        """Get content above quality threshold"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM collected_content
                WHERE quality_score >= ?
                ORDER BY quality_score DESC, collection_date DESC
            """, (min_quality,))

            return [dict(row) for row in cursor.fetchall()]

    def check_duplicate_content(self, content_hash: str) -> bool:
        """Check if content with this hash already exists"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT COUNT(*) FROM collected_content WHERE content_hash = ?
            """, (content_hash,))

            count = cursor.fetchone()[0]
            return count > 0

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Total content count
            cursor.execute("SELECT COUNT(*) FROM collected_content")
            total_content = cursor.fetchone()[0]

            # Content by domain
            cursor.execute("""
                SELECT domain, COUNT(*) as count
                FROM collected_content
                GROUP BY domain
                ORDER BY count DESC
            """)
            content_by_domain = {row[0]: row[1] for row in cursor.fetchall()}

            # Quality distribution
            cursor.execute("""
                SELECT
                    COUNT(CASE WHEN quality_score >= 0.8 THEN 1 END) as high_quality,
                    COUNT(CASE WHEN quality_score >= 0.6 AND quality_score < 0.8 THEN 1 END) as medium_quality,
                    COUNT(CASE WHEN quality_score < 0.6 THEN 1 END) as low_quality
                FROM collected_content
            """)
            quality_stats = cursor.fetchone()

            return {
                "total_content": total_content,
                "content_by_domain": content_by_domain,
                "quality_distribution": {
                    "high_quality": quality_stats[0],
                    "medium_quality": quality_stats[1],
                    "low_quality": quality_stats[2]
                }
            }

    def create_collection_job(self, domain: str, total_pages: int = None) -> int:
        """Create a new collection job and return job ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO collection_jobs (domain, status, total_pages, start_time)
                VALUES (?, ?, ?, ?)
            """, (domain, "pending", total_pages, datetime.now().isoformat()))

            job_id = cursor.lastrowid
            self.logger.info(f"Created collection job {job_id} for domain {domain}")
            return job_id

    def update_collection_job(self, job_id: int, status: str, pages_collected: int = None, error_message: str = None):
        """Update collection job status"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            update_fields = ["status = ?"]
            params = [status]

            if pages_collected is not None:
                update_fields.append("pages_collected = ?")
                params.append(pages_collected)

            if error_message is not None:
                update_fields.append("error_message = ?")
                params.append(error_message)

            if status in ["completed", "failed"]:
                update_fields.append("end_time = ?")
                params.append(datetime.now().isoformat())

            params.append(job_id)

            cursor.execute(f"""
                UPDATE collection_jobs
                SET {', '.join(update_fields)}
                WHERE id = ?
            """, params)

            self.logger.info(f"Updated collection job {job_id} to status {status}")

    def export_content(self, format: str = "json", min_quality: float = 0.0) -> str:
        """Export collected content in specified format"""
        content = self.get_content_by_quality(min_quality)

        if format == "json":
            return json.dumps(content, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"Unsupported export format: {format}")