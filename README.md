# PyJSONKit

A comprehensive Python toolkit for JSON processing with advanced AI-focused features for modern data workflows.

## 🚀 Features

### Core JSON Operations
- Easy JSON file manipulation and validation
- Pretty printing and formatting
- Robust parsing with error handling
- Simple API for common JSON operations

### 🤖 AI-Focused Features
- **AI JSON Processing**: Extract and fix JSON from AI model responses
- **Advanced Data Extraction**: JSONPath-like queries and entity extraction
- **Intelligent Data Cleaning**: Remove AI artifacts and sanitize data
- **Smart Data Transformation**: Reshape data for ML/AI workflows
- **Schema Generation**: Auto-generate schemas from AI data samples

## Installation

```bash
pip install pyjsonkit
```

## Quick Start

### Basic JSON Operations
```python
from pyjsonkit import JSONHandler

# Create a JSON handler
handler = JSONHandler("data.json")

# Get a value
value = handler.get("key")

# Set a value
handler.set("key", "value")

# Validate JSON
is_valid = handler.validate()
```

### AI-Focused Features
```python
from pyjsonkit import AIJSONProcessor, JSONExtractor, JSONCleaner

# Extract JSON from AI responses
ai_response = '''
Here's the data you requested:
```json
{"name": "John", "age": 30}
```
'''
data = AIJSONProcessor.extract_json_from_text(ai_response)

# Clean AI-generated artifacts
messy_data = {"name": "[AI_GENERATED] John Doe", "note": "[TODO: verify]"}
clean_data = JSONCleaner.clean_ai_artifacts(messy_data)

# Extract data with complex queries
result = JSONExtractor.extract_by_path(data, "users[*].name")
```

## 📚 Comprehensive Feature Set

### AI JSON Processor
- Extract JSON from mixed AI responses (markdown, code blocks, plain text)
- Fix common AI JSON errors (quotes, booleans, trailing commas)
- Batch process multiple AI responses with error handling
- Extract structured data from natural language text

### Advanced Data Extraction
- JSONPath-like data extraction with complex path queries
- Multi-path extraction in single operations
- AI entity extraction (emails, phones, URLs, etc.)
- Nested array extraction with configurable depth
- Schema analysis and statistics

### Intelligent Data Cleaning
- Remove AI-generated artifacts and markers
- Sanitize sensitive data for AI processing
- Normalize strings and remove extra whitespace
- Deduplicate arrays and remove null/empty values
- Clean malformed data structures

### Smart Data Transformation
- Reshape data for ML training (features/labels separation)
- Convert to chat/conversation formats for LLMs
- Create embeddings-ready format with metadata
- Aggregate and pivot data for analysis
- Flatten nested structures for CSV export
- Normalize data for AI prompts with size limits

### Schema Generation
- Auto-generate JSON schemas from data samples
- Create AI prompt schemas with validation rules
- Support for strict and flexible schema modes
- Include examples and constraints in generated schemas
- Validate data against generated schemas

## 🎯 Use Cases

- **AI/ML Data Pipelines**: Process and clean data from AI models
- **LLM Integration**: Extract structured data from language model outputs
- **Data Validation**: Ensure data quality in automated workflows
- **API Response Processing**: Handle inconsistent JSON from various sources
- **Data Transformation**: Prepare data for different ML frameworks

## Development

### Setup

```bash
git clone https://github.com/Pikachoo1111/jsonkit.git
cd jsonkit
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/
isort src/
```

## 📖 Documentation

For detailed documentation and examples, see the [examples](examples/) directory.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.
