#!/usr/bin/env python3
"""
Clean up duplicate www domains.
"""

from services.database import get_trusted_sources_db

def main():
    print("🔄 Cleaning up duplicate www domains...")

    db = get_trusted_sources_db()

    # Get all domains
    domains = db.get_domains(limit=100)

    print("Current domains:")
    for domain in domains:
        print(f"  ID {domain.id}: {domain.domain} - {domain.total_urls_found} URLs")

    # Delete the www.alzheimer-europe.org domain (should be ID 4 with 0 URLs)
    www_domain = None
    for domain in domains:
        if domain.domain == "www.alzheimer-europe.org" and domain.total_urls_found == 0:
            www_domain = domain
            break

    if www_domain:
        print(f"\n🗑️  Deleting duplicate domain: {www_domain.domain} (ID: {www_domain.id})")
        success = db.delete_domain(www_domain.id)
        if success:
            print("   ✅ Successfully deleted duplicate domain")
        else:
            print("   ❌ Failed to delete domain")
    else:
        print("\n⚠️  No duplicate www.alzheimer-europe.org domain found")

    print("\n🎉 Domain cleanup complete!")

if __name__ == "__main__":
    main()