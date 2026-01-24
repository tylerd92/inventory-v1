# Testing Guide - Inventory Management API

This document provides comprehensive information about the testing setup for the Inventory Management API.

## 🧪 Testing Framework

The project uses **pytest** as the primary testing framework along with several supporting libraries:

- **pytest**: Main testing framework
- **pytest-asyncio**: For testing async code
- **pytest-cov**: For code coverage reporting
- **httpx**: For making HTTP requests in tests (replaces requests for async support)
- **SQLAlchemy with SQLite**: In-memory database for testing

## 📁 Test Structure

```
tests/
├── __init__.py
├── conftest.py                     # Pytest fixtures and configuration
├── test_app.py                     # Main FastAPI app tests
├── test_integration.py             # Integration tests
├── api/
│   └── v1/
│       └── endpoints/
│           └── test_product.py     # Product API endpoint tests
├── models/
│   └── test_product.py             # Product model tests
├── schemas/
│   └── test_product.py             # Product schema tests
└── services/
    └── test_product_service.py     # Product service tests
```

## 🔧 Configuration

### pytest.ini Configuration (in pyproject.toml)

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short --strict-markers"
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
]
```

### Coverage Configuration

```toml
[tool.coverage.run]
source = ["app"]
omit = ["*/tests/*", "*/__pycache__/*", "*/migrations/*"]
```

## 🏃‍♂️ Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_app.py

# Run specific test class
pytest tests/models/test_product.py::TestProductModel

# Run specific test method
pytest tests/models/test_product.py::TestProductModel::test_product_creation
```

### Test Categories

```bash
# Run only unit tests
pytest -m "not integration"

# Run only integration tests
pytest -m integration

# Run tests excluding slow tests
pytest -m "not slow"
```

### Coverage Reports

```bash
# Run tests with coverage
pytest --cov=app

# Generate HTML coverage report
pytest --cov=app --cov-report=html

# Show missing lines
pytest --cov=app --cov-report=term-missing
```

### Using Make Commands

```bash
# Install development dependencies
make install-dev

# Run all tests
make test

# Run unit tests only
make test-unit

# Run integration tests only
make test-integration

# Run tests with coverage
make test-cov

# Run tests in verbose mode
make test-verbose

# Run specific test file
make test-file FILE=tests/test_app.py
```

### Using the Python Test Runner

```bash
# Run all tests
python run_tests.py

# Install dependencies and run tests
python run_tests.py --install

# Run specific test types
python run_tests.py unit
python run_tests.py integration
python run_tests.py coverage

# Run with quality checks
python run_tests.py --quality
```

## 🔨 Test Fixtures

The `conftest.py` file provides several reusable fixtures:

### Database Fixtures

- **`db_session`**: Provides a fresh SQLite in-memory database session for each test
- **`client`**: FastAPI test client with database dependency override

### Data Fixtures

- **`sample_product_data`**: Single product data for testing
- **`sample_products_data`**: Multiple products for testing lists and searches

### Example Usage

```python
def test_create_product(client, sample_product_data):
    response = client.post("/api/v1/products/", json=sample_product_data)
    assert response.status_code == 200
```

## 📊 Test Coverage

Current test coverage: **94%**

### Coverage Breakdown

- **API Endpoints**: 100% coverage
- **Services**: 100% coverage
- **Models**: 100% coverage
- **Schemas**: 100% coverage
- **Database Layer**: 64% coverage (some utility functions not tested)

### Areas Not Covered

- `app/api/main.py` - Unused file
- Some database session utility functions

## 🧪 Test Types

### 1. Unit Tests

Test individual components in isolation:

- **Model Tests**: Database model behavior
- **Schema Tests**: Pydantic model validation
- **Service Tests**: Business logic functions

### 2. Integration Tests

Test complete workflows:

- **API Integration**: Full request/response cycles
- **Database Integration**: End-to-end data operations
- **Error Handling**: Complete error scenarios

### 3. API Tests

Test HTTP endpoints:

- **CRUD Operations**: Create, Read, Update, Delete
- **Search and Filtering**: Query parameters
- **Pagination**: Skip and limit parameters
- **Error Responses**: 404, 422, etc.

## 📝 Writing New Tests

### Test Naming Convention

```python
class TestProductService:
    def test_create_product_success(self):
        """Test successful product creation."""
        pass

    def test_create_product_invalid_data(self):
        """Test product creation with invalid data."""
        pass
```

### Using Fixtures

```python
def test_example(db_session, sample_product_data):
    # db_session provides database connection
    # sample_product_data provides test data
    product = Product(**sample_product_data)
    db_session.add(product)
    db_session.commit()
    assert product.id is not None
```

### Marking Tests

```python
import pytest

@pytest.mark.integration
def test_full_workflow():
    """This is an integration test."""
    pass

@pytest.mark.slow
def test_performance():
    """This is a slow test."""
    pass
```

## 🔄 Continuous Integration

Tests are configured to run in CI/CD pipelines with:

- Automatic dependency installation
- Full test suite execution
- Coverage reporting
- Code quality checks

## 🐛 Debugging Tests

### Running Single Tests

```bash
# Run with detailed output
pytest -vvv tests/test_specific.py::test_method

# Run with pdb debugger
pytest --pdb tests/test_specific.py::test_method

# Run with logging output
pytest -s tests/test_specific.py
```

### Common Issues

1. **Database Connection Errors**: Ensure test database configuration is correct
2. **Import Errors**: Check PYTHONPATH and module imports
3. **Fixture Issues**: Verify fixture dependencies and scoping

## 📈 Best Practices

### 1. Test Organization

- Group related tests in classes
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)

### 2. Test Data

- Use fixtures for reusable test data
- Keep test data minimal but representative
- Avoid hardcoded values when possible

### 3. Assertions

- Use specific assertions (`assert len(items) == 3` vs `assert items`)
- Test both success and failure cases
- Verify complete response structure

### 4. Database Testing

- Use transaction rollbacks for cleanup
- Test with realistic data volumes
- Verify database state changes

### 5. API Testing

- Test all HTTP methods
- Verify response status codes
- Test request validation
- Check response schemas

## 🔧 Maintenance

### Regular Tasks

1. **Update Test Dependencies**: Keep testing libraries up to date
2. **Coverage Analysis**: Review uncovered code periodically
3. **Performance Testing**: Monitor test execution times
4. **Cleanup**: Remove obsolete tests and fixtures

### Adding New Features

When adding new features:

1. Write tests first (TDD approach)
2. Ensure adequate coverage
3. Add appropriate fixtures
4. Update integration tests
5. Document test scenarios

---

## 📞 Support

For questions about testing:

1. Check this documentation first
2. Review existing test examples
3. Consult pytest documentation
4. Ask the development team

Happy Testing! 🎉
