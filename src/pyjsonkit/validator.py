"""
JSON validation utilities.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class JSONValidator:
    """
    A class for validating JSON data and files.
    """

    @staticmethod
    def validate_json_string(json_string: str) -> tuple[bool, Optional[str]]:
        """
        Validate a JSON string.

        Args:
            json_string: The JSON string to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            json.loads(json_string)
            return True, None
        except json.JSONDecodeError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    @staticmethod
    def validate_json_file(file_path: Union[str, Path]) -> tuple[bool, Optional[str]]:
        """
        Validate a JSON file.

        Args:
            file_path: Path to the JSON file

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return False, f"File does not exist: {file_path}"

            with open(file_path, "r", encoding="utf-8") as file:
                json.load(file)
            return True, None
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {str(e)}"
        except Exception as e:
            return False, f"Error reading file: {str(e)}"

    @staticmethod
    def validate_schema(data: Any, schema: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate JSON data against a simple schema.

        Args:
            data: The data to validate
            schema: Schema dictionary with expected structure

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        def _validate_recursive(obj: Any, schema_obj: Any, path: str = "") -> None:
            if isinstance(schema_obj, dict):
                if not isinstance(obj, dict):
                    errors.append(
                        f"Expected object at {path}, got {type(obj).__name__}"
                    )
                    return

                for key, expected_type in schema_obj.items():
                    current_path = f"{path}.{key}" if path else key

                    if key not in obj:
                        errors.append(f"Missing required key: {current_path}")
                        continue

                    _validate_recursive(obj[key], expected_type, current_path)

            elif isinstance(schema_obj, list):
                if not isinstance(obj, list):
                    errors.append(f"Expected array at {path}, got {type(obj).__name__}")
                    return

                if len(schema_obj) > 0:
                    # Validate each item against the first schema element
                    item_schema = schema_obj[0]
                    for i, item in enumerate(obj):
                        _validate_recursive(item, item_schema, f"{path}[{i}]")

            elif isinstance(schema_obj, type):
                if not isinstance(obj, schema_obj):
                    errors.append(
                        f"Expected {schema_obj.__name__} at {path}, "
                        f"got {type(obj).__name__}"
                    )

            elif schema_obj == "string":
                if not isinstance(obj, str):
                    errors.append(
                        f"Expected string at {path}, got {type(obj).__name__}"
                    )

            elif schema_obj == "number":
                if not isinstance(obj, (int, float)):
                    errors.append(
                        f"Expected number at {path}, got {type(obj).__name__}"
                    )

            elif schema_obj == "boolean":
                if not isinstance(obj, bool):
                    errors.append(
                        f"Expected boolean at {path}, got {type(obj).__name__}"
                    )

            elif schema_obj == "null":
                if obj is not None:
                    errors.append(f"Expected null at {path}, got {type(obj).__name__}")

        _validate_recursive(data, schema)
        return len(errors) == 0, errors

    @staticmethod
    def check_required_keys(
        data: Dict[str, Any], required_keys: List[str]
    ) -> tuple[bool, List[str]]:
        """
        Check if all required keys are present in the data.

        Args:
            data: The data dictionary to check
            required_keys: List of required keys

        Returns:
            Tuple of (all_present, missing_keys)
        """
        if not isinstance(data, dict):
            return False, ["Data is not a dictionary"]

        missing_keys = [key for key in required_keys if key not in data]
        return len(missing_keys) == 0, missing_keys

    @staticmethod
    def validate_json_types(data: Any) -> tuple[bool, List[str]]:
        """
        Validate that all values in the data are JSON-serializable types.

        Args:
            data: The data to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        def _check_types(obj: Any, path: str = "") -> None:
            if obj is None or isinstance(obj, (bool, int, float, str)):
                return
            elif isinstance(obj, dict):
                for key, value in obj.items():
                    if not isinstance(key, str):
                        errors.append(f"Non-string key at {path}: {type(key).__name__}")
                    current_path = f"{path}.{key}" if path else str(key)
                    _check_types(value, current_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    _check_types(item, f"{path}[{i}]")
            else:
                errors.append(
                    f"Non-JSON-serializable type at {path}: {type(obj).__name__}"
                )

        _check_types(data)
        return len(errors) == 0, errors
