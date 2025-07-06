# JSONUtilKit Documentation

This directory contains documentation for JSONUtilKit.

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
from jsonutilkit import JSONHandler

handler = JSONHandler("data.json")
handler.set("key", "value")
value = handler.get("key")
```

### JSONValidator

```python
from jsonutilkit import JSONValidator

is_valid, error = JSONValidator.validate_json_string('{"key": "value"}')
is_valid, error = JSONValidator.validate_json_file("data.json")
```

### JSONParser

```python
from jsonutilkit import JSONParser

data = JSONParser.parse_string('{"key": "value"}')
json_str = JSONParser.to_string(data, indent=2)
```
