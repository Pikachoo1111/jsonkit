"""
AI-focused JSON processing utilities for handling AI model outputs.
"""

import json
import re
from typing import Any, Dict, List, Optional, Tuple, Union


class AIJSONProcessor:
    """
    Specialized processor for handling JSON from AI models with common issues.
    """

    @staticmethod
    def extract_json_from_text(
        text: str, multiple: bool = False
    ) -> Union[Dict[str, Any], List[Dict[str, Any]], None]:
        """
        Extract JSON objects from AI-generated text that may contain extra content.

        Args:
            text: Text that may contain JSON
            multiple: If True, extract all JSON objects found

        Returns:
            Extracted JSON object(s) or None if no valid JSON found
        """
        # Common patterns for JSON in AI responses
        patterns = [
            r"```json\s*(\{.*?\})\s*```",  # JSON in code blocks
            r"```\s*(\{.*?\})\s*```",  # JSON in generic code blocks
            r"(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})",  # Balanced braces
            r"(\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\])",  # Balanced brackets
        ]

        results = []
        seen_objects = set()

        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.MULTILINE)
            for match in matches:
                try:
                    parsed = json.loads(match.strip())
                    if multiple:
                        # Use JSON string as key to avoid duplicates
                        json_str = json.dumps(parsed, sort_keys=True)
                        if json_str not in seen_objects:
                            seen_objects.add(json_str)
                            results.append(parsed)
                    else:
                        return parsed
                except json.JSONDecodeError:
                    continue

        # Try to find JSON-like structures without delimiters
        json_like_pattern = r"(\{(?:[^{}]|(?:\{[^{}]*\}))*\})"
        matches = re.findall(json_like_pattern, text)

        for match in matches:
            try:
                parsed = json.loads(match.strip())
                if multiple:
                    json_str = json.dumps(parsed, sort_keys=True)
                    if json_str not in seen_objects:
                        seen_objects.add(json_str)
                        results.append(parsed)
                else:
                    return parsed
            except json.JSONDecodeError:
                continue

        return results if multiple else None

    @staticmethod
    def fix_common_ai_json_errors(json_string: str) -> str:
        """
        Fix common JSON formatting errors made by AI models.

        Args:
            json_string: Potentially malformed JSON string

        Returns:
            Fixed JSON string
        """
        # Remove common prefixes/suffixes
        json_string = json_string.strip()

        # Remove markdown code block markers
        json_string = re.sub(r"^```(?:json)?\s*", "", json_string, flags=re.MULTILINE)
        json_string = re.sub(r"\s*```$", "", json_string, flags=re.MULTILINE)

        # Fix trailing commas
        json_string = re.sub(r",(\s*[}\]])", r"\1", json_string)

        # Fix single quotes to double quotes
        json_string = re.sub(r"'([^']*)':", r'"\1":', json_string)
        json_string = re.sub(r":\s*'([^']*)'", r': "\1"', json_string)

        # Fix unquoted keys
        json_string = re.sub(
            r"([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:", r'\1"\2":', json_string
        )

        # Fix Python-style booleans and None
        json_string = re.sub(r"\bTrue\b", "true", json_string)
        json_string = re.sub(r"\bFalse\b", "false", json_string)
        json_string = re.sub(r"\bNone\b", "null", json_string)

        return json_string.strip()

    @staticmethod
    def parse_ai_response(
        response: str, expected_keys: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Parse AI response and extract structured data with validation.

        Args:
            response: AI model response text
            expected_keys: List of keys that should be present

        Returns:
            Parsed and validated JSON data

        Raises:
            ValueError: If no valid JSON found or required keys missing
        """
        # Try to extract JSON
        extracted = AIJSONProcessor.extract_json_from_text(response)

        if extracted is None:
            # Try fixing common errors and parsing again
            fixed_response = AIJSONProcessor.fix_common_ai_json_errors(response)
            try:
                extracted = json.loads(fixed_response)
            except json.JSONDecodeError:
                raise ValueError("No valid JSON found in AI response")

        if not isinstance(extracted, dict):
            raise ValueError("Extracted JSON is not an object")

        # Validate expected keys
        if expected_keys:
            missing_keys = [key for key in expected_keys if key not in extracted]
            if missing_keys:
                raise ValueError(f"Missing required keys: {missing_keys}")

        return extracted

    @staticmethod
    def batch_process_ai_responses(
        responses: List[str], expected_keys: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Process multiple AI responses in batch.

        Args:
            responses: List of AI response strings
            expected_keys: List of keys that should be present in each response

        Returns:
            List of parsed JSON objects
        """
        results = []
        for i, response in enumerate(responses):
            try:
                parsed = AIJSONProcessor.parse_ai_response(response, expected_keys)
                results.append(parsed)
            except ValueError as e:
                print(f"Warning: Failed to parse response {i}: {e}")
                results.append({})

        return results

    @staticmethod
    def extract_structured_data(text: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured data from text based on a schema template.

        Args:
            text: Input text to extract data from
            schema: Schema defining the expected structure

        Returns:
            Extracted data matching the schema
        """
        result = {}

        for key, field_type in schema.items():
            if field_type == "string":
                # Extract string patterns
                patterns = [
                    rf"{key}[:\s]+([^\n,}}]+)",
                    rf'"{key}"[:\s]+"([^"]+)"',
                    rf"'{key}'[:\s]+'([^']+)'",
                ]
                for pattern in patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        result[key] = match.group(1).strip()
                        break

            elif field_type == "number":
                # Extract numeric values
                patterns = [
                    rf"{key}[:\s]+(\d+(?:\.\d+)?)",
                    rf"{key}[:\s]*is[:\s]*(\d+(?:\.\d+)?)",
                    rf"(\d+(?:\.\d+)?)[:\s]*{key}",
                ]
                for pattern in patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        try:
                            result[key] = (
                                float(match.group(1))
                                if "." in match.group(1)
                                else int(match.group(1))
                            )
                            break
                        except ValueError:
                            continue

            elif field_type == "boolean":
                # Extract boolean values
                pattern = rf"{key}[:\s]+(true|false|yes|no|True|False)"
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    value = match.group(1).lower()
                    result[key] = value in ["true", "yes"]

            elif field_type == "list":
                # Extract list patterns
                patterns = [
                    rf"{key}[:\s]*\[(.*?)\]",
                    rf"{key}[:\s]*([^\n]+(?:,\s*[^\n,]+)*)",
                ]
                for pattern in patterns:
                    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                    if match:
                        items_str = match.group(1)
                        # Split by comma and clean up
                        items = [
                            item.strip().strip("\"'") for item in items_str.split(",")
                        ]
                        result[key] = [item for item in items if item]
                        break

        return result

    @staticmethod
    def validate_ai_json_structure(
        data: Dict[str, Any], required_structure: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate that AI-generated JSON matches expected structure.

        Args:
            data: JSON data to validate
            required_structure: Expected structure definition

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        def _validate_recursive(obj: Any, structure: Any, path: str = "") -> None:
            if isinstance(structure, dict):
                if not isinstance(obj, dict):
                    errors.append(
                        f"Expected object at {path}, got {type(obj).__name__}"
                    )
                    return

                for key, expected in structure.items():
                    current_path = f"{path}.{key}" if path else key

                    if key not in obj:
                        errors.append(f"Missing required field: {current_path}")
                        continue

                    _validate_recursive(obj[key], expected, current_path)

            elif isinstance(structure, list) and len(structure) > 0:
                if not isinstance(obj, list):
                    errors.append(f"Expected array at {path}, got {type(obj).__name__}")
                    return

                # Validate each item against the first structure element
                item_structure = structure[0]
                for i, item in enumerate(obj):
                    _validate_recursive(item, item_structure, f"{path}[{i}]")

            elif structure == "string":
                if not isinstance(obj, str):
                    errors.append(
                        f"Expected string at {path}, got {type(obj).__name__}"
                    )

            elif structure == "number":
                if not isinstance(obj, (int, float)):
                    errors.append(
                        f"Expected number at {path}, got {type(obj).__name__}"
                    )

            elif structure == "boolean":
                if not isinstance(obj, bool):
                    errors.append(
                        f"Expected boolean at {path}, got {type(obj).__name__}"
                    )

            elif structure == "array":
                if not isinstance(obj, list):
                    errors.append(f"Expected array at {path}, got {type(obj).__name__}")

        _validate_recursive(data, required_structure)
        return len(errors) == 0, errors
