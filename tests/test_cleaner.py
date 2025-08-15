"""
Tests for JSON cleaner functionality.
"""

import pytest
from pyjsonkit.cleaner import JSONCleaner


class TestJSONCleaner:
    """Test cases for JSONCleaner class."""
    
    def test_remove_null_values_simple(self):
        """Test removing null values from simple structure."""
        data = {
            "name": "John",
            "age": None,
            "email": "john@example.com",
            "phone": None
        }
        
        result = JSONCleaner.remove_null_values(data)
        
        assert "name" in result
        assert "email" in result
        assert "age" not in result
        assert "phone" not in result
    
    def test_remove_null_values_nested(self):
        """Test removing null values from nested structure."""
        data = {
            "user": {
                "name": "John",
                "age": None,
                "profile": {
                    "bio": None,
                    "website": "example.com"
                }
            },
            "items": [1, None, 3, None, 5]
        }
        
        result = JSONCleaner.remove_null_values(data)
        
        assert result["user"]["name"] == "John"
        assert "age" not in result["user"]
        assert result["user"]["profile"]["website"] == "example.com"
        assert "bio" not in result["user"]["profile"]
        assert result["items"] == [1, 3, 5]
    
    def test_remove_null_values_non_recursive(self):
        """Test removing null values without recursion."""
        data = {
            "name": "John",
            "age": None,
            "nested": {"value": None}
        }
        
        result = JSONCleaner.remove_null_values(data, recursive=False)
        
        assert "age" not in result
        assert result["nested"]["value"] is None  # Should remain
    
    def test_remove_empty_values(self):
        """Test removing empty values."""
        data = {
            "name": "John",
            "email": "",
            "tags": [],
            "metadata": {},
            "age": 0,  # Should remain (0 is not empty)
            "active": False  # Should remain (False is not empty)
        }
        
        result = JSONCleaner.remove_empty_values(data)
        
        assert "name" in result
        assert "age" in result
        assert "active" in result
        assert "email" not in result
        assert "tags" not in result
        assert "metadata" not in result
    
    def test_remove_empty_values_nested(self):
        """Test removing empty values from nested structure."""
        data = {
            "user": {
                "name": "John",
                "bio": "",
                "tags": []
            },
            "items": [
                {"name": "Item 1", "description": ""},
                {"name": "", "description": "Valid desc"}
            ]
        }
        
        result = JSONCleaner.remove_empty_values(data)
        
        assert result["user"]["name"] == "John"
        assert "bio" not in result["user"]
        assert "tags" not in result["user"]
        assert len(result["items"]) == 2
        assert "description" not in result["items"][0]
        assert "name" not in result["items"][1]
    
    def test_normalize_strings_strip(self):
        """Test normalizing strings with whitespace stripping."""
        data = {
            "name": "  John Doe  ",
            "items": ["  item1  ", "  item2  "]
        }
        
        result = JSONCleaner.normalize_strings(data, strip_whitespace=True)
        
        assert result["name"] == "John Doe"
        assert result["items"] == ["item1", "item2"]
    
    def test_normalize_strings_case(self):
        """Test normalizing strings with case conversion."""
        data = {
            "name": "John Doe",
            "email": "JOHN@EXAMPLE.COM"
        }
        
        result = JSONCleaner.normalize_strings(data, normalize_case="lower")
        
        assert result["name"] == "john doe"
        assert result["email"] == "john@example.com"
    
    def test_normalize_strings_extra_spaces(self):
        """Test normalizing strings by removing extra spaces."""
        data = {
            "description": "This   has    multiple     spaces"
        }
        
        result = JSONCleaner.normalize_strings(data, remove_extra_spaces=True)
        
        assert result["description"] == "This has multiple spaces"
    
    def test_sanitize_for_ai_remove_sensitive(self):
        """Test sanitizing data by removing sensitive information."""
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "555-123-4567",
            "ssn": "123-45-6789",
            "credit_card": "1234 5678 9012 3456"
        }
        
        result = JSONCleaner.sanitize_for_ai(data, remove_sensitive=True)
        
        assert result["name"] == "John Doe"  # Should remain
        assert "[REDACTED]" in result["email"]
        assert "[REDACTED]" in result["phone"]
        assert "[REDACTED]" in result["ssn"]
        assert "[REDACTED]" in result["credit_card"]
    
    def test_sanitize_for_ai_max_length(self):
        """Test sanitizing data with maximum string length."""
        data = {
            "short": "Short text",
            "long": "This is a very long text that should be truncated because it exceeds the maximum length"
        }
        
        result = JSONCleaner.sanitize_for_ai(data, max_string_length=20)
        
        assert result["short"] == "Short text"
        assert len(result["long"]) <= 23  # 20 + "..."
        assert result["long"].endswith("...")
    
    def test_sanitize_for_ai_allowed_keys(self):
        """Test sanitizing data with allowed keys filter."""
        data = {
            "name": "John",
            "age": 30,
            "secret": "confidential",
            "public_info": "available"
        }
        
        allowed_keys = {"name", "age", "public_info"}
        result = JSONCleaner.sanitize_for_ai(data, allowed_keys=allowed_keys)
        
        assert "name" in result
        assert "age" in result
        assert "public_info" in result
        assert "secret" not in result
    
    def test_deduplicate_arrays_simple(self):
        """Test deduplicating simple arrays."""
        data = {
            "numbers": [1, 2, 2, 3, 1, 4],
            "strings": ["a", "b", "a", "c", "b"]
        }
        
        result = JSONCleaner.deduplicate_arrays(data)
        
        assert len(result["numbers"]) == 4  # 1, 2, 3, 4
        assert len(result["strings"]) == 3  # a, b, c
        assert set(result["numbers"]) == {1, 2, 3, 4}
        assert set(result["strings"]) == {"a", "b", "c"}
    
    def test_deduplicate_arrays_complex(self):
        """Test deduplicating arrays with complex objects."""
        data = {
            "items": [
                {"id": 1, "name": "Item 1"},
                {"id": 2, "name": "Item 2"},
                {"id": 1, "name": "Item 1"},  # Duplicate
                {"id": 3, "name": "Item 3"}
            ]
        }
        
        result = JSONCleaner.deduplicate_arrays(data)
        
        assert len(result["items"]) == 3
        ids = [item["id"] for item in result["items"]]
        assert set(ids) == {1, 2, 3}
    
    def test_fix_encoding_issues(self):
        """Test fixing common encoding issues."""
        data = {
            "text1": "Donâ€™t worry",  # Should become "Don't worry"
            "text2": "â€œHelloâ€",      # Should become "Hello"
            "text3": "Caf\u00e9"        # Should remain as café
        }
        
        result = JSONCleaner.fix_encoding_issues(data)
        
        assert "'" in result["text1"]
        assert '"' in result["text2"]
    
    def test_standardize_dates(self):
        """Test standardizing date formats."""
        data = {
            "date1": "2023-12-25",      # Already correct
            "date2": "12/25/2023",      # MM/DD/YYYY
            "date3": "12-25-2023",      # MM-DD-YYYY
            "text": "Meeting on 01/15/2024 and 2024-02-20"
        }
        
        result = JSONCleaner.standardize_dates(data, target_format="%Y-%m-%d")
        
        assert result["date1"] == "2023-12-25"
        assert "2023-12-25" in result["date2"]
        assert "2023-12-25" in result["date3"]
        assert "2024-01-15" in result["text"]
        assert "2024-02-20" in result["text"]
    
    def test_clean_ai_artifacts(self):
        """Test cleaning AI-generated artifacts."""
        data = {
            "response": "[AI_GENERATED] Here is the answer [TODO: verify this]",
            "code": "```json\n{\"key\": \"value\"}\n```",
            "note": "This is important. Note: This is just an example."
        }
        
        result = JSONCleaner.clean_ai_artifacts(data)
        
        assert "[AI_GENERATED]" not in result["response"]
        assert "[TODO:" not in result["response"]
        assert "```" not in result["code"]
        assert "Note:" not in result["note"]
    
    def test_clean_ai_artifacts_nested(self):
        """Test cleaning AI artifacts from nested structure."""
        data = {
            "user": {
                "name": "[PLACEHOLDER] John Doe",
                "bio": "Software developer. Please note: this is auto-generated."
            },
            "items": [
                "Item 1 [EXAMPLE]",
                "Item 2"
            ]
        }
        
        result = JSONCleaner.clean_ai_artifacts(data)
        
        assert "[PLACEHOLDER]" not in result["user"]["name"]
        assert "Please note:" not in result["user"]["bio"]
        assert "[EXAMPLE]" not in result["items"][0]
        assert result["items"][1] == "Item 2"  # Should remain unchanged

    def test_comprehensive_cleaning(self):
        """Test comprehensive cleaning with multiple operations."""
        data = {
            "name": "  [AI_GENERATED] John Doe  ",
            "email": None,
            "tags": [],
            "description": "This   has    multiple     spaces",
            "metadata": {
                "created": None,
                "notes": ""
            }
        }

        # Apply multiple cleaning operations
        result = data
        result = JSONCleaner.remove_null_values(result)
        result = JSONCleaner.remove_empty_values(result)
        result = JSONCleaner.normalize_strings(result, strip_whitespace=True, remove_extra_spaces=True)
        result = JSONCleaner.clean_ai_artifacts(result)

        assert result["name"] == "John Doe"
        assert "email" not in result
        assert "tags" not in result
        assert result["description"] == "This has multiple spaces"
        assert "metadata" not in result  # Should be removed as it becomes empty
