"""
Tests for JSON extractor functionality.
"""

import pytest
from pyjsonkit.extractor import JSONExtractor


class TestJSONExtractor:
    """Test cases for JSONExtractor class."""
    
    @pytest.fixture
    def sample_data(self):
        """Sample JSON data for testing."""
        return {
            "user": {
                "name": "John Doe",
                "age": 30,
                "profile": {
                    "email": "john@example.com",
                    "phone": "123-456-7890"
                }
            },
            "items": [
                {"id": 1, "name": "Item 1", "price": 10.99},
                {"id": 2, "name": "Item 2", "price": 15.50}
            ],
            "metadata": {
                "created": "2023-01-01",
                "tags": ["important", "user-data"]
            }
        }
    
    def test_extract_by_path_simple(self, sample_data):
        """Test extracting data with simple path."""
        result = JSONExtractor.extract_by_path(sample_data, "user.name")
        assert result == "John Doe"
    
    def test_extract_by_path_nested(self, sample_data):
        """Test extracting data with nested path."""
        result = JSONExtractor.extract_by_path(sample_data, "user.profile.email")
        assert result == "john@example.com"
    
    def test_extract_by_path_array_index(self, sample_data):
        """Test extracting data with array index."""
        result = JSONExtractor.extract_by_path(sample_data, "items.0.name")
        assert result == "Item 1"
    
    def test_extract_by_path_not_found(self, sample_data):
        """Test extracting non-existent path."""
        result = JSONExtractor.extract_by_path(sample_data, "user.nonexistent")
        assert result is None
    
    def test_extract_by_path_with_default(self, sample_data):
        """Test extracting with default value."""
        result = JSONExtractor.extract_by_path(sample_data, "user.nonexistent", "default")
        assert result == "default"
    
    def test_extract_multiple_paths(self, sample_data):
        """Test extracting multiple paths."""
        paths = {
            "user_name": "user.name",
            "user_email": "user.profile.email",
            "first_item": "items.0.name"
        }
        
        result = JSONExtractor.extract_multiple_paths(sample_data, paths)
        
        assert result["user_name"] == "John Doe"
        assert result["user_email"] == "john@example.com"
        assert result["first_item"] == "Item 1"
    
    def test_find_all_values(self, sample_data):
        """Test finding all values for a key."""
        names = JSONExtractor.find_all_values(sample_data, "name")
        
        assert len(names) == 3  # user.name, item1.name, item2.name
        assert "John Doe" in names
        assert "Item 1" in names
        assert "Item 2" in names
    
    def test_find_by_condition(self, sample_data):
        """Test finding values by condition."""
        # Find all numeric values
        numbers = JSONExtractor.find_by_condition(
            sample_data, 
            lambda x: isinstance(x, (int, float))
        )
        
        assert 30 in numbers  # age
        assert 1 in numbers   # item id
        assert 2 in numbers   # item id
        assert 10.99 in numbers  # price
        assert 15.50 in numbers  # price
    
    def test_extract_text_content(self, sample_data):
        """Test extracting all text content."""
        text_values = JSONExtractor.extract_text_content(sample_data)
        
        assert "John Doe" in text_values
        assert "john@example.com" in text_values
        assert "Item 1" in text_values
        assert "important" in text_values
    
    def test_extract_numeric_content(self, sample_data):
        """Test extracting all numeric content."""
        numeric_values = JSONExtractor.extract_numeric_content(sample_data)
        
        assert 30 in numeric_values
        assert 1 in numeric_values
        assert 10.99 in numeric_values
    
    def test_extract_by_pattern_email(self, sample_data):
        """Test extracting values by regex pattern."""
        emails = JSONExtractor.extract_by_pattern(
            sample_data, 
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        )
        
        assert "john@example.com" in emails
    
    def test_extract_by_pattern_specific_field(self, sample_data):
        """Test extracting from specific field by pattern."""
        phones = JSONExtractor.extract_by_pattern(
            sample_data, 
            r'\d{3}-\d{3}-\d{4}',
            field="phone"
        )
        
        assert "123-456-7890" in phones
    
    def test_extract_schema_info(self, sample_data):
        """Test extracting schema information."""
        schema_info = JSONExtractor.extract_schema_info(sample_data)
        
        assert schema_info["type"] == "dict"
        assert "structure" in schema_info
        assert "statistics" in schema_info
        
        # Check statistics
        stats = schema_info["statistics"]
        assert stats["total_string_values"] > 0
        assert stats["total_numeric_values"] > 0
    
    def test_extract_ai_entities_email(self):
        """Test extracting AI entities - email."""
        data = {
            "contact": "Please reach out to support@example.com for help",
            "backup": "Also try admin@test.org"
        }
        
        entities = JSONExtractor.extract_ai_entities(data, ["email"])
        
        assert len(entities["email"]) == 2
        assert "support@example.com" in entities["email"]
        assert "admin@test.org" in entities["email"]
    
    def test_extract_ai_entities_url(self):
        """Test extracting AI entities - URL."""
        data = {
            "links": "Visit https://example.com or http://test.org for more info"
        }
        
        entities = JSONExtractor.extract_ai_entities(data, ["url"])
        
        assert len(entities["url"]) == 2
        assert "https://example.com" in entities["url"]
        assert "http://test.org" in entities["url"]
    
    def test_extract_ai_entities_phone(self):
        """Test extracting AI entities - phone."""
        data = {
            "contact": "Call us at (555) 123-4567 or 555-987-6543"
        }
        
        entities = JSONExtractor.extract_ai_entities(data, ["phone"])
        
        assert len(entities["phone"]) >= 1
    
    def test_extract_ai_entities_multiple(self):
        """Test extracting multiple AI entities."""
        data = {
            "info": "Contact john@example.com or visit https://example.com, call 555-123-4567"
        }
        
        entities = JSONExtractor.extract_ai_entities(data, ["email", "url", "phone"])
        
        assert len(entities["email"]) >= 1
        assert len(entities["url"]) >= 1
        assert len(entities["phone"]) >= 1
    
    def test_extract_nested_arrays(self):
        """Test extracting nested arrays."""
        data = {
            "level1": [
                [1, 2, 3],
                [4, 5, 6]
            ],
            "level2": [
                [
                    [7, 8],
                    [9, 10]
                ]
            ]
        }
        
        nested_arrays = JSONExtractor.extract_nested_arrays(data, min_depth=2)
        
        assert len(nested_arrays) >= 2
        assert [1, 2, 3] in nested_arrays
        assert [4, 5, 6] in nested_arrays
    
    def test_extract_nested_arrays_min_depth(self):
        """Test extracting nested arrays with minimum depth."""
        data = {
            "shallow": [1, 2, 3],  # depth 1
            "deep": [[4, 5], [6, 7]]  # depth 2
        }
        
        # Should only get the deep arrays
        nested_arrays = JSONExtractor.extract_nested_arrays(data, min_depth=2)
        
        assert [1, 2, 3] not in nested_arrays
        assert [4, 5] in nested_arrays
        assert [6, 7] in nested_arrays
