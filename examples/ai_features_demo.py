#!/usr/bin/env python3
"""
Comprehensive demo of PyJSONKit's AI-focused features.

This example demonstrates how to use the advanced AI processing capabilities
for handling JSON data from AI models and performing post-processing tasks.
"""

import json
from pyjsonkit import (
    AIJSONProcessor, JSONExtractor, JSONCleaner,
    JSONTransformer, SchemaGenerator
)


def demo_ai_json_processor():
    """Demonstrate AI JSON processing capabilities."""
    print("=" * 60)
    print("AI JSON PROCESSOR DEMO")
    print("=" * 60)
    
    # Simulate AI model response with common issues
    ai_response = '''
    Here's the extracted information:
    ```json
    {
        'name': 'John Doe',
        'age': 30,
        'skills': ['Python', 'JavaScript', 'SQL',],
        'active': True,
        'metadata': None
    }
    ```
    Additional notes: This data was extracted from the resume.
    '''
    
    print("1. Extracting JSON from AI response:")
    print(f"Raw response: {ai_response[:100]}...")
    
    # Extract and fix JSON
    extracted = AIJSONProcessor.extract_json_from_text(ai_response)
    print(f"Extracted JSON: {extracted}")
    
    # Parse with validation
    try:
        parsed = AIJSONProcessor.parse_ai_response(ai_response, ["name", "age", "skills"])
        print(f"Validated JSON: {parsed}")
    except ValueError as e:
        print(f"Validation error: {e}")
    
    # Batch processing multiple responses
    responses = [
        '{"name": "Alice", "score": 95}',
        '{"name": "Bob", "score": 87}',
        'Invalid JSON response',
        '{"name": "Charlie", "score": 92}'
    ]
    
    print("\n2. Batch processing AI responses:")
    batch_results = AIJSONProcessor.batch_process_ai_responses(responses, ["name"])
    for i, result in enumerate(batch_results):
        print(f"Response {i}: {result}")
    
    # Extract structured data from text
    print("\n3. Extracting structured data from text:")
    text = "The user John Doe is 30 years old, active: true, skills: Python, JavaScript"
    schema = {"name": "string", "age": "number", "active": "boolean", "skills": "list"}
    
    structured = AIJSONProcessor.extract_structured_data(text, schema)
    print(f"Structured data: {structured}")


def demo_json_extractor():
    """Demonstrate advanced JSON extraction capabilities."""
    print("\n" + "=" * 60)
    print("JSON EXTRACTOR DEMO")
    print("=" * 60)
    
    # Complex nested data
    data = {
        "users": [
            {
                "id": 1,
                "profile": {
                    "name": "John Doe",
                    "contact": {
                        "email": "john@example.com",
                        "phone": "555-123-4567"
                    }
                },
                "posts": [
                    {"title": "Post 1", "likes": 25},
                    {"title": "Post 2", "likes": 42}
                ]
            },
            {
                "id": 2,
                "profile": {
                    "name": "Jane Smith",
                    "contact": {
                        "email": "jane@example.com",
                        "phone": "555-987-6543"
                    }
                }
            }
        ],
        "metadata": {
            "total_users": 2,
            "last_updated": "2023-12-01"
        }
    }
    
    print("1. Extracting data by path:")
    name = JSONExtractor.extract_by_path(data, "users.0.profile.name")
    print(f"First user name: {name}")
    
    email = JSONExtractor.extract_by_path(data, "users.1.profile.contact.email")
    print(f"Second user email: {email}")
    
    print("\n2. Extracting multiple paths:")
    paths = {
        "first_user": "users.0.profile.name",
        "total_count": "metadata.total_users",
        "last_update": "metadata.last_updated"
    }
    extracted = JSONExtractor.extract_multiple_paths(data, paths)
    print(f"Multiple extractions: {extracted}")
    
    print("\n3. Finding all values for a key:")
    all_names = JSONExtractor.find_all_values(data, "name")
    print(f"All names: {all_names}")
    
    print("\n4. Extracting AI entities:")
    entities = JSONExtractor.extract_ai_entities(data, ["email", "phone"])
    print(f"Extracted entities: {entities}")
    
    print("\n5. Schema analysis:")
    schema_info = JSONExtractor.extract_schema_info(data)
    print(f"Schema type: {schema_info['type']}")
    print(f"Statistics: {schema_info['statistics']}")


