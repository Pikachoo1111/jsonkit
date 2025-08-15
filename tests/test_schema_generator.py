"""
Tests for JSON schema generator functionality.
"""

import pytest
from pyjsonkit.schema_generator import SchemaGenerator


class TestSchemaGenerator:
    """Test cases for SchemaGenerator class."""
    
    @pytest.fixture
    def sample_data(self):
        """Sample data for schema generation."""
        return [
            {
                "name": "John Doe",
                "age": 30,
                "email": "john@example.com",
                "active": True,
                "scores": [85, 92, 78]
            },
            {
                "name": "Jane Smith",
                "age": 25,
                "email": "jane@example.com",
                "active": False,
                "scores": [90, 88, 95]
            },
            {
                "name": "Bob Johnson",
                "age": 35,
                "email": "bob@example.com",
                "active": True,
                "scores": [75, 80, 85],
                "optional_field": "extra_data"
            }
        ]
    
    def test_generate_from_samples_basic(self, sample_data):
        """Test basic schema generation from samples."""
        schema = SchemaGenerator.generate_from_samples(sample_data)
        
        assert schema["type"] == "object"
        assert "$schema" in schema
        assert "properties" in schema
        
        # Check required fields (present in most samples)
        required = schema.get("required", [])
        assert "name" in required
        assert "age" in required
        assert "email" in required
        assert "active" in required
        assert "scores" in required
        
        # Optional field should not be required
        assert "optional_field" not in required
    
    def test_generate_from_samples_field_types(self, sample_data):
        """Test that field types are correctly identified."""
        schema = SchemaGenerator.generate_from_samples(sample_data)
        
        properties = schema["properties"]
        
        assert properties["name"]["type"] == "string"
        assert properties["age"]["type"] == "integer"
        assert properties["email"]["type"] == "string"
        assert properties["active"]["type"] == "boolean"
        assert properties["scores"]["type"] == "array"
    
    def test_generate_from_samples_string_constraints(self, sample_data):
        """Test string field constraints."""
        schema = SchemaGenerator.generate_from_samples(sample_data)
        
        email_schema = schema["properties"]["email"]
        assert email_schema["format"] == "email"
        assert "minLength" in email_schema
        assert "maxLength" in email_schema
    
    def test_generate_from_samples_numeric_constraints(self, sample_data):
        """Test numeric field constraints."""
        schema = SchemaGenerator.generate_from_samples(sample_data)
        
        age_schema = schema["properties"]["age"]
        assert "minimum" in age_schema
        assert "maximum" in age_schema
        assert age_schema["minimum"] == 25
        assert age_schema["maximum"] == 35
    
    def test_generate_from_samples_array_constraints(self, sample_data):
        """Test array field constraints."""
        schema = SchemaGenerator.generate_from_samples(sample_data)
        
        scores_schema = schema["properties"]["scores"]
        assert "minItems" in scores_schema
        assert "maxItems" in scores_schema
        assert "items" in scores_schema
        assert scores_schema["items"]["type"] == "integer"
    
    def test_generate_from_samples_with_examples(self, sample_data):
        """Test schema generation with examples."""
        schema = SchemaGenerator.generate_from_samples(sample_data, include_examples=True)
        
        name_schema = schema["properties"]["name"]
        assert "examples" in name_schema
        assert len(name_schema["examples"]) <= 3
        assert "John Doe" in name_schema["examples"]
    
    def test_generate_from_samples_without_examples(self, sample_data):
        """Test schema generation without examples."""
        schema = SchemaGenerator.generate_from_samples(sample_data, include_examples=False)
        
        name_schema = schema["properties"]["name"]
        assert "examples" not in name_schema
    
    def test_generate_from_samples_strict_mode(self, sample_data):
        """Test schema generation in strict mode."""
        schema = SchemaGenerator.generate_from_samples(sample_data, strict=True)
        
        assert schema["additionalProperties"] is False
        
        # In strict mode, optional_field should still not be required
        # since it's not present in all samples
        required = schema.get("required", [])
        assert "optional_field" not in required
    
    def test_generate_from_samples_mixed_types(self):
        """Test schema generation with mixed types."""
        data = [
            {"field": "string_value"},
            {"field": 42},
            {"field": True}
        ]
        
        schema = SchemaGenerator.generate_from_samples(data)
        
        field_schema = schema["properties"]["field"]
        assert "anyOf" in field_schema
        
        types = [item["type"] for item in field_schema["anyOf"]]
        assert "string" in types
        assert "integer" in types
        assert "boolean" in types
    
    def test_generate_from_samples_nullable_fields(self):
        """Test schema generation with nullable fields."""
        data = [
            {"name": "John", "middle_name": "William"},
            {"name": "Jane", "middle_name": None},
            {"name": "Bob", "middle_name": "Robert"}
        ]
        
        schema = SchemaGenerator.generate_from_samples(data)
        
        middle_name_schema = schema["properties"]["middle_name"]
        
        # Should handle nullable field
        if "type" in middle_name_schema:
            assert isinstance(middle_name_schema["type"], list)
            assert "null" in middle_name_schema["type"]
        else:
            assert "anyOf" in middle_name_schema
    
    def test_generate_from_samples_nested_objects(self):
        """Test schema generation with nested objects."""
        data = [
            {
                "user": {
                    "name": "John",
                    "profile": {"bio": "Developer"}
                }
            },
            {
                "user": {
                    "name": "Jane",
                    "profile": {"bio": "Designer"}
                }
            }
        ]
        
        schema = SchemaGenerator.generate_from_samples(data)
        
        user_schema = schema["properties"]["user"]
        assert user_schema["type"] == "object"
        assert "properties" in user_schema
        assert "name" in user_schema["properties"]
        assert "profile" in user_schema["properties"]
    
    def test_generate_ai_prompt_schema(self):
        """Test generating schema for AI prompts."""
        task_description = "Extract user information"
        expected_fields = ["name", "age", "email", "skills"]
        field_types = {
            "name": "string",
            "age": "integer",
            "email": "string",
            "skills": "array"
        }
        
        schema = SchemaGenerator.generate_ai_prompt_schema(
            task_description, expected_fields, field_types
        )
        
        assert schema["title"] == "AI Response Schema: Extract user information"
        assert schema["type"] == "object"
        assert schema["additionalProperties"] is False
        assert schema["required"] == expected_fields
        
        # Check field constraints
        assert schema["properties"]["name"]["minLength"] == 1
        assert schema["properties"]["name"]["maxLength"] == 1000
        assert schema["properties"]["skills"]["minItems"] == 0
        assert schema["properties"]["skills"]["maxItems"] == 100
        assert schema["properties"]["age"]["minimum"] == 0
    
    def test_generate_ai_prompt_schema_default_types(self):
        """Test AI prompt schema with default field types."""
        expected_fields = ["summary", "keywords"]
        
        schema = SchemaGenerator.generate_ai_prompt_schema(
            "Summarize text", expected_fields
        )
        
        # Should default to string type
        assert schema["properties"]["summary"]["type"] == "string"
        assert schema["properties"]["keywords"]["type"] == "string"
    
    def test_validate_against_schema_valid(self):
        """Test validating valid data against schema."""
        data = {
            "name": "John Doe",
            "age": 30,
            "active": True
        }
        
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
                "active": {"type": "boolean"}
            },
            "required": ["name", "age"]
        }
        
        is_valid, errors = SchemaGenerator.validate_against_schema(data, schema)
        
        assert is_valid
        assert len(errors) == 0
    
    def test_validate_against_schema_missing_required(self):
        """Test validation with missing required field."""
        data = {"name": "John Doe"}
        
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name", "age"]
        }
        
        is_valid, errors = SchemaGenerator.validate_against_schema(data, schema)
        
        assert not is_valid
        assert len(errors) > 0
        assert any("Missing required field" in error for error in errors)
    
    def test_validate_against_schema_wrong_type(self):
        """Test validation with wrong field type."""
        data = {
            "name": "John Doe",
            "age": "thirty"  # Should be integer
        }
        
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            }
        }
        
        is_valid, errors = SchemaGenerator.validate_against_schema(data, schema)
        
        assert not is_valid
        assert len(errors) > 0
        assert any("Type mismatch" in error for error in errors)
    
    def test_validate_against_schema_array_items(self):
        """Test validation of array items."""
        data = {
            "scores": [85, 92, 78]
        }
        
        schema = {
            "type": "object",
            "properties": {
                "scores": {
                    "type": "array",
                    "items": {"type": "integer"}
                }
            }
        }
        
        is_valid, errors = SchemaGenerator.validate_against_schema(data, schema)
        
        assert is_valid
        assert len(errors) == 0
    
    def test_get_json_type(self):
        """Test JSON type detection."""
        assert SchemaGenerator._get_json_type(True) == "boolean"
        assert SchemaGenerator._get_json_type(42) == "integer"
        assert SchemaGenerator._get_json_type(3.14) == "number"
        assert SchemaGenerator._get_json_type("hello") == "string"
        assert SchemaGenerator._get_json_type([1, 2, 3]) == "array"
        assert SchemaGenerator._get_json_type({"key": "value"}) == "object"
        assert SchemaGenerator._get_json_type(None) == "null"
