#!/usr/bin/env python3
"""
Initialize database with new domains-first schema.
"""

from services.database import get_trusted_sources_db
from models.trusted_sources import DomainCategory, DomainCreate

def main():
    print("🔄 Initializing database with new schema...")

    # Get database service and create tables
    db = get_trusted_sources_db()
    db.create_tables()

    print("✅ Database tables created successfully!")

    # Add some initial trusted domains
    print("🔄 Adding initial trusted domains...")

    domains_to_add = [
        {
            "domain": "fhi.no",
            "category": DomainCategory.GOVERNMENT,
            "sitemap_url": "https://www.fhi.no/sitemap.xml"
        },
        {
            "domain": "helsedirektoratet.no",
            "category": DomainCategory.GOVERNMENT,
            "sitemap_url": "https://www.helsedirektoratet.no/sitemap.xml"
        },
        {
            "domain": "alzheimer-europe.org",
            "category": DomainCategory.MEDICAL_ORG,
            "sitemap_url": "https://www.alzheimer-europe.org/sitemap.xml"
        },
        {
            "domain": "www.alzheimer-europe.org",
            "category": DomainCategory.MEDICAL_ORG,
            "sitemap_url": "https://www.alzheimer-europe.org/sitemap.xml"
        },
        {
            "domain": "nasjonalforeningen.no",
            "category": DomainCategory.ADVOCACY,
        }
    ]

    for domain_data in domains_to_add:
        try:
            domain_create = DomainCreate(**domain_data)
            domain = db.add_domain(domain_create)
            print(f"   ✓ Added domain: {domain.domain} ({domain.category.value})")
        except Exception as e:
            print(f"   ⚠️  Failed to add {domain_data['domain']}: {e}")

    print("\n🎉 Database initialization complete!")
    print("   You can now use the crawl API to discover URLs from these domains.")

if __name__ == "__main__":
    main()