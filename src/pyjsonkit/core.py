"""
Core JSON handling functionality.
"""

import json
from pathlib import Path
from typing import Any, Dict, Union


class JSONHandler:
    """
    A class for handling JSON file operations.

    Provides methods to read, write, validate, and manipulate JSON files.
    """

    def __init__(self, file_path: Union[str, Path]):
        """
        Initialize the JSONHandler with a file path.

        Args:
            file_path: Path to the JSON file

        Raises:
            FileNotFoundError: If the file doesn't exist
            json.JSONDecodeError: If the file contains invalid JSON
        """
        self.file_path = Path(file_path)
        self._data: Dict[str, Any] = {}

        if self.file_path.exists():
            self._load_data()
        else:
            # Create empty file if it doesn't exist
            self._save_data()

    def _load_data(self) -> None:
        """Load data from the JSON file."""
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                self._data = json.load(file)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Invalid JSON in file {self.file_path}: {e.msg}", e.doc, e.pos
            ) from e
        except Exception as e:
            raise IOError(f"Error reading file {self.file_path}: {e}")

    def _save_data(self) -> None:
        """Save data to the JSON file."""
        try:
            # Ensure directory exists
            self.file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.file_path, "w", encoding="utf-8") as file:
                json.dump(self._data, file, indent=2, ensure_ascii=False)
        except Exception as e:
            raise IOError(f"Error writing to file {self.file_path}: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the JSON data.

        Args:
            key: The key to retrieve
            default: Default value if key doesn't exist

        Returns:
            The value associated with the key, or default if not found
        """
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set a value in the JSON data and save to file.

        Args:
            key: The key to set
            value: The value to associate with the key
        """
        self._data[key] = value
        self._save_data()

    def delete(self, key: str) -> bool:
        """
        Delete a key from the JSON data.

        Args:
            key: The key to delete

        Returns:
            True if key was deleted, False if key didn't exist
        """
        if key in self._data:
            del self._data[key]
            self._save_data()
            return True
        return False

    def clear(self) -> None:
        """Clear all data from the JSON file."""
        self._data = {}
        self._save_data()

    def keys(self) -> list:
        """Get all keys in the JSON data."""
        return list(self._data.keys())

    def values(self) -> list:
        """Get all values in the JSON data."""
        return list(self._data.values())

    def items(self) -> list:
        """Get all key-value pairs in the JSON data."""
        return list(self._data.items())

    def update(self, data: Dict[str, Any]) -> None:
        """
        Update the JSON data with new data.

        Args:
            data: Dictionary to merge with existing data
        """
        self._data.update(data)
        self._save_data()

    def to_dict(self) -> Dict[str, Any]:
        """Return a copy of the internal data dictionary."""
        return self._data.copy()

    def validate(self) -> bool:
        """
        Validate that the current data is valid JSON.

        Returns:
            True if data is valid JSON, False otherwise
        """
        try:
            json.dumps(self._data)
            return True
        except (TypeError, ValueError):
            return False

    def pretty_print(self) -> str:
        """
        Return a pretty-printed string representation of the JSON data.

        Returns:
            Formatted JSON string
        """
        return json.dumps(self._data, indent=2, ensure_ascii=False)

    def __str__(self) -> str:
        """String representation of the JSON data."""
        return json.dumps(self._data)

    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"JSONHandler(file_path='{self.file_path}', keys={len(self._data)})"

    def __len__(self) -> int:
        """Return the number of keys in the JSON data."""
        return len(self._data)

    def __contains__(self, key: str) -> bool:
        """Check if a key exists in the JSON data."""
        return key in self._data
