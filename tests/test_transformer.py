"""
Tests for JSON transformer functionality.
"""

import pytest
from pyjsonkit.transformer import JSONTransformer


class TestJSONTransformer:
    """Test cases for JSONTransformer class."""
    
    @pytest.fixture
    def training_data(self):
        """Sample training data."""
        return [
            {"feature1": 10, "feature2": "text1", "feature3": True, "label": 1},
            {"feature1": 20, "feature2": "text2", "feature3": False, "label": 0},
            {"feature1": 15, "feature2": "text3", "feature3": True, "label": 1}
        ]
    
    def test_reshape_for_training(self, training_data):
        """Test reshaping data for ML training."""
        input_keys = ["feature1", "feature2", "feature3"]
        output_keys = ["label"]
        
        result = JSONTransformer.reshape_for_training(training_data, input_keys, output_keys)
        
        assert "inputs" in result
        assert "outputs" in result
        assert "input_features" in result
        assert "output_features" in result
        
        assert len(result["inputs"]) == 3
        assert len(result["outputs"]) == 3
        assert result["input_features"] == input_keys
        assert result["output_features"] == output_keys
        
        # Check first row
        assert result["inputs"][0][0] == 10  # feature1
        assert result["inputs"][0][1] == 5   # feature2 length
        assert result["inputs"][0][2] == 1   # feature3 as int
        assert result["outputs"][0] == 1     # label
    
    def test_pivot_data(self):
        """Test pivoting data."""
        data = [
            {"category": "A", "month": "Jan", "sales": 100},
            {"category": "A", "month": "Feb", "sales": 150},
            {"category": "B", "month": "Jan", "sales": 200},
            {"category": "B", "month": "Feb", "sales": 250}
        ]
        
        result = JSONTransformer.pivot_data(data, "category", "month", "sales")
        
        assert "A" in result
        assert "B" in result
        assert result["A"]["Jan"] == 100
        assert result["A"]["Feb"] == 150
        assert result["B"]["Jan"] == 200
        assert result["B"]["Feb"] == 250
    
    def test_normalize_for_ai_prompt(self):
        """Test normalizing data for AI prompts."""
        data = {
            "user": {
                "name": "John Doe",
                "age": 30,
                "skills": ["Python", "JavaScript", "SQL"]
            },
            "projects": [
                {"name": "Project 1", "status": "completed"},
                {"name": "Project 2", "status": "in_progress"}
            ]
        }
        
        result = JSONTransformer.normalize_for_ai_prompt(data, max_depth=3, max_items=5)

        assert isinstance(result, str)
        assert "John Doe" in result
        # Skills array should be visible at depth 3
        assert "skills" in result
        assert "Project 1" in result
    
    def test_normalize_for_ai_prompt_truncation(self):
        """Test AI prompt normalization with truncation."""
        data = {
            "items": [f"Item {i}" for i in range(20)]  # More than max_items
        }
        
        result = JSONTransformer.normalize_for_ai_prompt(data, max_items=5)
        
        assert "Item 0" in result
        assert "Item 4" in result
        assert "... and 15 more items" in result
    
    def test_create_embeddings_format(self):
        """Test creating embeddings format."""
        data = [
            {"title": "Article 1", "content": "Content 1", "author": "John"},
            {"title": "Article 2", "content": "Content 2", "author": "Jane"}
        ]
        
        result = JSONTransformer.create_embeddings_format(
            data, 
            text_key="content", 
            metadata_keys=["title", "author"]
        )
        
        assert len(result) == 2
        assert result[0]["id"] == 0
        assert result[0]["text"] == "Content 1"
        assert result[0]["metadata"]["title"] == "Article 1"
        assert result[0]["metadata"]["author"] == "John"
    
    def test_convert_to_chat_format(self):
        """Test converting to chat format."""
        data = [
            {"role": "USER", "content": "Hello"},
            {"role": "ASSISTANT", "content": "Hi there!"},
            {"role": "USER", "content": "How are you?"}
        ]
        
        result = JSONTransformer.convert_to_chat_format(data)
        
        assert len(result) == 3
        assert result[0]["role"] == "user"
        assert result[0]["content"] == "Hello"
        assert result[1]["role"] == "assistant"
        assert result[1]["content"] == "Hi there!"
    
    def test_aggregate_by_key(self):
        """Test aggregating data by key."""
        data = [
            {"category": "A", "value": 10, "count": 1},
            {"category": "A", "value": 20, "count": 1},
            {"category": "B", "value": 15, "count": 2},
            {"category": "B", "value": 25, "count": 3}
        ]
        
        aggregations = {
            "value": "sum",
            "count": "avg"
        }
        
        result = JSONTransformer.aggregate_by_key(data, "category", aggregations)
        
        assert "A" in result
        assert "B" in result
        assert result["A"]["value"] == 30  # 10 + 20
        assert result["A"]["count"] == 1   # (1 + 1) / 2
        assert result["B"]["value"] == 40  # 15 + 25
        assert result["B"]["count"] == 2.5 # (2 + 3) / 2
    
    def test_aggregate_by_key_different_functions(self):
        """Test different aggregation functions."""
        data = [
            {"group": "X", "score": 85, "name": "Alice"},
            {"group": "X", "score": 92, "name": "Bob"},
            {"group": "Y", "score": 78, "name": "Charlie"}
        ]
        
        aggregations = {
            "score": "max",
            "name": "list"
        }
        
        result = JSONTransformer.aggregate_by_key(data, "group", aggregations)
        
        assert result["X"]["score"] == 92  # max of 85, 92
        assert len(result["X"]["name"]) == 2  # Alice, Bob
        assert "Alice" in result["X"]["name"]
        assert "Bob" in result["X"]["name"]
    
    def test_create_time_series(self):
        """Test creating time series data."""
        data = [
            {"timestamp": "2023-01-01", "value": 10},
            {"timestamp": "2023-01-01", "value": 15},
            {"timestamp": "2023-01-02", "value": 20},
            {"timestamp": "2023-01-02", "value": 25}
        ]
        
        result = JSONTransformer.create_time_series(data, "timestamp", "value", "day")
        
        assert len(result) == 2
        assert result[0]["timestamp"] == "2023-01-01"
        assert result[0]["count"] == 2
        assert result[0]["sum"] == 25  # 10 + 15
        assert result[0]["avg"] == 12.5
        
        assert result[1]["timestamp"] == "2023-01-02"
        assert result[1]["sum"] == 45  # 20 + 25
    
    def test_create_time_series_different_formats(self):
        """Test time series with different date formats."""
        data = [
            {"date": "01/15/2023", "sales": 100},
            {"date": "01/16/2023", "sales": 150}
        ]
        
        result = JSONTransformer.create_time_series(data, "date", "sales", "day")
        
        assert len(result) == 2
        assert result[0]["sum"] == 100
        assert result[1]["sum"] == 150
    
    def test_flatten_for_csv(self):
        """Test flattening for CSV export."""
        data = [
            {
                "name": "John",
                "address": {
                    "street": "123 Main St",
                    "city": "Anytown"
                },
                "hobbies": ["reading", "coding"]
            }
        ]
        
        result = JSONTransformer.flatten_for_csv(data)
        
        assert len(result) == 1
        flattened = result[0]
        
        assert flattened["name"] == "John"
        assert flattened["address_street"] == "123 Main St"
        assert flattened["address_city"] == "Anytown"
        assert "hobbies" in flattened  # Should be converted to string
    
    def test_flatten_for_csv_with_arrays(self):
        """Test flattening with array handling."""
        data = [
            {
                "user": "Alice",
                "scores": [85, 92, 78],
                "projects": [
                    {"name": "Project A", "status": "done"},
                    {"name": "Project B", "status": "pending"}
                ]
            }
        ]
        
        result = JSONTransformer.flatten_for_csv(data, separator=".")
        
        assert len(result) == 1
        flattened = result[0]
        
        assert flattened["user"] == "Alice"
        assert "scores" in flattened
        assert "projects.0.name" in flattened
        assert flattened["projects.0.name"] == "Project A"
        assert flattened["projects.1.status"] == "pending"
    
    def test_flatten_for_csv_max_depth(self):
        """Test flattening with maximum depth limit."""
        data = [
            {
                "level1": {
                    "level2": {
                        "level3": {
                            "level4": "deep_value"
                        }
                    }
                }
            }
        ]
        
        result = JSONTransformer.flatten_for_csv(data, max_depth=2)
        
        assert len(result) == 1
        flattened = result[0]
        
        # Should stop at max_depth and convert to string
        assert "level1_level2" in flattened
        assert isinstance(flattened["level1_level2"], str)
