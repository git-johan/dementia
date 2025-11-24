"""
Domain-specific content extractors package.

This package contains specialized content extractors for different domains,
providing higher quality extraction compared to generic approaches.
"""

from .base_extractor import BaseExtractor, ExtractionResult
from .helsedirektoratet_no import HelsedirektoratetNoExtractor

__all__ = [
    'BaseExtractor',
    'ExtractionResult',
    'HelsedirektoratetNoExtractor'
]