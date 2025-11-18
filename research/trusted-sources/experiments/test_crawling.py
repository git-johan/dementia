#!/usr/bin/env python3
"""
Experiment: Test different crawling approaches for Norwegian health sites
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prototype.config import TrustedSourcesConfig
from prototype.storage import TrustedSourcesStorage
from prototype.collector import ContentCollector


def test_single_domain_collection():
    """Test collection from a single high-priority Norwegian domain"""
    print("=== Single Domain Collection Test ===")

    config = TrustedSourcesConfig()
    storage = TrustedSourcesStorage()
    collector = ContentCollector(config, storage)

    # Test with FHI (Norwegian Institute of Public Health)
    domain = "fhi.no"
    max_pages = 3  # Small test

    print(f"Testing collection from {domain} (max {max_pages} pages)")

    try:
        result = collector.collect_from_domain(domain, max_pages)
        print(f"Result: {result}")

        # Analyze collected content
        content_list = storage.get_content_by_domain(domain)
        print(f"Collected {len(content_list)} pieces of content")

        for item in content_list:
            print(f"  - {item['title'][:60]}... (Quality: {item['quality_score']:.2f})")

    except Exception as e:
        print(f"Collection failed: {e}")


def test_page_discovery_methods():
    """Test different methods for discovering relevant pages"""
    print("\n=== Page Discovery Methods Test ===")

    config = TrustedSourcesConfig()
    storage = TrustedSourcesStorage()
    collector = ContentCollector(config, storage)

    domain = "helsedirektoratet.no"

    # Test the page discovery without actually collecting content
    print(f"Testing page discovery for {domain}")

    try:
        # This would require modifying the collector to expose discovery method
        print("Page discovery test would go here")
        print("Could test different strategies:")
        print("  1. Sitemap-based discovery")
        print("  2. Keyword-based link following")
        print("  3. Structured path exploration")

    except Exception as e:
        print(f"Discovery test failed: {e}")


def test_content_quality_scoring():
    """Test the content quality scoring algorithm"""
    print("\n=== Content Quality Scoring Test ===")

    # Test with sample Norwegian content
    test_contents = [
        {
            "title": "Hva er demens?",
            "content": "Demens er en fellesbetegnelse for tilstander som gir redusert hukommelse, "
                      "språk, problemløsning og andre tenkeevner som påvirker en persons evne til "
                      "å utføre daglige aktiviteter. Demens skyldes sykdom eller skade i hjernen. "
                      "Alzheimers sykdom er den vanligste årsaken til demens og kan utgjøre 60-80 % "
                      "av tilfellene. Vaskulær demens, som oppstår etter slag, er den nest vanligste "
                      "demenstypen.",
            "expected_score": "high"
        },
        {
            "title": "Kontakt oss",
            "content": "Ring oss på 12345678 eller send e-post til post@eksempel.no",
            "expected_score": "low"
        }
    ]

    storage = TrustedSourcesStorage()
    collector = ContentCollector(TrustedSourcesConfig(), storage)

    for i, test in enumerate(test_contents):
        score = collector._calculate_quality_score(test["content"], test["title"])
        print(f"Test {i+1}: {test['title']}")
        print(f"  Content length: {len(test['content'])} chars")
        print(f"  Quality score: {score:.2f}")
        print(f"  Expected: {test['expected_score']}")
        print()


if __name__ == "__main__":
    print("Trusted Sources Crawling Experiments")
    print("=====================================")

    # Run tests
    test_content_quality_scoring()
    # Uncomment to test actual collection (requires internet)
    # test_single_domain_collection()
    # test_page_discovery_methods()

    print("\nExperiment complete!")