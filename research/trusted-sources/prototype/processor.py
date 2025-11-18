"""
Content processor for trusted sources research
"""
import re
import logging
from typing import List, Dict, Any, Tuple
from difflib import SequenceMatcher
from collections import Counter

from .storage import TrustedSourcesStorage


class ContentProcessor:
    """Processes and analyzes collected content"""

    def __init__(self, storage: TrustedSourcesStorage):
        self.storage = storage
        self.logger = logging.getLogger("trusted-sources.processor")

    def analyze_content_quality(self, domain: str = None) -> Dict[str, Any]:
        """Analyze quality of collected content"""
        if domain:
            content_list = self.storage.get_content_by_domain(domain)
        else:
            content_list = self.storage.get_content_by_quality(0.0)  # Get all content

        if not content_list:
            return {"error": "No content found"}

        # Quality distribution
        quality_scores = [item['quality_score'] for item in content_list]
        quality_analysis = {
            "total_content": len(content_list),
            "average_quality": sum(quality_scores) / len(quality_scores),
            "high_quality_count": len([s for s in quality_scores if s >= 0.8]),
            "medium_quality_count": len([s for s in quality_scores if 0.6 <= s < 0.8]),
            "low_quality_count": len([s for s in quality_scores if s < 0.6])
        }

        # Content length analysis
        content_lengths = [len(item['content']) for item in content_list]
        quality_analysis.update({
            "average_content_length": sum(content_lengths) / len(content_lengths),
            "min_content_length": min(content_lengths),
            "max_content_length": max(content_lengths)
        })

        # Norwegian keyword analysis
        norwegian_keywords = [
            'demens', 'demensomsorg', 'alzheimer', 'hukommelse',
            'aldersdemens', 'kognitiv', 'pleie', 'omsorg'
        ]

        keyword_counts = Counter()
        for item in content_list:
            content_lower = item['content'].lower()
            for keyword in norwegian_keywords:
                if keyword in content_lower:
                    keyword_counts[keyword] += 1

        quality_analysis["keyword_frequency"] = dict(keyword_counts)

        return quality_analysis

    def find_duplicates(self, similarity_threshold: float = 0.8) -> List[Dict[str, Any]]:
        """Find duplicate or very similar content"""
        content_list = self.storage.get_content_by_quality(0.0)  # Get all content
        duplicates = []

        self.logger.info(f"Checking {len(content_list)} pieces of content for duplicates")

        for i, content1 in enumerate(content_list):
            for j, content2 in enumerate(content_list[i + 1:], i + 1):
                similarity = self._calculate_content_similarity(
                    content1['content'], content2['content']
                )

                if similarity >= similarity_threshold:
                    duplicates.append({
                        "content1_id": content1['id'],
                        "content1_url": content1['url'],
                        "content1_domain": content1['domain'],
                        "content2_id": content2['id'],
                        "content2_url": content2['url'],
                        "content2_domain": content2['domain'],
                        "similarity": similarity
                    })

        self.logger.info(f"Found {len(duplicates)} duplicate pairs")
        return duplicates

    def extract_key_information(self, content_id: int) -> Dict[str, Any]:
        """Extract key information from specific content"""
        # This would be where we could use NB-Llama or other local models
        # For now, implement basic extraction
        content_list = self.storage.get_content_by_quality(0.0)
        content_item = next((item for item in content_list if item['id'] == content_id), None)

        if not content_item:
            return {"error": "Content not found"}

        content = content_item['content']

        # Basic information extraction
        extracted_info = {
            "content_id": content_id,
            "url": content_item['url'],
            "domain": content_item['domain'],
            "title": content_item['title'],
            "word_count": len(content.split()),
            "character_count": len(content),
            "estimated_reading_time": len(content.split()) / 200  # ~200 words per minute
        }

        # Extract Norwegian dementia-specific terms
        norwegian_terms = self._extract_norwegian_terms(content)
        extracted_info["norwegian_dementia_terms"] = norwegian_terms

        # Extract potential sections/headings
        sections = self._extract_sections(content)
        extracted_info["content_sections"] = sections

        # Extract contact information or references
        references = self._extract_references(content)
        extracted_info["references"] = references

        return extracted_info

    def generate_citation(self, content_id: int) -> str:
        """Generate a proper citation for the content"""
        content_list = self.storage.get_content_by_quality(0.0)
        content_item = next((item for item in content_list if item['id'] == content_id), None)

        if not content_item:
            return "Content not found"

        # Generate APA-style citation for Norwegian sources
        title = content_item['title']
        url = content_item['url']
        domain = content_item['domain']
        collection_date = content_item['collection_date'][:10]  # Just the date part

        # Determine organization name
        org_names = {
            "helsedirektoratet.no": "Helsedirektoratet",
            "fhi.no": "Folkehelseinstituttet",
            "aldringoghelse.no": "Nasjonalt kompetansesenter for aldring og helse",
            "nasjonalforeningen.no": "Nasjonalforeningen for folkehelsen",
            "who.int": "World Health Organization",
            "alzheimer-europe.org": "Alzheimer Europe",
            "alz.org": "Alzheimer's Association"
        }

        organization = org_names.get(domain, domain)

        citation = f"{organization}. ({collection_date}). {title}. Hentet fra {url}"

        return citation

    def _calculate_content_similarity(self, content1: str, content2: str) -> float:
        """Calculate similarity between two pieces of content"""
        # Use sequence matcher for basic similarity
        matcher = SequenceMatcher(None, content1, content2)
        return matcher.ratio()

    def _extract_norwegian_terms(self, content: str) -> List[str]:
        """Extract Norwegian dementia-related terms from content"""
        norwegian_terms = [
            'demens', 'demensomsorg', 'alzheimer', 'alzheimers sykdom',
            'hukommelsestap', 'kognitiv svikt', 'aldersdemens',
            'vaskulær demens', 'frontotemporal demens', 'lewy body-demens',
            'mild kognitiv svikt', 'mks', 'pleie og omsorg',
            'dagaktiviteter', 'hjemmetjenester', 'institusjonsomsorg'
        ]

        found_terms = []
        content_lower = content.lower()

        for term in norwegian_terms:
            if term in content_lower:
                # Count occurrences
                count = content_lower.count(term)
                found_terms.append({"term": term, "count": count})

        return sorted(found_terms, key=lambda x: x['count'], reverse=True)

    def _extract_sections(self, content: str) -> List[str]:
        """Extract potential section headings from content"""
        # Look for lines that might be headings
        lines = content.split('\n')
        potential_headings = []

        for line in lines:
            line = line.strip()
            # Heuristics for headings
            if (len(line) > 0 and len(line) < 100 and
                (line.isupper() or line.istitle()) and
                not line.endswith('.') and
                any(keyword in line.lower() for keyword in ['demens', 'omsorg', 'symptom', 'behandling'])):

                potential_headings.append(line)

        return potential_headings[:10]  # Limit to top 10

    def _extract_references(self, content: str) -> List[str]:
        """Extract references or source links from content"""
        # Look for URLs in the content
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, content)

        # Look for reference patterns
        reference_patterns = [
            r'Kilde:.*',
            r'Referanse:.*',
            r'Les mer:.*',
            r'Se også:.*'
        ]

        references = []
        for pattern in reference_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            references.extend(matches)

        # Combine URLs and reference text
        all_references = urls + references
        return all_references[:5]  # Limit to 5 references