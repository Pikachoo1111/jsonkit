"""
PyJSONKit - A comprehensive Python toolkit for JSON processing with AI features.

This package provides utilities for reading, writing, validating, and
manipulating JSON data, with advanced AI-focused features for modern data workflows.
"""

__version__ = "0.1.0"
__author__ = "Armaan Shahpuri"
__email__ = "armaan30312@gmail.com"

from .core import JSONHandler
from .parser import JSONParser
from .validator import JSONValidator
from .ai_processor import AIJSONProcessor
from .extractor import JSONExtractor
from .cleaner import JSONCleaner
from .transformer import JSONTransformer
from .schema_generator import SchemaGenerator

__all__ = [
    "JSONHandler",
    "JSONValidator",
    "JSONParser",
    "AIJSONProcessor",
    "JSONExtractor",
    "JSONCleaner",
    "JSONTransformer",
    "SchemaGenerator",
]
