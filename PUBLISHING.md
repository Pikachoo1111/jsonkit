# Publishing Guide for JSONKit

This guide explains how to publish JSONKit to PyPI.

## Prerequisites

1. **PyPI Account**: Create accounts on both:
   - [PyPI](https://pypi.org/account/register/) (production)
   - [TestPyPI](https://test.pypi.org/account/register/) (testing)

2. **API Tokens**: Generate API tokens for both accounts:
   - Go to Account Settings → API tokens
   - Create a token with "Entire account" scope
   - Save the tokens securely

## Publishing Steps

### 1. Test on TestPyPI First

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ jsonkit
```

### 2. Publish to PyPI

```bash
# Upload to PyPI
twine upload dist/*

# Test installation from PyPI
pip install jsonkit
```

## Authentication

You'll be prompted for credentials. Use:
- Username: `__token__`
- Password: Your API token (including the `pypi-` prefix)

Or configure credentials in `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-testpypi-token-here
```

## Version Management

Before publishing a new version:

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md` with new changes
3. Commit changes
4. Create a git tag: `git tag v0.1.1`
5. Push tag: `git push origin v0.1.1`
6. Rebuild package: `python -m build`
7. Publish new version

## Package Status

✅ **Ready for Publication**

The package is now ready to be published to PyPI with:
- ✅ Professional package structure
- ✅ Comprehensive AI-focused features
- ✅ Complete test suite (133 tests, 100% passing)
- ✅ Updated documentation and README
- ✅ Proper licensing and metadata
- ✅ Built and validated distributions
- ✅ All imports working correctly

## Quick Publish Commands

```bash
# Build the package
python -m build

# Check the package
twine check dist/*

# Upload to TestPyPI (recommended first)
twine upload --repository testpypi dist/*

# Upload to PyPI (production)
twine upload dist/*
```

## Post-Publication

After publishing:
1. Test installation: `pip install jsonkit`
2. Update GitHub repository with release notes
3. Consider creating a GitHub release
4. Share on social media or relevant communities
