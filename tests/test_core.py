"""
Tests for the core JSONHandler functionality.
"""

import json
import tempfile
from pathlib import Path

import pytest

from pyjsonkit.core import JSONHandler


class TestJSONHandler:
    """Test cases for JSONHandler class."""

    def test_init_with_existing_file(self):
        """Test initialization with an existing JSON file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"test": "value"}, f)
            temp_path = f.name

        try:
            handler = JSONHandler(temp_path)
            assert handler.get("test") == "value"
        finally:
            Path(temp_path).unlink()

    def test_init_with_new_file(self):
        """Test initialization with a new file path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "new_file.json"
            handler = JSONHandler(file_path)

            assert file_path.exists()
            assert len(handler) == 0

    def test_get_and_set(self):
        """Test getting and setting values."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test.json"
            handler = JSONHandler(file_path)

            # Test setting and getting
            handler.set("key1", "value1")
            assert handler.get("key1") == "value1"

            # Test default value
            assert handler.get("nonexistent", "default") == "default"

    def test_delete(self):
        """Test deleting keys."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test.json"
            handler = JSONHandler(file_path)

            handler.set("key1", "value1")
            handler.set("key2", "value2")

            # Test successful deletion
            assert handler.delete("key1") is True
            assert "key1" not in handler
            assert handler.get("key1") is None

            # Test deletion of non-existent key
            assert handler.delete("nonexistent") is False

    def test_clear(self):
        """Test clearing all data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test.json"
            handler = JSONHandler(file_path)

            handler.set("key1", "value1")
            handler.set("key2", "value2")

            handler.clear()
            assert len(handler) == 0
            assert list(handler.keys()) == []

    def test_keys_values_items(self):
        """Test keys, values, and items methods."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test.json"
            handler = JSONHandler(file_path)

            test_data = {"a": 1, "b": 2, "c": 3}
            handler.update(test_data)

            assert set(handler.keys()) == set(test_data.keys())
            assert set(handler.values()) == set(test_data.values())
            assert set(handler.items()) == set(test_data.items())

    def test_update(self):
        """Test updating with new data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test.json"
            handler = JSONHandler(file_path)

            handler.set("existing", "value")
            handler.update({"new": "data", "existing": "updated"})

            assert handler.get("new") == "data"
            assert handler.get("existing") == "updated"

    def test_validate(self):
        """Test JSON validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test.json"
            handler = JSONHandler(file_path)

            # Valid JSON data
            handler.set("key", "value")
            assert handler.validate() is True

    def test_pretty_print(self):
        """Test pretty printing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test.json"
            handler = JSONHandler(file_path)

            handler.set("key", "value")
            pretty = handler.pretty_print()

            assert "key" in pretty
            assert "value" in pretty
            assert pretty.count("\n") > 0  # Should be formatted

    def test_magic_methods(self):
        """Test magic methods."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test.json"
            handler = JSONHandler(file_path)

            handler.set("key", "value")

            # Test __len__
            assert len(handler) == 1

            # Test __contains__
            assert "key" in handler
            assert "nonexistent" not in handler

            # Test __str__
            str_repr = str(handler)
            assert "key" in str_repr
            assert "value" in str_repr

            # Test __repr__
            repr_str = repr(handler)
            assert "JSONHandler" in repr_str
            assert str(file_path) in repr_str

    def test_invalid_json_file(self):
        """Test handling of invalid JSON files."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("invalid json content")
            temp_path = f.name

        try:
            with pytest.raises(json.JSONDecodeError):
                JSONHandler(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_to_dict(self):
        """Test converting to dictionary."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test.json"
            handler = JSONHandler(file_path)

            test_data = {"a": 1, "b": 2}
            handler.update(test_data)

            result = handler.to_dict()
            assert result == test_data
            assert result is not handler._data  # Should be a copy
