"""
Advanced JSON transformation utilities for AI data processing.
"""

import re
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional


class JSONTransformer:
    """
    Advanced utilities for transforming JSON data structures.
    """

    @staticmethod
    def reshape_for_training(
        data: List[Dict[str, Any]], input_keys: List[str], output_keys: List[str]
    ) -> Dict[str, List[Any]]:
        """
        Reshape JSON data for machine learning training.

        Args:
            data: List of JSON objects
            input_keys: Keys to use as input features
            output_keys: Keys to use as output labels

        Returns:
            Dictionary with 'inputs' and 'outputs' arrays
        """
        inputs = []
        outputs = []

        for item in data:
            if isinstance(item, dict):
                # Extract input features
                input_row = []
                for key in input_keys:
                    value = item.get(key)
                    if isinstance(value, (int, float)):
                        input_row.append(value)
                    elif isinstance(value, str):
                        input_row.append(
                            len(value)
                        )  # Use string length as numeric feature
                    elif isinstance(value, bool):
                        input_row.append(1 if value else 0)
                    else:
                        input_row.append(0)  # Default for complex types

                # Extract output labels
                output_row = []
                for key in output_keys:
                    value = item.get(key)
                    if isinstance(value, (int, float, bool)):
                        output_row.append(value)
                    elif isinstance(value, str):
                        output_row.append(value)
                    else:
                        output_row.append(None)

                inputs.append(input_row)
                outputs.append(output_row if len(output_row) > 1 else output_row[0])

        return {
            "inputs": inputs,
            "outputs": outputs,
            "input_features": input_keys,
            "output_features": output_keys,
        }

    @staticmethod
    def pivot_data(
        data: List[Dict[str, Any]], index_key: str, column_key: str, value_key: str
    ) -> Dict[str, Dict[str, Any]]:
        """
        Pivot JSON data similar to pandas pivot operation.

        Args:
            data: List of JSON objects
            index_key: Key to use as row index
            column_key: Key to use as column names
            value_key: Key to use as values

        Returns:
            Pivoted data structure
        """
        result = defaultdict(dict)

        for item in data:
            if all(key in item for key in [index_key, column_key, value_key]):
                index_val = item[index_key]
                column_val = item[column_key]
                value_val = item[value_key]

                result[index_val][column_val] = value_val

        return dict(result)

    @staticmethod
    def normalize_for_ai_prompt(
        data: Dict[str, Any], max_depth: int = 3, max_items: int = 10
    ) -> str:
        """
        Convert JSON to a normalized string format suitable for AI prompts.

        Args:
            data: JSON data to normalize
            max_depth: Maximum nesting depth to include
            max_items: Maximum number of items to include in arrays

        Returns:
            Normalized string representation
        """

        def _normalize_recursive(obj: Any, depth: int = 0, path: str = "") -> str:
            if depth > max_depth:
                return "[TRUNCATED]"

            if isinstance(obj, dict):
                if not obj:
                    return "{}"

                items = []
                for key, value in list(obj.items())[:max_items]:
                    current_path = f"{path}.{key}" if path else key
                    normalized_value = _normalize_recursive(
                        value, depth + 1, current_path
                    )
                    items.append(f"{key}: {normalized_value}")

                if len(obj) > max_items:
                    items.append(f"... and {len(obj) - max_items} more items")

                return "{ " + ", ".join(items) + " }"

            elif isinstance(obj, list):
                if not obj:
                    return "[]"

                items = []
                for i, item in enumerate(obj[:max_items]):
                    current_path = f"{path}[{i}]"
                    normalized_item = _normalize_recursive(
                        item, depth + 1, current_path
                    )
                    items.append(normalized_item)

                if len(obj) > max_items:
                    items.append(f"... and {len(obj) - max_items} more items")

                return "[ " + ", ".join(items) + " ]"

            elif isinstance(obj, str):
                if len(obj) > 50:
                    return f'"{obj[:47]}..."'
                return f'"{obj}"'

            else:
                return str(obj)

        return _normalize_recursive(data)

    @staticmethod
    def create_embeddings_format(
        data: List[Dict[str, Any]],
        text_key: str,
        metadata_keys: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Transform data into format suitable for embedding generation.

        Args:
            data: List of JSON objects
            text_key: Key containing text to embed
            metadata_keys: Keys to include as metadata

        Returns:
            List of objects formatted for embedding
        """
        result = []
        metadata_keys = metadata_keys or []

        for i, item in enumerate(data):
            if isinstance(item, dict) and text_key in item:
                embedding_obj = {"id": i, "text": str(item[text_key]), "metadata": {}}

                # Add metadata
                for key in metadata_keys:
                    if key in item:
                        embedding_obj["metadata"][key] = item[key]

                result.append(embedding_obj)

        return result

    @staticmethod
    def convert_to_chat_format(
        data: List[Dict[str, Any]], role_key: str = "role", content_key: str = "content"
    ) -> List[Dict[str, str]]:
        """
        Convert data to chat/conversation format for AI training.

        Args:
            data: List of JSON objects
            role_key: Key containing the role (user, assistant, system)
            content_key: Key containing the message content

        Returns:
            List of chat messages
        """
        result = []

        for item in data:
            if isinstance(item, dict) and role_key in item and content_key in item:
                chat_message = {
                    "role": str(item[role_key]).lower(),
                    "content": str(item[content_key]),
                }
                result.append(chat_message)

        return result

    @staticmethod
    def aggregate_by_key(
        data: List[Dict[str, Any]], group_key: str, aggregations: Dict[str, str]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Aggregate data by a grouping key with various aggregation functions.

        Args:
            data: List of JSON objects
            group_key: Key to group by
            aggregations: Dict mapping field names to aggregation functions
                         ('sum', 'avg', 'count', 'min', 'max', 'list')

        Returns:
            Aggregated data grouped by the group_key
        """
        groups = defaultdict(list)

        # Group data
        for item in data:
            if isinstance(item, dict) and group_key in item:
                groups[item[group_key]].append(item)

        # Aggregate each group
        result = {}
        for group_value, group_items in groups.items():
            aggregated = {}

            for field, agg_func in aggregations.items():
                values = [item.get(field) for item in group_items if field in item]
                numeric_values = [v for v in values if isinstance(v, (int, float))]

                if agg_func == "sum":
                    aggregated[field] = sum(numeric_values)
                elif agg_func == "avg":
                    aggregated[field] = (
                        sum(numeric_values) / len(numeric_values)
                        if numeric_values
                        else 0
                    )
                elif agg_func == "count":
                    aggregated[field] = len(values)
                elif agg_func == "min":
                    aggregated[field] = min(numeric_values) if numeric_values else None
                elif agg_func == "max":
                    aggregated[field] = max(numeric_values) if numeric_values else None
                elif agg_func == "list":
                    aggregated[field] = values
                else:
                    aggregated[field] = values[0] if values else None

            result[group_value] = aggregated

        return result

    @staticmethod
    def create_time_series(
        data: List[Dict[str, Any]],
        timestamp_key: str,
        value_key: str,
        interval: str = "day",
    ) -> List[Dict[str, Any]]:
        """
        Transform data into time series format.

        Args:
            data: List of JSON objects
            timestamp_key: Key containing timestamp data
            value_key: Key containing values to aggregate
            interval: Time interval ('hour', 'day', 'week', 'month')

        Returns:
            Time series data
        """
        from collections import defaultdict

        time_buckets = defaultdict(list)

        for item in data:
            if isinstance(item, dict) and timestamp_key in item and value_key in item:
                timestamp_str = str(item[timestamp_key])

                # Try to parse timestamp
                try:
                    # Handle various timestamp formats
                    if re.match(r"\d{4}-\d{2}-\d{2}", timestamp_str):
                        dt = datetime.strptime(timestamp_str[:10], "%Y-%m-%d")
                    elif re.match(r"\d{2}/\d{2}/\d{4}", timestamp_str):
                        dt = datetime.strptime(timestamp_str[:10], "%m/%d/%Y")
                    else:
                        continue

                    # Create time bucket based on interval
                    if interval == "hour":
                        bucket = dt.strftime("%Y-%m-%d %H:00")
                    elif interval == "day":
                        bucket = dt.strftime("%Y-%m-%d")
                    elif interval == "week":
                        # Get Monday of the week
                        monday = dt - datetime.timedelta(days=dt.weekday())
                        bucket = monday.strftime("%Y-%m-%d")
                    elif interval == "month":
                        bucket = dt.strftime("%Y-%m")
                    else:
                        bucket = dt.strftime("%Y-%m-%d")

                    time_buckets[bucket].append(item[value_key])

                except ValueError:
                    continue

        # Convert to time series format
        result = []
        for timestamp, values in sorted(time_buckets.items()):
            numeric_values = [v for v in values if isinstance(v, (int, float))]

            result.append(
                {
                    "timestamp": timestamp,
                    "count": len(values),
                    "sum": sum(numeric_values) if numeric_values else 0,
                    "avg": (
                        sum(numeric_values) / len(numeric_values)
                        if numeric_values
                        else 0
                    ),
                    "min": min(numeric_values) if numeric_values else None,
                    "max": max(numeric_values) if numeric_values else None,
                }
            )

        return result

    @staticmethod
    def flatten_for_csv(
        data: List[Dict[str, Any]], separator: str = "_", max_depth: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Flatten nested JSON for CSV export.

        Args:
            data: List of JSON objects
            separator: Separator for nested keys
            max_depth: Maximum depth to flatten

        Returns:
            List of flattened objects
        """

        def _flatten_dict(
            obj: Dict[str, Any], parent_key: str = "", depth: int = 0
        ) -> Dict[str, Any]:
            if depth >= max_depth:
                return {parent_key: str(obj)}

            items = []
            for key, value in obj.items():
                new_key = f"{parent_key}{separator}{key}" if parent_key else key

                if isinstance(value, dict):
                    items.extend(_flatten_dict(value, new_key, depth + 1).items())
                elif isinstance(value, list):
                    # Convert list to string or flatten if contains dicts
                    if value and isinstance(value[0], dict):
                        for i, item in enumerate(value):
                            if isinstance(item, dict):
                                items.extend(
                                    _flatten_dict(
                                        item, f"{new_key}{separator}{i}", depth + 1
                                    ).items()
                                )
                            else:
                                items.append((f"{new_key}{separator}{i}", item))
                    else:
                        items.append((new_key, str(value)))
                else:
                    items.append((new_key, value))

            return dict(items)

        result = []
        for item in data:
            if isinstance(item, dict):
                flattened = _flatten_dict(item)
                result.append(flattened)

        return result
