#!/usr/bin/env python3
"""
Basic usage examples for PyJSONKit.
"""

import tempfile
from pathlib import Path

from pyjsonkit import JSONHandler, JSONValidator, JSONParser


def main():
    """Demonstrate basic PyJSONKit functionality."""
    print("PyJSONKit Basic Usage Examples")
    print("=" * 40)
    
    # Create a temporary file for demonstration
    with tempfile.TemporaryDirectory() as temp_dir:
        json_file = Path(temp_dir) / "example.json"
        
        # Example 1: JSONHandler basic operations
        print("\n1. JSONHandler - Basic Operations")
        print("-" * 30)
        
        handler = JSONHandler(json_file)
        
        # Set some data
        handler.set("name", "John Doe")
        handler.set("age", 30)
        handler.set("skills", ["Python", "JavaScript", "SQL"])
        
        print(f"Name: {handler.get('name')}")
        print(f"Age: {handler.get('age')}")
        print(f"Skills: {handler.get('skills')}")
        print(f"Total keys: {len(handler)}")
        
        # Update with multiple values
        handler.update({
            "city": "New York",
            "active": True
        })
        
        print(f"All keys: {handler.keys()}")
        
        # Example 2: JSONValidator
        print("\n2. JSONValidator - Validation")
        print("-" * 30)
        
        # Validate JSON string
        valid_json = '{"name": "Alice", "age": 25}'
        invalid_json = '{"name": "Bob", "age": }'
        
        is_valid, error = JSONValidator.validate_json_string(valid_json)
        print(f"Valid JSON string: {is_valid}")
        
        is_valid, error = JSONValidator.validate_json_string(invalid_json)
        print(f"Invalid JSON string: {is_valid}, Error: {error}")
        
        # Validate file
        is_valid, error = JSONValidator.validate_json_file(json_file)
        print(f"JSON file valid: {is_valid}")
        
        # Schema validation
        data = {"name": "Charlie", "age": 35, "active": True}
        schema = {"name": "string", "age": "number", "active": "boolean"}
        
        is_valid, errors = JSONValidator.validate_schema(data, schema)
        print(f"Schema validation: {is_valid}")
        
        # Example 3: JSONParser
        print("\n3. JSONParser - Parsing and Manipulation")
        print("-" * 30)
        
        # Parse string
        json_string = '{"user": {"name": "David", "details": {"age": 28}}}'
        parsed_data = JSONParser.parse_string(json_string)
        print(f"Parsed data: {parsed_data}")
        
        # Flatten object
        flattened = JSONParser.flatten_object(parsed_data)
        print(f"Flattened: {flattened}")
        
        # Unflatten back
        unflattened = JSONParser.unflatten_object(flattened)
        print(f"Unflattened: {unflattened}")
        
        # Merge objects
        obj1 = {"a": 1, "b": {"x": 10}}
        obj2 = {"b": {"y": 20}, "c": 3}
        merged = JSONParser.deep_merge_objects(obj1, obj2)
        print(f"Deep merged: {merged}")
        
        # Pretty print
        print("\n4. Pretty Printing")
        print("-" * 30)
        print("Handler contents:")
        print(handler.pretty_print())


if __name__ == "__main__":
    main()
