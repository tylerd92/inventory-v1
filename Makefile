.PHONY: test test-unit test-integration test-cov clean install-dev lint format

# Python and pytest paths
PYTHON := ./venv/bin/python
PYTEST := ./venv/bin/pytest
PIP := ./venv/bin/pip

# Install development dependencies
install-dev:
	$(PIP) install -r requirements-dev.txt

# Run all tests
test:
	$(PYTEST)

# Run only unit tests
test-unit:
	$(PYTEST) -m "not integration" -v

# Run only integration tests
test-integration:
	$(PYTEST) -m integration -v

# Run tests with coverage
test-cov:
	$(PYTEST) --cov=app --cov-report=html --cov-report=term-missing

# Run tests in verbose mode
test-verbose:
	$(PYTEST) -v --tb=long

# Run specific test file
test-file:
	$(PYTEST) $(FILE) -v

# Clean up generated files
clean:
	rm -rf .coverage htmlcov/ .pytest_cache/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

# Format code
format:
	./venv/bin/black app/ tests/
	./venv/bin/isort app/ tests/

# Lint code
lint:
	./venv/bin/flake8 app/ tests/
	./venv/bin/mypy app/
	./venv/bin/pylint app/

# Security check
security:
	./venv/bin/bandit -r app/
	./venv/bin/safety check

# Run all quality checks
quality: lint security

# Run tests and quality checks
ci: test quality