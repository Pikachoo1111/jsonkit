"""
Tests for the JSONValidator functionality.
"""

import json
import tempfile
from pathlib import Path

import pytest

from pyjsonkit.validator import JSONValidator


class TestJSONValidator:
    """Test cases for JSONValidator class."""

    def test_validate_json_string_valid(self):
        """Test validation of valid JSON strings."""
        valid_json = '{"key": "value", "number": 42, "array": [1, 2, 3]}'
        is_valid, error = JSONValidator.validate_json_string(valid_json)

        assert is_valid is True
        assert error is None

    def test_validate_json_string_invalid(self):
        """Test validation of invalid JSON strings."""
        invalid_json = '{"key": "value", "invalid": }'
        is_valid, error = JSONValidator.validate_json_string(invalid_json)

        assert is_valid is False
        assert error is not None
        assert isinstance(error, str)

    def test_validate_json_file_valid(self):
        """Test validation of valid JSON files."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"test": "data"}, f)
            temp_path = f.name

        try:
            is_valid, error = JSONValidator.validate_json_file(temp_path)
            assert is_valid is True
            assert error is None
        finally:
            Path(temp_path).unlink()

    def test_validate_json_file_invalid(self):
        """Test validation of invalid JSON files."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write('{"invalid": json}')
            temp_path = f.name

        try:
            is_valid, error = JSONValidator.validate_json_file(temp_path)
            assert is_valid is False
            assert error is not None
            assert "Invalid JSON" in error
        finally:
            Path(temp_path).unlink()

    def test_validate_json_file_not_exists(self):
        """Test validation of non-existent files."""
        is_valid, error = JSONValidator.validate_json_file("nonexistent.json")

        assert is_valid is False
        assert error is not None
        assert "does not exist" in error

    def test_validate_schema_valid(self):
        """Test schema validation with valid data."""
        data = {"name": "John", "age": 30, "active": True, "scores": [85, 90, 78]}

        schema = {
            "name": "string",
            "age": "number",
            "active": "boolean",
            "scores": ["number"],
        }

        is_valid, errors = JSONValidator.validate_schema(data, schema)
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_schema_invalid(self):
        """Test schema validation with invalid data."""
        data = {
            "name": 123,  # Should be string
            "age": "thirty",  # Should be number
            "scores": "not an array",  # Should be array
        }

        schema = {"name": "string", "age": "number", "scores": ["number"]}

        is_valid, errors = JSONValidator.validate_schema(data, schema)
        assert is_valid is False
        assert len(errors) > 0

    def test_validate_schema_missing_keys(self):
        """Test schema validation with missing required keys."""
        data = {
            "name": "John"
            # Missing "age" key
        }

        schema = {"name": "string", "age": "number"}

        is_valid, errors = JSONValidator.validate_schema(data, schema)
        assert is_valid is False
        assert any("Missing required key" in error for error in errors)

    def test_validate_schema_nested(self):
        """Test schema validation with nested objects."""
        data = {"user": {"name": "John", "details": {"age": 30}}}

        schema = {"user": {"name": "string", "details": {"age": "number"}}}

        is_valid, errors = JSONValidator.validate_schema(data, schema)
        assert is_valid is True
        assert len(errors) == 0

    def test_check_required_keys_valid(self):
        """Test checking required keys with valid data."""
        data = {"name": "John", "age": 30, "email": "john@example.com"}
        required_keys = ["name", "age"]

        all_present, missing = JSONValidator.check_required_keys(data, required_keys)
        assert all_present is True
        assert len(missing) == 0

    def test_check_required_keys_missing(self):
        """Test checking required keys with missing keys."""
        data = {"name": "John"}
        required_keys = ["name", "age", "email"]

        all_present, missing = JSONValidator.check_required_keys(data, required_keys)
        assert all_present is False
        assert set(missing) == {"age", "email"}

    def test_check_required_keys_not_dict(self):
        """Test checking required keys with non-dictionary data."""
        data = "not a dictionary"
        required_keys = ["name"]

        all_present, missing = JSONValidator.check_required_keys(data, required_keys)
        assert all_present is False
        assert "not a dictionary" in missing[0]

    def test_validate_json_types_valid(self):
        """Test validation of JSON-serializable types."""
        data = {
            "string": "text",
            "number": 42,
            "float": 3.14,
            "boolean": True,
            "null": None,
            "array": [1, 2, 3],
            "object": {"nested": "value"},
        }

        is_valid, errors = JSONValidator.validate_json_types(data)
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_json_types_invalid(self):
        """Test validation with non-JSON-serializable types."""

        class CustomClass:
            pass

        data = {
            "valid": "string",
            "invalid": CustomClass(),
            "also_invalid": set([1, 2, 3]),
        }

        is_valid, errors = JSONValidator.validate_json_types(data)
        assert is_valid is False
        assert len(errors) > 0

    def test_validate_json_types_non_string_keys(self):
        """Test validation with non-string keys."""
        data = {"valid_key": "value", 123: "invalid key type"}

        is_valid, errors = JSONValidator.validate_json_types(data)
        assert is_valid is False
        assert any("Non-string key" in error for error in errors)
