"""
Advanced JSON data extraction utilities.
"""

import re
from typing import Any, Callable, Dict, List, Optional, Union


class JSONExtractor:
    """
    Advanced utilities for extracting specific data from JSON structures.
    """

    @staticmethod
    def extract_by_path(data: Dict[str, Any], path: str, default: Any = None) -> Any:
        """
        Extract data using JSONPath-like syntax.

        Args:
            data: JSON data to extract from
            path: Path string (e.g., "user.profile.name" or "items[0].id")
            default: Default value if path not found

        Returns:
            Extracted value or default
        """
        try:
            current = data

            # Split path and handle array indices
            parts = re.split(r"[\.\[\]]", path)
            parts = [part for part in parts if part]  # Remove empty strings

            for part in parts:
                if part.isdigit():
                    # Array index
                    current = current[int(part)]
                else:
                    # Object key
                    current = current[part]

            return current
        except (KeyError, IndexError, TypeError):
            return default

    @staticmethod
    def extract_multiple_paths(
        data: Dict[str, Any], paths: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Extract multiple values using path mappings.

        Args:
            data: JSON data to extract from
            paths: Dictionary mapping result keys to extraction paths

        Returns:
            Dictionary with extracted values
        """
        result = {}
        for result_key, path in paths.items():
            result[result_key] = JSONExtractor.extract_by_path(data, path)
        return result

    @staticmethod
    def find_all_values(data: Any, key: str) -> List[Any]:
        """
        Find all values for a given key in nested JSON structure.

        Args:
            data: JSON data to search
            key: Key to search for

        Returns:
            List of all values found for the key
        """
        results = []

        def _search_recursive(obj: Any) -> None:
            if isinstance(obj, dict):
                if key in obj:
                    results.append(obj[key])
                for value in obj.values():
                    _search_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    _search_recursive(item)

        _search_recursive(data)
        return results

    @staticmethod
    def find_by_condition(data: Any, condition: Callable[[Any], bool]) -> List[Any]:
        """
        Find all values that match a condition function.

        Args:
            data: JSON data to search
            condition: Function that returns True for matching values

        Returns:
            List of matching values
        """
        results = []

        def _search_recursive(obj: Any) -> None:
            if condition(obj):
                results.append(obj)

            if isinstance(obj, dict):
                for value in obj.values():
                    _search_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    _search_recursive(item)

        _search_recursive(data)
        return results

    @staticmethod
    def extract_text_content(data: Any) -> List[str]:
        """
        Extract all string values from JSON structure.

        Args:
            data: JSON data to extract from

        Returns:
            List of all string values found
        """
        return JSONExtractor.find_by_condition(data, lambda x: isinstance(x, str))

    @staticmethod
    def extract_numeric_content(data: Any) -> List[Union[int, float]]:
        """
        Extract all numeric values from JSON structure.

        Args:
            data: JSON data to extract from

        Returns:
            List of all numeric values found
        """
        return JSONExtractor.find_by_condition(
            data, lambda x: isinstance(x, (int, float))
        )

    @staticmethod
    def extract_by_pattern(
        data: Any, pattern: str, field: Optional[str] = None
    ) -> List[Any]:
        """
        Extract values matching a regex pattern.

        Args:
            data: JSON data to search
            pattern: Regex pattern to match
            field: Specific field to search in (if None, searches all string values)

        Returns:
            List of matching values
        """
        regex = re.compile(pattern)
        results = []

        def _search_recursive(obj: Any, current_field: str = "") -> None:
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if field is None or key == field:
                        if isinstance(value, str) and regex.search(value):
                            results.append(value)
                    _search_recursive(value, key)
            elif isinstance(obj, list):
                for item in obj:
                    _search_recursive(item, current_field)
            elif isinstance(obj, str) and (field is None or current_field == field):
                if regex.search(obj):
                    results.append(obj)

        _search_recursive(data)
        return results

    @staticmethod
    def extract_schema_info(data: Any) -> Dict[str, Any]:
        """
        Extract schema information from JSON data.

        Args:
            data: JSON data to analyze

        Returns:
            Schema information including types, structure, and statistics
        """
        schema_info = {"type": type(data).__name__, "structure": {}, "statistics": {}}

        def _analyze_recursive(obj: Any, path: str = "") -> Dict[str, Any]:
            if isinstance(obj, dict):
                structure = {}
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    structure[key] = _analyze_recursive(value, current_path)
                return {
                    "type": "object",
                    "properties": structure,
                    "key_count": len(obj),
                }

            elif isinstance(obj, list):
                if not obj:
                    return {"type": "array", "items": None, "length": 0}

                # Analyze first few items to determine array item type
                item_types = set()
                for item in obj[:5]:  # Sample first 5 items
                    item_types.add(type(item).__name__)

                return {
                    "type": "array",
                    "items": _analyze_recursive(obj[0]) if obj else None,
                    "length": len(obj),
                    "item_types": list(item_types),
                }

            else:
                return {
                    "type": type(obj).__name__,
                    "value": (
                        obj if isinstance(obj, (str, int, float, bool)) else str(obj)
                    ),
                }

        schema_info["structure"] = _analyze_recursive(data)

        # Calculate statistics
        all_strings = JSONExtractor.extract_text_content(data)
        all_numbers = JSONExtractor.extract_numeric_content(data)

        schema_info["statistics"] = {
            "total_string_values": len(all_strings),
            "total_numeric_values": len(all_numbers),
            "avg_string_length": (
                sum(len(s) for s in all_strings) / len(all_strings)
                if all_strings
                else 0
            ),
            "numeric_range": {
                "min": min(all_numbers) if all_numbers else None,
                "max": max(all_numbers) if all_numbers else None,
            },
        }

        return schema_info

    @staticmethod
    def extract_ai_entities(data: Any, entity_types: List[str]) -> Dict[str, List[str]]:
        """
        Extract entities that might be relevant for AI processing.

        Args:
            data: JSON data to extract from
            entity_types: Types of entities to look for
                (e.g., ['email', 'url', 'phone'])

        Returns:
            Dictionary mapping entity types to found values
        """
        patterns = {
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "url": r"https?://[^\s]+",
            "phone": (r"(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}"),
            "ip": r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",
            "date": (
                r"\b\d{4}-\d{2}-\d{2}\b|\b\d{2}/\d{2}/\d{4}\b|" r"\b\d{2}-\d{2}-\d{4}\b"
            ),
            "time": r"\b\d{1,2}:\d{2}(?::\d{2})?\s?(?:AM|PM|am|pm)?\b",
            "uuid": r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b",
            "hashtag": r"#\w+",
            "mention": r"@\w+",
            "currency": r"\$\d+(?:\.\d{2})?|\d+(?:\.\d{2})?\s?(?:USD|EUR|GBP|JPY)",
        }

        results = {}
        all_text = JSONExtractor.extract_text_content(data)
        combined_text = " ".join(all_text)

        for entity_type in entity_types:
            if entity_type in patterns:
                matches = re.findall(
                    patterns[entity_type], combined_text, re.IGNORECASE
                )
                results[entity_type] = list(set(matches))  # Remove duplicates
            else:
                results[entity_type] = []

        return results

    @staticmethod
    def extract_nested_arrays(data: Any, min_depth: int = 2) -> List[List[Any]]:
        """
        Extract nested arrays from JSON structure.

        Args:
            data: JSON data to search
            min_depth: Minimum nesting depth to consider

        Returns:
            List of nested arrays found
        """
        results = []

        def _search_recursive(obj: Any, array_depth: int = 0) -> None:
            if isinstance(obj, list):
                current_depth = array_depth + 1

                # If we've reached the minimum depth, add this array
                if current_depth >= min_depth:
                    results.append(obj)

                # Continue searching deeper
                for item in obj:
                    _search_recursive(item, current_depth)
            elif isinstance(obj, dict):
                for value in obj.values():
                    _search_recursive(value, array_depth)

        _search_recursive(data)
        return results
