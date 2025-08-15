# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2024-12-07

### Added
- **Core JSON Operations**
  - JSONHandler class for file-based JSON operations
  - JSONValidator class for JSON validation with custom rules
  - JSONParser class for JSON parsing and manipulation
  - Professional package structure following Python best practices

- **AI-Focused Features** (Major expansion)
  - **AIJSONProcessor**: Extract and fix JSON from AI model responses
    - Extract JSON from mixed text (markdown, code blocks, plain text)
    - Fix common AI JSON errors (quotes, booleans, trailing commas)
    - Batch process multiple AI responses with error handling
    - Extract structured data from natural language text

  - **JSONExtractor**: Advanced data extraction capabilities
    - JSONPath-like data extraction with complex path queries
    - Multi-path extraction in single operations
    - AI entity extraction (emails, phones, URLs, etc.)
    - Nested array extraction with configurable depth
    - Schema analysis and statistics

  - **JSONCleaner**: Intelligent data cleaning and sanitization
    - Remove AI-generated artifacts and markers
    - Sanitize sensitive data for AI processing
    - Normalize strings and remove extra whitespace
    - Deduplicate arrays and remove null/empty values
    - Clean malformed data structures

  - **JSONTransformer**: Smart data transformation for ML/AI workflows
    - Reshape data for ML training (features/labels separation)
    - Convert to chat/conversation formats for LLMs
    - Create embeddings-ready format with metadata
    - Aggregate and pivot data for analysis
    - Flatten nested structures for CSV export
    - Normalize data for AI prompts with size limits

  - **SchemaGenerator**: Auto-generate schemas from AI data samples
    - Generate JSON schemas from data samples
    - Create AI prompt schemas with validation rules
    - Support for strict and flexible schema modes
    - Include examples and constraints in generated schemas
    - Validate data against generated schemas

- **Testing & Quality**
  - Comprehensive test suite with 133+ tests
  - 100% test coverage for all new AI features
  - Real-world demo showcasing AI capabilities
  - Type hints throughout codebase
  - Code quality tools (black, isort, flake8, mypy)

### Changed
- Updated package description to reflect AI-focused capabilities
- Enhanced README with comprehensive feature documentation
- Improved package metadata and classifiers
- Updated development status to Beta
- Renamed package from jsonutilkit to pyjsonkit for PyPI compatibility

### Fixed
- Regex patterns in AI processor for proper number/boolean extraction
- Nested array extraction logic with correct depth calculation
- AI artifact cleaning patterns to handle various markers
- Schema generation strict mode for proper field identification
- Duplicate JSON extraction through deduplication
- Import cleanup to resolve linting warnings
