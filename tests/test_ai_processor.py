"""
Tests for AI JSON processor functionality.
"""

import json
import pytest
from pyjsonkit.ai_processor import AIJSONProcessor


class TestAIJSONProcessor:
    """Test cases for AIJSONProcessor class."""
    
    def test_extract_json_from_text_code_block(self):
        """Test extracting JSON from markdown code blocks."""
        text = '''
        Here's the JSON data:
        ```json
        {"name": "John", "age": 30}
        ```
        That's the data.
        '''
        
        result = AIJSONProcessor.extract_json_from_text(text)
        assert result == {"name": "John", "age": 30}
    
    def test_extract_json_from_text_generic_block(self):
        """Test extracting JSON from generic code blocks."""
        text = '''
        ```
        {"status": "success", "data": [1, 2, 3]}
        ```
        '''
        
        result = AIJSONProcessor.extract_json_from_text(text)
        assert result == {"status": "success", "data": [1, 2, 3]}
    
    def test_extract_json_from_text_multiple(self):
        """Test extracting multiple JSON objects."""
        text = '''
        First object: {"a": 1}
        Second object: {"b": 2}
        '''
        
        results = AIJSONProcessor.extract_json_from_text(text, multiple=True)
        assert len(results) == 2
        assert {"a": 1} in results
        assert {"b": 2} in results
    
    def test_extract_json_from_text_no_json(self):
        """Test handling text with no JSON."""
        text = "This is just plain text with no JSON."
        
        result = AIJSONProcessor.extract_json_from_text(text)
        assert result is None
    
    def test_fix_common_ai_json_errors_trailing_commas(self):
        """Test fixing trailing commas."""
        malformed = '{"name": "John", "age": 30,}'
        fixed = AIJSONProcessor.fix_common_ai_json_errors(malformed)
        
        # Should be valid JSON now
        parsed = json.loads(fixed)
        assert parsed == {"name": "John", "age": 30}
    
    def test_fix_common_ai_json_errors_single_quotes(self):
        """Test fixing single quotes."""
        malformed = "{'name': 'John', 'age': 30}"
        fixed = AIJSONProcessor.fix_common_ai_json_errors(malformed)
        
        parsed = json.loads(fixed)
        assert parsed == {"name": "John", "age": 30}
    
    def test_fix_common_ai_json_errors_python_booleans(self):
        """Test fixing Python-style booleans."""
        malformed = '{"active": True, "deleted": False, "data": None}'
        fixed = AIJSONProcessor.fix_common_ai_json_errors(malformed)
        
        parsed = json.loads(fixed)
        assert parsed == {"active": True, "deleted": False, "data": None}
    
    def test_fix_common_ai_json_errors_unquoted_keys(self):
        """Test fixing unquoted keys."""
        malformed = '{name: "John", age: 30}'
        fixed = AIJSONProcessor.fix_common_ai_json_errors(malformed)
        
        parsed = json.loads(fixed)
        assert parsed == {"name": "John", "age": 30}
    
    def test_parse_ai_response_success(self):
        """Test successful AI response parsing."""
        response = '''
        Here's the requested data:
        ```json
        {"name": "Alice", "score": 95, "passed": true}
        ```
        '''
        
        result = AIJSONProcessor.parse_ai_response(response, ["name", "score"])
        assert result["name"] == "Alice"
        assert result["score"] == 95
        assert result["passed"] is True
    
    def test_parse_ai_response_missing_keys(self):
        """Test AI response parsing with missing required keys."""
        response = '{"name": "Alice"}'
        
        with pytest.raises(ValueError, match="Missing required keys"):
            AIJSONProcessor.parse_ai_response(response, ["name", "age"])
    
    def test_parse_ai_response_no_json(self):
        """Test AI response parsing with no valid JSON."""
        response = "This is just text without any JSON data."
        
        with pytest.raises(ValueError, match="No valid JSON found"):
            AIJSONProcessor.parse_ai_response(response)
    
    def test_batch_process_ai_responses(self):
        """Test batch processing of AI responses."""
        responses = [
            '{"name": "Alice", "score": 95}',
            '{"name": "Bob", "score": 87}',
            'Invalid response',
            '{"name": "Charlie", "score": 92}'
        ]
        
        results = AIJSONProcessor.batch_process_ai_responses(responses, ["name"])
        
        assert len(results) == 4
        assert results[0]["name"] == "Alice"
        assert results[1]["name"] == "Bob"
        assert results[2] == {}  # Failed parsing
        assert results[3]["name"] == "Charlie"
    
    def test_extract_structured_data_string(self):
        """Test extracting structured string data."""
        text = "The user's name is John Doe and their email is john@example.com"
        schema = {"name": "string", "email": "string"}
        
        result = AIJSONProcessor.extract_structured_data(text, schema)
        assert "name" in result
        assert "email" in result
    
    def test_extract_structured_data_number(self):
        """Test extracting structured numeric data."""
        text = "The temperature is 25.5 degrees and humidity is 60"
        schema = {"temperature": "number", "humidity": "number"}
        
        result = AIJSONProcessor.extract_structured_data(text, schema)
        assert result.get("temperature") == 25.5
        assert result.get("humidity") == 60
    
    def test_extract_structured_data_boolean(self):
        """Test extracting structured boolean data."""
        text = "Active: true, Verified: false"
        schema = {"Active": "boolean", "Verified": "boolean"}
        
        result = AIJSONProcessor.extract_structured_data(text, schema)
        assert result.get("Active") is True
        assert result.get("Verified") is False
    
    def test_extract_structured_data_list(self):
        """Test extracting structured list data."""
        text = "Skills: Python, JavaScript, SQL"
        schema = {"Skills": "list"}
        
        result = AIJSONProcessor.extract_structured_data(text, schema)
        assert "Skills" in result
        assert isinstance(result["Skills"], list)
        assert len(result["Skills"]) == 3
    
    def test_validate_ai_json_structure_valid(self):
        """Test validating valid AI JSON structure."""
        data = {
            "name": "John",
            "age": 30,
            "skills": ["Python", "JavaScript"]
        }
        
        structure = {
            "name": "string",
            "age": "number",
            "skills": ["string"]
        }
        
        is_valid, errors = AIJSONProcessor.validate_ai_json_structure(data, structure)
        assert is_valid
        assert len(errors) == 0
    
    def test_validate_ai_json_structure_invalid(self):
        """Test validating invalid AI JSON structure."""
        data = {
            "name": "John",
            "age": "thirty",  # Should be number
            "skills": "Python"  # Should be array
        }
        
        structure = {
            "name": "string",
            "age": "number",
            "skills": ["string"]
        }
        
        is_valid, errors = AIJSONProcessor.validate_ai_json_structure(data, structure)
        assert not is_valid
        assert len(errors) > 0
    
    def test_validate_ai_json_structure_missing_field(self):
        """Test validating structure with missing required field."""
        data = {"name": "John"}
        
        structure = {
            "name": "string",
            "age": "number"
        }
        
        is_valid, errors = AIJSONProcessor.validate_ai_json_structure(data, structure)
        assert not is_valid
        assert any("Missing required field" in error for error in errors)