def demo_json_cleaner():
    """Demonstrate JSON cleaning capabilities."""
    print("\n" + "=" * 60)
    print("JSON CLEANER DEMO")
    print("=" * 60)
    
    # Messy AI-generated data
    messy_data = {
        "name": "  [AI_GENERATED] John Doe  ",
        "email": "john@example.com",
        "phone": "555-123-4567",
        "bio": None,
        "tags": [],
        "metadata": {
            "created": None,
            "notes": "",
            "artifacts": "[TODO: verify this data]"
        },
        "description": "This   has    multiple     spaces",
        "items": [1, 1, 2, 2, 3, 1]  # Duplicates
    }
    
    print("1. Original messy data:")
    print(json.dumps(messy_data, indent=2))
    
    print("\n2. After removing null values:")
    cleaned = JSONCleaner.remove_null_values(messy_data)
    print(json.dumps(cleaned, indent=2))
    
    print("\n3. After removing empty values:")
    cleaned = JSONCleaner.remove_empty_values(cleaned)
    print(json.dumps(cleaned, indent=2))
    
    print("\n4. After normalizing strings:")
    cleaned = JSONCleaner.normalize_strings(
        cleaned, 
        strip_whitespace=True, 
        remove_extra_spaces=True
    )
    print(json.dumps(cleaned, indent=2))
    
    print("\n5. After cleaning AI artifacts:")
    cleaned = JSONCleaner.clean_ai_artifacts(cleaned)
    print(json.dumps(cleaned, indent=2))
    
    print("\n6. After deduplicating arrays:")
    cleaned = JSONCleaner.deduplicate_arrays(cleaned)
    print(json.dumps(cleaned, indent=2))
    
    print("\n7. Sanitized for AI processing:")
    sanitized = JSONCleaner.sanitize_for_ai(
        messy_data, 
        remove_sensitive=True, 
        max_string_length=50
    )
    print(json.dumps(sanitized, indent=2))


def demo_json_transformer():
    """Demonstrate JSON transformation capabilities."""
    print("\n" + "=" * 60)
    print("JSON TRANSFORMER DEMO")
    print("=" * 60)
    
    # Sample data for ML training
    training_data = [
        {"text": "Great product!", "sentiment": "positive", "confidence": 0.95, "length": 14},
        {"text": "Terrible service", "sentiment": "negative", "confidence": 0.88, "length": 16},
        {"text": "It's okay", "sentiment": "neutral", "confidence": 0.72, "length": 9},
        {"text": "Love it!", "sentiment": "positive", "confidence": 0.91, "length": 8}
    ]
    
    print("1. Reshaping for ML training:")
    ml_data = JSONTransformer.reshape_for_training(
        training_data, 
        input_keys=["length", "confidence"], 
        output_keys=["sentiment"]
    )
    print(f"Training inputs: {ml_data['inputs']}")
    print(f"Training outputs: {ml_data['outputs']}")
    
    print("\n2. Converting to chat format:")
    chat_data = [
        {"role": "user", "content": "Hello, how are you?"},
        {"role": "assistant", "content": "I'm doing well, thank you!"},
        {"role": "user", "content": "Can you help me with JSON processing?"}
    ]
    
    chat_format = JSONTransformer.convert_to_chat_format(chat_data)
    print("Chat format:")
    for msg in chat_format:
        print(f"  {msg['role']}: {msg['content']}")
    
    print("\n3. Creating embeddings format:")
    articles = [
        {"title": "AI in Healthcare", "content": "AI is transforming healthcare...", "category": "tech"},
        {"title": "Climate Change", "content": "Global warming effects...", "category": "environment"}
    ]
    
    embeddings_format = JSONTransformer.create_embeddings_format(
        articles, 
        text_key="content", 
        metadata_keys=["title", "category"]
    )
    print("Embeddings format:")
    for item in embeddings_format:
        print(f"  ID: {item['id']}, Text: {item['text'][:30]}..., Metadata: {item['metadata']}")
    
    print("\n4. Aggregating data:")
    sales_data = [
        {"region": "North", "sales": 1000, "quarter": "Q1"},
        {"region": "North", "sales": 1200, "quarter": "Q2"},
        {"region": "South", "sales": 800, "quarter": "Q1"},
        {"region": "South", "sales": 900, "quarter": "Q2"}
    ]
    
    aggregated = JSONTransformer.aggregate_by_key(
        sales_data, 
        "region", 
        {"sales": "sum", "quarter": "count"}
    )
    print(f"Aggregated sales: {aggregated}")
    
    print("\n5. Flattening for CSV:")
    nested_data = [
        {
            "user": {"name": "John", "age": 30},
            "preferences": {"theme": "dark", "notifications": True}
        }
    ]
    
    flattened = JSONTransformer.flatten_for_csv(nested_data)
    print(f"Flattened for CSV: {flattened[0]}")


