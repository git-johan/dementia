#!/usr/bin/env python3
"""
Experiment: Test content quality assessment methods
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prototype.storage import TrustedSourcesStorage
from prototype.processor import ContentProcessor


def test_norwegian_keyword_extraction():
    """Test extraction of Norwegian dementia keywords"""
    print("=== Norwegian Keyword Extraction Test ===")

    processor = ContentProcessor(TrustedSourcesStorage())

    test_content = """
    Demens er en av de største helseutfordringene i vår tid. Alzheimers sykdom er den vanligste
    formen for demens, men det finnes også vaskulær demens, frontotemporal demens, og Lewy body-demens.

    Symptomer på demens inkluderer hukommelsestap, kognitiv svikt, og problemer med daglige aktiviteter.
    Mild kognitiv svikt (MKS) kan være et tidlig tegn på demens.

    God demensomsorg krever en helhetlig tilnærming som inkluderer medisinsk behandling,
    pleie og omsorg, og støtte til pårørende. Hjemmetjenester og dagaktiviteter kan hjelpe
    personer med demens å leve hjemme lengre.
    """

    norwegian_terms = processor._extract_norwegian_terms(test_content)

    print("Extracted Norwegian dementia terms:")
    for term_info in norwegian_terms:
        print(f"  {term_info['term']}: {term_info['count']} occurrences")


def test_content_section_extraction():
    """Test extraction of content sections"""
    print("\n=== Content Section Extraction Test ===")

    processor = ContentProcessor(TrustedSourcesStorage())

    test_content_with_headings = """
    DEMENS - EN OVERSIKT

    Hva er demens?
    Demens er en fellesbetegnelse for tilstander som påvirker hjernen.

    SYMPTOMER PÅ DEMENS
    De vanligste symptomene inkluderer hukommelsestap og forvirring.

    Behandling og omsorg
    Det finnes ingen kur for demens, men symptomene kan behandles.

    STØTTE TIL PÅRØRENDE
    Pårørende trenger også støtte i denne vanskelige tiden.

    Dette er vanlig tekst som ikke er en overskrift.
    """

    sections = processor._extract_sections(test_content_with_headings)

    print("Extracted content sections:")
    for section in sections:
        print(f"  - {section}")


def test_citation_generation():
    """Test citation generation for Norwegian sources"""
    print("\n=== Citation Generation Test ===")

    # This would need actual content in the database
    # For now, show the expected citation format

    sample_citations = {
        "helsedirektoratet.no": "Helsedirektoratet. (2024-11-18). Demens - informasjon og råd. Hentet fra https://helsedirektoratet.no/demens",
        "fhi.no": "Folkehelseinstituttet. (2024-11-18). Tall og fakta om demens i Norge. Hentet fra https://fhi.no/demens-statistikk",
        "who.int": "World Health Organization. (2024-11-18). Dementia fact sheet. Hentet fra https://who.int/dementia-facts"
    }

    print("Sample citation formats:")
    for domain, citation in sample_citations.items():
        print(f"  {domain}:")
        print(f"    {citation}")
        print()


def test_quality_scoring_factors():
    """Test different factors that influence quality scoring"""
    print("\n=== Quality Scoring Factors Test ===")

    processor = ContentProcessor(TrustedSourcesStorage())
    storage = TrustedSourcesStorage()

    # We need a collector instance for the quality scoring method
    from prototype.config import TrustedSourcesConfig
    from prototype.collector import ContentCollector
    collector = ContentCollector(TrustedSourcesConfig(), storage)

    test_cases = [
        {
            "name": "High-quality Norwegian content",
            "title": "Demens: Symptomer, årsaker og behandling",
            "content": """
            Demens er en progressiv hjernerelatert lidelse som påvirker hukommelse, tenkning, orientering,
            forståelse, regning, læringsevne, språk og dømmekraft. Alzheimers sykdom er den vanligste formen
            for demens og kan utgjøre 60-80 prosent av tilfellene.

            Symptomer på demens utvikler seg gradvis og kan inkludere:
            - Hukommelsestap som påvirker dagliglivet
            - Vanskeligheter med planlegging og problemløsning
            - Forvirring om tid og sted
            - Problemer med språk og kommunikasjon

            Det finnes ingen kur for demens, men tidlig diagnose og god omsorg kan forbedre livskvaliteten
            for både pasienten og pårørende. Demensomsorg bør være individualisert og fokusere på personens
            ressurser og behov.
            """,
            "expected": "Should score high due to Norwegian content, medical keywords, good structure"
        },
        {
            "name": "Short navigation content",
            "title": "Meny",
            "content": "Hjem | Om oss | Kontakt | Personvern",
            "expected": "Should score low due to short length and lack of substance"
        },
        {
            "name": "English medical content",
            "title": "Understanding Dementia",
            "content": """
            Dementia is a term used to describe various symptoms of cognitive decline, such as forgetfulness.
            It is a symptom of several underlying diseases and brain disorders. Dementia is not a single
            disease in itself, but a general term to describe symptoms of impairment in memory, communication,
            and thinking.
            """,
            "expected": "Should score medium - good content but not Norwegian"
        }
    ]

    for test_case in test_cases:
        score = collector._calculate_quality_score(test_case["content"], test_case["title"])
        print(f"Test: {test_case['name']}")
        print(f"  Title: {test_case['title']}")
        print(f"  Content length: {len(test_case['content'])} chars")
        print(f"  Quality score: {score:.2f}")
        print(f"  Expected: {test_case['expected']}")
        print()


if __name__ == "__main__":
    print("Content Quality Assessment Experiments")
    print("======================================")

    test_norwegian_keyword_extraction()
    test_content_section_extraction()
    test_citation_generation()
    test_quality_scoring_factors()

    print("Quality assessment experiments complete!")