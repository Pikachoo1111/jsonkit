"""
JSON Schema generation utilities for AI data validation.
"""

from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Union


class SchemaGenerator:
    """
    Generate JSON schemas from data samples, especially useful for AI-generated content.
    """

    @staticmethod
    def generate_from_samples(
        samples: List[Dict[str, Any]],
        strict: bool = False,
        include_examples: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate JSON schema from multiple data samples.

        Args:
            samples: List of JSON objects to analyze
            strict: If True, all samples must have the same structure
            include_examples: Whether to include example values

        Returns:
            Generated JSON schema
        """
        if not samples:
            return {"type": "object"}

        # Analyze all samples
        schema_info = SchemaGenerator._analyze_samples(samples)

        # Generate schema
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {},
            "additionalProperties": not strict,
        }

        required_fields = []

        for field_name, field_info in schema_info.items():
            field_schema = SchemaGenerator._generate_field_schema(
                field_info, include_examples
            )
            schema["properties"][field_name] = field_schema

            # Mark as required if present in most samples
            # In strict mode, still only require fields present in most samples
            if field_info["presence_ratio"] > 0.8:
                required_fields.append(field_name)

        if required_fields:
            schema["required"] = required_fields

        return schema

    @staticmethod
    def _analyze_samples(samples: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Analyze samples to extract field information."""
        field_info = defaultdict(
            lambda: {
                "types": Counter(),
                "examples": [],
                "presence_count": 0,
                "null_count": 0,
                "nested_schemas": [],
            }
        )

        total_samples = len(samples)

        for sample in samples:
            if not isinstance(sample, dict):
                continue

            for field_name, value in sample.items():
                info = field_info[field_name]
                info["presence_count"] += 1

                if value is None:
                    info["null_count"] += 1
                    info["types"]["null"] += 1
                else:
                    value_type = SchemaGenerator._get_json_type(value)
                    info["types"][value_type] += 1

                    # Store examples (limit to avoid memory issues)
                    if len(info["examples"]) < 5:
                        info["examples"].append(value)

                    # Analyze nested objects
                    if isinstance(value, dict):
                        info["nested_schemas"].append(value)
                    elif (
                        isinstance(value, list) and value and isinstance(value[0], dict)
                    ):
                        info["nested_schemas"].extend(value)

        # Calculate presence ratios
        for field_name, info in field_info.items():
            info["presence_ratio"] = info["presence_count"] / total_samples

        return dict(field_info)

    @staticmethod
    def _get_json_type(value: Any) -> str:
        """Get JSON schema type for a value."""
        if isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "integer"
        elif isinstance(value, float):
            return "number"
        elif isinstance(value, str):
            return "string"
        elif isinstance(value, list):
            return "array"
        elif isinstance(value, dict):
            return "object"
        elif value is None:
            return "null"
        else:
            return "string"  # Default fallback

    @staticmethod
    def _generate_field_schema(
        field_info: Dict[str, Any], include_examples: bool
    ) -> Dict[str, Any]:
        """Generate schema for a single field."""
        types = field_info["types"]
        most_common_type = types.most_common(1)[0][0] if types else "string"

        # Handle multiple types
        if len(types) > 1:
            type_list = [t for t, count in types.most_common() if count > 0]
            if "null" in type_list and len(type_list) > 1:
                # Nullable field
                non_null_types = [t for t in type_list if t != "null"]
                if len(non_null_types) == 1:
                    field_schema = {"type": [non_null_types[0], "null"]}
                else:
                    field_schema = {"anyOf": [{"type": t} for t in type_list]}
            else:
                field_schema = {"anyOf": [{"type": t} for t in type_list]}
        else:
            field_schema = {"type": most_common_type}

        # Add format and constraints based on type
        if most_common_type == "string":
            SchemaGenerator._add_string_constraints(
                field_schema, field_info["examples"]
            )
        elif most_common_type in ["integer", "number"]:
            SchemaGenerator._add_numeric_constraints(
                field_schema, field_info["examples"]
            )
        elif most_common_type == "array":
            SchemaGenerator._add_array_constraints(field_schema, field_info["examples"])
        elif most_common_type == "object":
            SchemaGenerator._add_object_constraints(
                field_schema, field_info["nested_schemas"]
            )

        # Add examples
        if include_examples and field_info["examples"]:
            field_schema["examples"] = field_info["examples"][:3]  # Limit examples

        return field_schema

    @staticmethod
    def _add_string_constraints(schema: Dict[str, Any], examples: List[str]) -> None:
        """Add string-specific constraints to schema."""
        if not examples:
            return

        string_examples = [ex for ex in examples if isinstance(ex, str)]
        if not string_examples:
            return

        # Analyze string patterns
        lengths = [len(s) for s in string_examples]
        schema["minLength"] = min(lengths)
        schema["maxLength"] = max(lengths)

        # Check for common formats
        import re

        # Email pattern
        if all(re.match(r"^[^@]+@[^@]+\.[^@]+$", s) for s in string_examples):
            schema["format"] = "email"

        # Date pattern
        elif all(re.match(r"^\d{4}-\d{2}-\d{2}$", s) for s in string_examples):
            schema["format"] = "date"

        # URL pattern
        elif all(re.match(r"^https?://", s) for s in string_examples):
            schema["format"] = "uri"

        # UUID pattern
        elif all(
            re.match(
                r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
                s,
                re.I,
            )
            for s in string_examples
        ):
            schema["format"] = "uuid"

    @staticmethod
    def _add_numeric_constraints(
        schema: Dict[str, Any], examples: List[Union[int, float]]
    ) -> None:
        """Add numeric constraints to schema."""
        numeric_examples = [ex for ex in examples if isinstance(ex, (int, float))]
        if not numeric_examples:
            return

        schema["minimum"] = min(numeric_examples)
        schema["maximum"] = max(numeric_examples)

    @staticmethod
    def _add_array_constraints(
        schema: Dict[str, Any], examples: List[List[Any]]
    ) -> None:
        """Add array constraints to schema."""
        array_examples = [ex for ex in examples if isinstance(ex, list)]
        if not array_examples:
            return

        lengths = [len(arr) for arr in array_examples]
        schema["minItems"] = min(lengths)
        schema["maxItems"] = max(lengths)

        # Analyze item types
        all_items = []
        for arr in array_examples:
            all_items.extend(arr)

        if all_items:
            item_types = Counter(
                SchemaGenerator._get_json_type(item) for item in all_items
            )
            most_common_item_type = item_types.most_common(1)[0][0]
            schema["items"] = {"type": most_common_item_type}

    @staticmethod
    def _add_object_constraints(
        schema: Dict[str, Any], nested_objects: List[Dict[str, Any]]
    ) -> None:
        """Add object constraints to schema."""
        if not nested_objects:
            return

        # Generate schema for nested objects
        nested_schema = SchemaGenerator.generate_from_samples(
            nested_objects, strict=False, include_examples=False
        )
        if "properties" in nested_schema:
            schema["properties"] = nested_schema["properties"]
        if "required" in nested_schema:
            schema["required"] = nested_schema["required"]

    @staticmethod
    def generate_ai_prompt_schema(
        task_description: str,
        expected_fields: List[str],
        field_types: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a schema specifically for AI prompt responses.

        Args:
            task_description: Description of the AI task
            expected_fields: List of expected field names
            field_types: Optional mapping of field names to types

        Returns:
            JSON schema for AI responses
        """
        field_types = field_types or {}

        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": f"AI Response Schema: {task_description}",
            "type": "object",
            "properties": {},
            "required": expected_fields,
            "additionalProperties": False,
        }

        for field in expected_fields:
            field_type = field_types.get(field, "string")

            field_schema = {"type": field_type}

            # Add AI-specific constraints
            if field_type == "string":
                field_schema["minLength"] = 1
                field_schema["maxLength"] = 1000  # Reasonable limit for AI responses
            elif field_type == "array":
                field_schema["minItems"] = 0
                field_schema["maxItems"] = 100
                field_schema["items"] = {"type": "string"}
            elif field_type in ["integer", "number"]:
                field_schema["minimum"] = 0

            schema["properties"][field] = field_schema

        return schema

    @staticmethod
    def validate_against_schema(
        data: Any, schema: Dict[str, Any]
    ) -> tuple[bool, List[str]]:
        """
        Simple schema validation (basic implementation).

        Args:
            data: Data to validate
            schema: JSON schema to validate against

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        def _validate_recursive(
            obj: Any, schema_obj: Dict[str, Any], path: str = ""
        ) -> None:
            # Check type
            expected_type = schema_obj.get("type")
            if expected_type:
                if isinstance(expected_type, list):
                    obj_type = SchemaGenerator._get_json_type(obj)
                    if obj_type not in expected_type:
                        errors.append(
                            f"Type mismatch at {path}: expected "
                            f"{expected_type}, got {obj_type}"
                        )
                else:
                    obj_type = SchemaGenerator._get_json_type(obj)
                    if obj_type != expected_type:
                        errors.append(
                            f"Type mismatch at {path}: expected "
                            f"{expected_type}, got {obj_type}"
                        )

            # Validate object properties
            if isinstance(obj, dict) and "properties" in schema_obj:
                # Check required fields
                required = schema_obj.get("required", [])
                for req_field in required:
                    if req_field not in obj:
                        errors.append(f"Missing required field: {path}.{req_field}")

                # Validate each property
                for prop_name, prop_value in obj.items():
                    if prop_name in schema_obj["properties"]:
                        prop_schema = schema_obj["properties"][prop_name]
                        current_path = f"{path}.{prop_name}" if path else prop_name
                        _validate_recursive(prop_value, prop_schema, current_path)

            # Validate array items
            if isinstance(obj, list) and "items" in schema_obj:
                item_schema = schema_obj["items"]
                for i, item in enumerate(obj):
                    current_path = f"{path}[{i}]"
                    _validate_recursive(item, item_schema, current_path)

        _validate_recursive(data, schema)
        return len(errors) == 0, errors
