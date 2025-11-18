#!/usr/bin/env python3
"""
Experiment: Test content deduplication methods
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prototype.storage import TrustedSourcesStorage
from prototype.processor import ContentProcessor


def test_similarity_calculation():
    """Test the content similarity calculation algorithm"""
    print("=== Content Similarity Calculation Test ===")

    processor = ContentProcessor(TrustedSourcesStorage())

    test_pairs = [
        {
            "name": "Identical content",
            "content1": "Demens er en tilstand som påvirker hjernen og hukommelsen.",
            "content2": "Demens er en tilstand som påvirker hjernen og hukommelsen.",
            "expected_similarity": 1.0
        },
        {
            "name": "Very similar content",
            "content1": "Demens er en tilstand som påvirker hjernen og hukommelsen. Alzheimers sykdom er den vanligste formen.",
            "content2": "Demens er en tilstand som påvirker hjernen og hukommelse. Alzheimers sykdom er den mest vanlige formen.",
            "expected_similarity": 0.9
        },
        {
            "name": "Somewhat similar content",
            "content1": "Demens påvirker hukommelsen og tenkeevnene til eldre mennesker.",
            "content2": "Alzheimers sykdom er en form for demens som rammer mange eldre.",
            "expected_similarity": 0.4
        },
        {
            "name": "Completely different content",
            "content1": "Demens er en alvorlig hjernerelatert lidelse.",
            "content2": "Hvordan lage fiskekaker: Kok poteter og bland med fisk.",
            "expected_similarity": 0.1
        }
    ]

    for test in test_pairs:
        similarity = processor._calculate_content_similarity(test["content1"], test["content2"])
        print(f"Test: {test['name']}")
        print(f"  Content 1: {test['content1'][:50]}...")
        print(f"  Content 2: {test['content2'][:50]}...")
        print(f"  Calculated similarity: {similarity:.3f}")
        print(f"  Expected range: ~{test['expected_similarity']}")
        print()


def test_duplicate_detection_scenarios():
    """Test different scenarios where duplicates might occur"""
    print("=== Duplicate Detection Scenarios ===")

    scenarios = [
        {
            "name": "Same article from different domains",
            "description": "When the same health authority article appears on multiple sites",
            "content1": {
                "url": "https://helsedirektoratet.no/demens/symptomer",
                "domain": "helsedirektoratet.no",
                "title": "Symptomer på demens",
                "content": "Tidlige tegn på demens kan omfatte hukommelsestap, forvirring og problemer med daglige aktiviteter."
            },
            "content2": {
                "url": "https://helsenorge.no/demens/symptomer",
                "domain": "helsenorge.no",
                "title": "Demens - tidlige symptomer",
                "content": "Tidlige tegn på demens kan omfatte hukommelsestap, forvirring og problemer med daglige aktiviteter."
            }
        },
        {
            "name": "Updated version of same article",
            "description": "When an article is updated but core content remains the same",
            "content1": {
                "url": "https://fhi.no/demens-statistikk-2023",
                "domain": "fhi.no",
                "title": "Demens i Norge 2023",
                "content": "I 2023 ble det registrert 90.000 personer med demens i Norge. Alzheimers utgjorde 70% av tilfellene."
            },
            "content2": {
                "url": "https://fhi.no/demens-statistikk-2024",
                "domain": "fhi.no",
                "title": "Demens i Norge 2024",
                "content": "I 2024 ble det registrert 92.000 personer med demens i Norge. Alzheimers utgjorde 70% av tilfellene."
            }
        },
        {
            "name": "Translation or adaptation",
            "description": "When international content is adapted for Norwegian audience",
            "content1": {
                "url": "https://who.int/dementia-facts",
                "domain": "who.int",
                "title": "Dementia facts",
                "content": "Dementia affects memory, thinking and behavior. Alzheimer's disease is the most common form of dementia."
            },
            "content2": {
                "url": "https://fhi.no/who-demens-fakta",
                "domain": "fhi.no",
                "title": "WHO: Fakta om demens",
                "content": "Demens påvirker hukommelse, tenkning og atferd. Alzheimers sykdom er den vanligste formen for demens."
            }
        }
    ]

    processor = ContentProcessor(TrustedSourcesStorage())

    for scenario in scenarios:
        similarity = processor._calculate_content_similarity(
            scenario["content1"]["content"],
            scenario["content2"]["content"]
        )

        print(f"Scenario: {scenario['name']}")
        print(f"  Description: {scenario['description']}")
        print(f"  Source 1: {scenario['content1']['domain']} - {scenario['content1']['title']}")
        print(f"  Source 2: {scenario['content2']['domain']} - {scenario['content2']['title']}")
        print(f"  Content similarity: {similarity:.3f}")

        # Determine if this would be flagged as duplicate
        threshold = 0.8
        is_duplicate = similarity >= threshold
        print(f"  Would be flagged as duplicate (threshold {threshold}): {is_duplicate}")
        print()


def test_deduplication_strategies():
    """Test different strategies for handling duplicates"""
    print("=== Deduplication Strategies ===")

    strategies = [
        {
            "name": "Strict deduplication",
            "threshold": 0.95,
            "description": "Only flag nearly identical content as duplicates"
        },
        {
            "name": "Moderate deduplication",
            "threshold": 0.8,
            "description": "Flag very similar content as duplicates"
        },
        {
            "name": "Aggressive deduplication",
            "threshold": 0.6,
            "description": "Flag somewhat similar content as duplicates"
        }
    ]

    sample_similarity_scores = [0.99, 0.85, 0.75, 0.65, 0.45, 0.25]

    for strategy in strategies:
        print(f"Strategy: {strategy['name']} (threshold: {strategy['threshold']})")
        print(f"  {strategy['description']}")

        flagged_count = sum(1 for score in sample_similarity_scores if score >= strategy['threshold'])
        print(f"  Would flag {flagged_count}/{len(sample_similarity_scores)} pairs as duplicates")

        print("  Flagged pairs:")
        for score in sample_similarity_scores:
            if score >= strategy['threshold']:
                print(f"    - Similarity {score:.2f}: DUPLICATE")
            else:
                print(f"    - Similarity {score:.2f}: keep")
        print()


def test_hash_based_deduplication():
    """Test hash-based exact duplicate detection"""
    print("=== Hash-based Exact Duplicate Detection ===")

    import hashlib

    test_contents = [
        "Demens er en tilstand som påvirker hjernen.",
        "Demens er en tilstand som påvirker hjernen.",  # Exact duplicate
        "Demens er en tilstand som påvirker hjernen. ",  # With extra space
        "demens er en tilstand som påvirker hjernen.",  # Different case
        "Demens er en alvorlig tilstand som påvirker hjernen.",  # Similar but different
    ]

    print("Testing hash-based duplicate detection:")

    content_hashes = {}
    for i, content in enumerate(test_contents):
        # Clean content before hashing (remove extra whitespace, normalize case)
        cleaned_content = ' '.join(content.strip().lower().split())
        content_hash = hashlib.md5(cleaned_content.encode('utf-8')).hexdigest()

        print(f"Content {i+1}: {content[:40]}...")
        print(f"  Cleaned: {cleaned_content[:40]}...")
        print(f"  Hash: {content_hash[:16]}...")

        if content_hash in content_hashes:
            print(f"  DUPLICATE of content {content_hashes[content_hash]}")
        else:
            content_hashes[content_hash] = i + 1
            print(f"  UNIQUE")
        print()


if __name__ == "__main__":
    print("Content Deduplication Experiments")
    print("=================================")

    test_similarity_calculation()
    test_duplicate_detection_scenarios()
    test_deduplication_strategies()
    test_hash_based_deduplication()

    print("Deduplication experiments complete!")