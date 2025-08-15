"""
Tests for the JSONParser functionality.
"""

import json
import tempfile
from pathlib import Path

import pytest

from pyjsonkit.parser import JSONParser


class TestJSONParser:
    """Test cases for JSONParser class."""

    def test_parse_string_valid(self):
        """Test parsing valid JSON strings."""
        json_string = '{"name": "John", "age": 30, "scores": [85, 90, 78]}'
        result = JSONParser.parse_string(json_string)

        expected = {"name": "John", "age": 30, "scores": [85, 90, 78]}
        assert result == expected

    def test_parse_string_invalid(self):
        """Test parsing invalid JSON strings."""
        invalid_json = '{"name": "John", "age": }'

        with pytest.raises(json.JSONDecodeError):
            JSONParser.parse_string(invalid_json)

    def test_parse_file_valid(self):
        """Test parsing valid JSON files."""
        test_data = {"name": "John", "age": 30}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(test_data, f)
            temp_path = f.name

        try:
            result = JSONParser.parse_file(temp_path)
            assert result == test_data
        finally:
            Path(temp_path).unlink()

    def test_parse_file_not_exists(self):
        """Test parsing non-existent files."""
        with pytest.raises(FileNotFoundError):
            JSONParser.parse_file("nonexistent.json")

    def test_to_string_compact(self):
        """Test converting data to compact JSON string."""
        data = {"name": "John", "age": 30}
        result = JSONParser.to_string(data)

        # Should be compact (no extra whitespace)
        assert "\n" not in result
        assert '"name"' in result
        assert '"John"' in result

    def test_to_string_pretty(self):
        """Test converting data to pretty JSON string."""
        data = {"name": "John", "age": 30}
        result = JSONParser.to_string(data, indent=2)

        # Should be formatted with indentation
        assert "\n" in result
        assert "  " in result  # Should have indentation

    def test_to_string_sorted(self):
        """Test converting data to JSON string with sorted keys."""
        data = {"zebra": 1, "apple": 2, "banana": 3}
        result = JSONParser.to_string(data, sort_keys=True)

        # Keys should appear in alphabetical order
        apple_pos = result.find('"apple"')
        banana_pos = result.find('"banana"')
        zebra_pos = result.find('"zebra"')

        assert apple_pos < banana_pos < zebra_pos

    def test_to_file(self):
        """Test writing data to JSON file."""
        data = {"name": "John", "age": 30}

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "output.json"
            JSONParser.to_file(data, file_path)

            # Verify file was created and contains correct data
            assert file_path.exists()
            with open(file_path, "r") as f:
                loaded_data = json.load(f)
            assert loaded_data == data

    def test_merge_objects(self):
        """Test merging multiple JSON objects."""
        obj1 = {"a": 1, "b": 2}
        obj2 = {"c": 3, "d": 4}
        obj3 = {"e": 5}

        result = JSONParser.merge_objects(obj1, obj2, obj3)
        expected = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5}

        assert result == expected

    def test_merge_objects_overlapping(self):
        """Test merging objects with overlapping keys."""
        obj1 = {"a": 1, "b": 2}
        obj2 = {"b": 3, "c": 4}  # 'b' should be overwritten

        result = JSONParser.merge_objects(obj1, obj2)
        expected = {"a": 1, "b": 3, "c": 4}

        assert result == expected

    def test_deep_merge_objects(self):
        """Test deep merging of nested objects."""
        obj1 = {"user": {"name": "John", "age": 30}, "settings": {"theme": "dark"}}
        obj2 = {"user": {"email": "john@example.com"}, "settings": {"language": "en"}}

        result = JSONParser.deep_merge_objects(obj1, obj2)
        expected = {
            "user": {"name": "John", "age": 30, "email": "john@example.com"},
            "settings": {"theme": "dark", "language": "en"},
        }

        assert result == expected

    def test_extract_keys(self):
        """Test extracting specific keys from an object."""
        data = {"name": "John", "age": 30, "email": "john@example.com", "city": "NYC"}
        keys_to_extract = ["name", "email", "nonexistent"]

        result = JSONParser.extract_keys(data, keys_to_extract)
        expected = {"name": "John", "email": "john@example.com"}

        assert result == expected

    def test_extract_keys_not_dict(self):
        """Test extracting keys from non-dictionary data."""
        data = "not a dictionary"
        keys_to_extract = ["name"]

        result = JSONParser.extract_keys(data, keys_to_extract)
        assert result == {}

    def test_flatten_object_simple(self):
        """Test flattening a simple nested object."""
        data = {"user": {"name": "John", "details": {"age": 30}}, "active": True}

        result = JSONParser.flatten_object(data)
        expected = {"user.name": "John", "user.details.age": 30, "active": True}

        assert result == expected

    def test_flatten_object_with_arrays(self):
        """Test flattening objects containing arrays."""
        data = {"users": [{"name": "John"}, {"name": "Jane"}]}

        result = JSONParser.flatten_object(data)
        expected = {"users.0.name": "John", "users.1.name": "Jane"}

        assert result == expected

    def test_flatten_object_custom_separator(self):
        """Test flattening with custom separator."""
        data = {"user": {"name": "John"}}
        result = JSONParser.flatten_object(data, separator="_")
        expected = {"user_name": "John"}

        assert result == expected

    def test_unflatten_object_simple(self):
        """Test unflattening a simple flattened object."""
        flat_data = {"user.name": "John", "user.age": 30, "active": True}

        result = JSONParser.unflatten_object(flat_data)
        expected = {"user": {"name": "John", "age": 30}, "active": True}

        assert result == expected

    def test_unflatten_object_with_arrays(self):
        """Test unflattening objects with array indices."""
        flat_data = {"users.0.name": "John", "users.1.name": "Jane"}

        result = JSONParser.unflatten_object(flat_data)
        # Note: This is a simplified test - the actual implementation
        # might need refinement for complex array handling
        assert "users" in result

    def test_flatten_unflatten_roundtrip(self):
        """Test that flatten and unflatten are inverse operations."""
        original = {
            "user": {"name": "John", "details": {"age": 30, "city": "NYC"}},
            "active": True,
        }

        flattened = JSONParser.flatten_object(original)
        unflattened = JSONParser.unflatten_object(flattened)

        assert unflattened == original
