.PHONY: help install install-dev test test-cov lint format clean build upload docs

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install the package
	pip install -e .

install-dev:  ## Install the package with development dependencies
	pip install -e ".[dev]"

test:  ## Run tests
	pytest

test-cov:  ## Run tests with coverage
	pytest --cov=src/pyjsonkit --cov-report=html --cov-report=term

lint:  ## Run linting checks
	flake8 src/ tests/
	mypy src/

format:  ## Format code
	black src/ tests/
	isort src/ tests/

format-check:  ## Check code formatting
	black --check src/ tests/
	isort --check-only src/ tests/

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:  ## Build the package
	python -m build

upload:  ## Upload to PyPI (requires authentication)
	python -m twine upload dist/*

upload-test:  ## Upload to Test PyPI
	python -m twine upload --repository testpypi dist/*

docs:  ## Build documentation (if using Sphinx)
	@echo "Documentation build not configured yet"

pre-commit:  ## Run pre-commit hooks
	pre-commit run --all-files

setup-pre-commit:  ## Setup pre-commit hooks
	pre-commit install
