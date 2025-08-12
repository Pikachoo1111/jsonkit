"""
JSON cleaning and sanitization utilities for AI-generated content.
"""

import re
from datetime import datetime
from typing import Any, Optional, Set


class JSONCleaner:
    """
    Utilities for cleaning and sanitizing JSON data, especially from AI sources.
    """

    @staticmethod
    def remove_null_values(data: Any, recursive: bool = True) -> Any:
        """
        Remove null/None values from JSON data.

        Args:
            data: JSON data to clean
            recursive: Whether to clean nested structures

        Returns:
            Cleaned data without null values
        """
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                if value is not None:
                    if recursive:
                        cleaned_value = JSONCleaner.remove_null_values(value, recursive)
                        if cleaned_value is not None:
                            result[key] = cleaned_value
                    else:
                        result[key] = value
            return result

        elif isinstance(data, list):
            result = []
            for item in data:
                if item is not None:
                    if recursive:
                        cleaned_item = JSONCleaner.remove_null_values(item, recursive)
                        if cleaned_item is not None:
                            result.append(cleaned_item)
                    else:
                        result.append(item)
            return result

        return data

    @staticmethod
    def remove_empty_values(data: Any, recursive: bool = True) -> Any:
        """
        Remove empty values (null, empty strings, empty arrays, empty objects).

        Args:
            data: JSON data to clean
            recursive: Whether to clean nested structures

        Returns:
            Cleaned data without empty values
        """
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                if recursive:
                    cleaned_value = JSONCleaner.remove_empty_values(value, recursive)
                else:
                    cleaned_value = value

                # Keep non-empty values
                if (
                    cleaned_value is not None
                    and cleaned_value != ""
                    and cleaned_value != []
                    and cleaned_value != {}
                ):
                    result[key] = cleaned_value
            return result

        elif isinstance(data, list):
            result = []
            for item in data:
                if recursive:
                    cleaned_item = JSONCleaner.remove_empty_values(item, recursive)
                else:
                    cleaned_item = item

                if (
                    cleaned_item is not None
                    and cleaned_item != ""
                    and cleaned_item != []
                    and cleaned_item != {}
                ):
                    result.append(cleaned_item)
            return result

        return data

    @staticmethod
    def normalize_strings(
        data: Any,
        strip_whitespace: bool = True,
        normalize_case: Optional[str] = None,
        remove_extra_spaces: bool = True,
    ) -> Any:
        """
        Normalize string values in JSON data.

        Args:
            data: JSON data to normalize
            strip_whitespace: Whether to strip leading/trailing whitespace
            normalize_case: 'lower', 'upper', 'title', or None
            remove_extra_spaces: Whether to collapse multiple spaces to single space

        Returns:
            Data with normalized strings
        """

        def _normalize_string(s: str) -> str:
            if strip_whitespace:
                s = s.strip()

            if remove_extra_spaces:
                s = re.sub(r"\s+", " ", s)

            if normalize_case == "lower":
                s = s.lower()
            elif normalize_case == "upper":
                s = s.upper()
            elif normalize_case == "title":
                s = s.title()

            return s

        if isinstance(data, dict):
            return {
                key: JSONCleaner.normalize_strings(
                    value, strip_whitespace, normalize_case, remove_extra_spaces
                )
                for key, value in data.items()
            }

        elif isinstance(data, list):
            return [
                JSONCleaner.normalize_strings(
                    item, strip_whitespace, normalize_case, remove_extra_spaces
                )
                for item in data
            ]

        elif isinstance(data, str):
            return _normalize_string(data)

        return data

    @staticmethod
    def sanitize_for_ai(
        data: Any,
        remove_sensitive: bool = True,
        max_string_length: Optional[int] = None,
        allowed_keys: Optional[Set[str]] = None,
    ) -> Any:
        """
        Sanitize JSON data for AI processing by removing sensitive info and
        limiting size.

        Args:
            data: JSON data to sanitize
            remove_sensitive: Whether to remove potentially sensitive information
            max_string_length: Maximum length for string values
            allowed_keys: Set of allowed keys (others will be removed)

        Returns:
            Sanitized data
        """
        sensitive_patterns = (
            [
                r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",  # Credit card
                r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
                # Phone
                r"\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b",
            ]
            if remove_sensitive
            else []
        )

        def _sanitize_string(s: str) -> str:
            # Remove sensitive patterns
            for pattern in sensitive_patterns:
                s = re.sub(pattern, "[REDACTED]", s, flags=re.IGNORECASE)

            # Limit string length
            if max_string_length and len(s) > max_string_length:
                s = s[:max_string_length] + "..."

            return s

        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                # Skip disallowed keys
                if allowed_keys and key not in allowed_keys:
                    continue

                result[key] = JSONCleaner.sanitize_for_ai(
                    value, remove_sensitive, max_string_length, allowed_keys
                )
            return result

        elif isinstance(data, list):
            return [
                JSONCleaner.sanitize_for_ai(
                    item, remove_sensitive, max_string_length, allowed_keys
                )
                for item in data
            ]

        elif isinstance(data, str):
            return _sanitize_string(data)

        return data

    @staticmethod
    def deduplicate_arrays(data: Any) -> Any:
        """
        Remove duplicate items from arrays in JSON data.

        Args:
            data: JSON data to deduplicate

        Returns:
            Data with deduplicated arrays
        """
        if isinstance(data, dict):
            return {
                key: JSONCleaner.deduplicate_arrays(value)
                for key, value in data.items()
            }

        elif isinstance(data, list):
            # Handle different types of items
            seen = set()
            result = []

            for item in data:
                # For hashable items, use set for deduplication
                if isinstance(item, (str, int, float, bool, type(None))):
                    if item not in seen:
                        seen.add(item)
                        result.append(JSONCleaner.deduplicate_arrays(item))
                else:
                    # For unhashable items (dict, list), use slower comparison
                    item_cleaned = JSONCleaner.deduplicate_arrays(item)
                    if item_cleaned not in result:
                        result.append(item_cleaned)

            return result

        return data

    @staticmethod
    def fix_encoding_issues(data: Any) -> Any:
        """
        Fix common encoding issues in JSON strings.

        Args:
            data: JSON data to fix

        Returns:
            Data with fixed encoding
        """

        def _fix_string(s: str) -> str:
            # Fix common encoding issues
            replacements = [
                # Common UTF-8 encoding issues (double-encoded)
                ("\u00e2\u20ac\u2122", "'"),  # â€™ -> '
                ("\u00e2\u20ac\u0153", '"'),  # â€œ -> "
                ("\u00e2\u20ac\u009d", '"'),  # â€ -> "
                ("\u00e2\u20ac\u201c", "-"),  # â€" -> -
                ("\u00e2\u20ac\u201d", "-"),  # â€" -> -
                ("\u00e2\u20ac\u00a6", "..."),  # â€¦ -> ...
                # Proper Unicode characters
                ("\u2019", "'"),  # Right single quotation mark
                ("\u201c", '"'),  # Left double quotation mark
                ("\u201d", '"'),  # Right double quotation mark
                ("\u2013", "-"),  # En dash
                ("\u2014", "-"),  # Em dash
                ("\u2026", "..."),  # Horizontal ellipsis
                ("\xc3\xb1", "ñ"),  # ñ with tilde
            ]

            for bad, good in replacements:
                s = s.replace(bad, good)

            # Remove or replace other problematic characters
            s = re.sub(r"[^\x00-\x7F]+", "", s)  # Remove non-ASCII if needed

            return s

        if isinstance(data, dict):
            return {
                key: JSONCleaner.fix_encoding_issues(value)
                for key, value in data.items()
            }

        elif isinstance(data, list):
            return [JSONCleaner.fix_encoding_issues(item) for item in data]

        elif isinstance(data, str):
            return _fix_string(data)

        return data

    @staticmethod
    def standardize_dates(data: Any, target_format: str = "%Y-%m-%d") -> Any:
        """
        Standardize date formats in JSON data.

        Args:
            data: JSON data to process
            target_format: Target date format string

        Returns:
            Data with standardized dates
        """
        date_patterns = [
            (r"\b\d{4}-\d{2}-\d{2}\b", "%Y-%m-%d"),
            (r"\b\d{2}/\d{2}/\d{4}\b", "%m/%d/%Y"),
            (r"\b\d{2}-\d{2}-\d{4}\b", "%m-%d-%Y"),
            (r"\b\d{1,2}/\d{1,2}/\d{4}\b", "%m/%d/%Y"),
        ]

        def _standardize_string(s: str) -> str:
            for pattern, format_str in date_patterns:
                matches = re.findall(pattern, s)
                for match in matches:
                    try:
                        # Parse the date and reformat
                        parsed_date = datetime.strptime(match, format_str)
                        new_date = parsed_date.strftime(target_format)
                        s = s.replace(match, new_date)
                    except ValueError:
                        continue  # Skip if parsing fails
            return s

        if isinstance(data, dict):
            return {
                key: JSONCleaner.standardize_dates(value, target_format)
                for key, value in data.items()
            }

        elif isinstance(data, list):
            return [JSONCleaner.standardize_dates(item, target_format) for item in data]

        elif isinstance(data, str):
            return _standardize_string(data)

        return data

    @staticmethod
    def clean_ai_artifacts(data: Any) -> Any:
        """
        Remove common AI-generated artifacts and formatting issues.

        Args:
            data: JSON data to clean

        Returns:
            Cleaned data
        """

        def _clean_string(s: str) -> str:
            # Remove AI-specific artifacts
            artifacts = [
                r"\[AI_GENERATED\]",
                r"\[PLACEHOLDER\]",
                r"\[TODO:.*?\]",
                r"\[EXAMPLE\]",
                r"<thinking>.*?</thinking>",
                r"```json\s*",
                r"\s*```",
                r"Note:.*?(?=\n|$)",
                r"Please note:.*?(?=\n|$)",
            ]

            for artifact in artifacts:
                s = re.sub(artifact, "", s, flags=re.IGNORECASE | re.DOTALL)

            # Clean up extra whitespace
            s = re.sub(r"\n\s*\n", "\n", s)  # Multiple newlines
            s = re.sub(r"\s+", " ", s)  # Multiple spaces
            s = s.strip()

            return s

        if isinstance(data, dict):
            return {
                key: JSONCleaner.clean_ai_artifacts(value)
                for key, value in data.items()
            }

        elif isinstance(data, list):
            return [JSONCleaner.clean_ai_artifacts(item) for item in data]

        elif isinstance(data, str):
            return _clean_string(data)

        return data
