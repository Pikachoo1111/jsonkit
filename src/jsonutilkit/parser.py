"""
JSON parsing utilities.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class JSONParser:
    """
    A class for parsing and manipulating JSON data.
    """

    @staticmethod
    def parse_string(json_string: str) -> Any:
        """
        Parse a JSON string.

        Args:
            json_string: The JSON string to parse

        Returns:
            Parsed JSON data

        Raises:
            json.JSONDecodeError: If the string is not valid JSON
        """
        return json.loads(json_string)

    @staticmethod
    def parse_file(file_path: Union[str, Path]) -> Any:
        """
        Parse a JSON file.

        Args:
            file_path: Path to the JSON file

        Returns:
            Parsed JSON data

        Raises:
            FileNotFoundError: If the file doesn't exist
            json.JSONDecodeError: If the file contains invalid JSON
        """
        file_path = Path(file_path)
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    @staticmethod
    def to_string(
        data: Any, indent: Optional[int] = None, sort_keys: bool = False
    ) -> str:
        """
        Convert data to a JSON string.

        Args:
            data: The data to convert
            indent: Number of spaces for indentation (None for compact)
            sort_keys: Whether to sort keys alphabetically

        Returns:
            JSON string representation
        """
        return json.dumps(data, indent=indent, sort_keys=sort_keys, ensure_ascii=False)

    @staticmethod
    def to_file(
        data: Any,
        file_path: Union[str, Path],
        indent: Optional[int] = 2,
        sort_keys: bool = False,
    ) -> None:
        """
        Write data to a JSON file.

        Args:
            data: The data to write
            file_path: Path to the output file
            indent: Number of spaces for indentation
            sort_keys: Whether to sort keys alphabetically
        """
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(
                data, file, indent=indent, sort_keys=sort_keys, ensure_ascii=False
            )

    @staticmethod
    def merge_objects(*objects: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge multiple JSON objects into one.

        Args:
            *objects: JSON objects to merge

        Returns:
            Merged JSON object
        """
        result = {}
        for obj in objects:
            if isinstance(obj, dict):
                result.update(obj)
        return result

    @staticmethod
    def deep_merge_objects(
        obj1: Dict[str, Any], obj2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Deep merge two JSON objects.

        Args:
            obj1: First object
            obj2: Second object (takes precedence)

        Returns:
            Deep merged JSON object
        """
        result = obj1.copy()

        for key, value in obj2.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = JSONParser.deep_merge_objects(result[key], value)
            else:
                result[key] = value

        return result

    @staticmethod
    def extract_keys(data: Any, keys: List[str]) -> Dict[str, Any]:
        """
        Extract specific keys from a JSON object.

        Args:
            data: The JSON object
            keys: List of keys to extract

        Returns:
            New object with only the specified keys
        """
        if not isinstance(data, dict):
            return {}

        return {key: data[key] for key in keys if key in data}

    @staticmethod
    def flatten_object(obj: Dict[str, Any], separator: str = ".") -> Dict[str, Any]:
        """
        Flatten a nested JSON object.

        Args:
            obj: The object to flatten
            separator: Separator for nested keys

        Returns:
            Flattened object
        """

        def _flatten(obj: Any, parent_key: str = "") -> Dict[str, Any]:
            items = []

            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_key = f"{parent_key}{separator}{key}" if parent_key else key
                    items.extend(_flatten(value, new_key).items())
            elif isinstance(obj, list):
                for i, value in enumerate(obj):
                    new_key = f"{parent_key}{separator}{i}" if parent_key else str(i)
                    items.extend(_flatten(value, new_key).items())
            else:
                return {parent_key: obj}

            return dict(items)

        return _flatten(obj)

    @staticmethod
    def unflatten_object(
        flat_obj: Dict[str, Any], separator: str = "."
    ) -> Dict[str, Any]:
        """
        Unflatten a flattened JSON object.

        Args:
            flat_obj: The flattened object
            separator: Separator used in flattened keys

        Returns:
            Unflattened nested object
        """
        result = {}

        for key, value in flat_obj.items():
            keys = key.split(separator)
            current = result

            for k in keys[:-1]:
                if k.isdigit():
                    k = int(k)
                    if not isinstance(current, list):
                        current = []
                    while len(current) <= k:
                        current.append({})
                    current = current[k]
                else:
                    if k not in current:
                        current[k] = {}
                    current = current[k]

            final_key = keys[-1]
            if final_key.isdigit():
                final_key = int(final_key)
                if not isinstance(current, list):
                    current = []
                while len(current) <= final_key:
                    current.append(None)
                current[final_key] = value
            else:
                current[final_key] = value

        return result
