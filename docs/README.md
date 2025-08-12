# JSONKit Documentation

This directory contains documentation for JSONKit.

## Structure

- `api/` - API reference documentation
- `examples/` - Usage examples and tutorials
- `guides/` - How-to guides and best practices

## Building Documentation

If you want to build Sphinx documentation:

```bash
pip install -e ".[docs]"
cd docs
make html
```

## Quick Reference

### JSONHandler

```python
from jsonkit import JSONHandler

handler = JSONHandler("data.json")
handler.set("key", "value")
value = handler.get("key")
```

### JSONValidator

```python
from jsonkit import JSONValidator

is_valid, error = JSONValidator.validate_json_string('{"key": "value"}')
is_valid, error = JSONValidator.validate_json_file("data.json")
```

### JSONParser

```python
from jsonkit import JSONParser

data = JSONParser.parse_string('{"key": "value"}')
json_str = JSONParser.to_string(data, indent=2)
```