def demo_schema_generator():
    """Demonstrate schema generation capabilities."""
    print("\n" + "=" * 60)
    print("SCHEMA GENERATOR DEMO")
    print("=" * 60)
    
    # Sample data from AI responses
    ai_responses = [
        {
            "name": "John Doe",
            "age": 30,
            "email": "john@example.com",
            "skills": ["Python", "JavaScript"],
            "active": True
        },
        {
            "name": "Jane Smith",
            "age": 25,
            "email": "jane@example.com",
            "skills": ["Java", "C++", "Python"],
            "active": False
        },
        {
            "name": "Bob Johnson",
            "age": 35,
            "email": "bob@example.com",
            "skills": ["Go", "Rust"],
            "active": True,
            "optional_field": "extra_data"
        }
    ]
    
    print("1. Generating schema from AI response samples:")
    schema = SchemaGenerator.generate_from_samples(ai_responses, include_examples=True)
    print(json.dumps(schema, indent=2))
    
    print("\n2. Generating AI prompt schema:")
    ai_schema = SchemaGenerator.generate_ai_prompt_schema(
        "Extract user information from text",
        expected_fields=["name", "age", "email", "skills"],
        field_types={
            "name": "string",
            "age": "integer", 
            "email": "string",
            "skills": "array"
        }
    )
    print(json.dumps(ai_schema, indent=2))
    
    print("\n3. Validating data against schema:")
    test_data = {
        "name": "Alice Cooper",
        "age": 28,
        "email": "alice@example.com",
        "skills": ["Python", "Machine Learning"]
    }
    
    is_valid, errors = SchemaGenerator.validate_against_schema(test_data, ai_schema)
    print(f"Validation result: {'Valid' if is_valid else 'Invalid'}")
    if errors:
        print(f"Errors: {errors}")


def main():
    """Run all demos."""
    print("PyJSONKit AI Features Comprehensive Demo")
    print("=" * 60)
    
    demo_ai_json_processor()
    demo_json_extractor()
    demo_json_cleaner()
    demo_json_transformer()
    demo_schema_generator()
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
    print("\nThis demo showcased PyJSONKit's advanced AI-focused features:")
    print("• AI JSON Processing: Extract and fix JSON from AI responses")
    print("• Advanced Extraction: Complex path-based data extraction")
    print("• Intelligent Cleaning: Remove artifacts and sanitize data")
    print("• Smart Transformation: Reshape data for ML and AI workflows")
    print("• Schema Generation: Auto-generate schemas from AI data samples")
    print("\nThese features make PyJSONKit ideal for AI/ML data pipelines!")


if __name__ == "__main__":
    main()
