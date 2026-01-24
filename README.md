# Inventory Management API

A comprehensive inventory management system built with FastAPI, featuring product management capabilities and a robust testing suite.

## 🚀 Features

- **Product Management**: Create, read, update, and delete products
- **Search & Filtering**: Search products by name and category
- **Pagination**: Efficient handling of large product lists
- **RESTful API**: Well-structured API endpoints
- **Comprehensive Testing**: Unit and integration tests with 94% coverage
- **Docker Support**: Containerized application with PostgreSQL database
- **Data Validation**: Pydantic schemas for request/response validation

## 📋 Requirements

- Python 3.11+
- PostgreSQL (for production) or SQLite (for testing)
- Docker and Docker Compose (optional)

## 🛠️ Installation

### Option 1: Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd inventory-v1
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database configuration
   ```

5. **Create database tables**
   ```bash
   python create_tables.py
   ```

6. **Run the application**
   ```bash
   uvicorn app.app:app --reload
   ```

### Option 2: Docker

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd inventory-v1
   ```

2. **Create environment file**
   ```bash
   echo "DATABASE_URL=postgresql://inventory_user:inventory_pass@db:5432/inventory" > .env
   ```

3. **Run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

Once the application is running, you can access:

- **Interactive API Documentation**: `http://localhost:8000/docs`
- **Alternative API Documentation**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

## 🔗 API Endpoints

### Products

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/products/` | Create a new product |
| `GET` | `/api/v1/products/` | Get all products (with search/pagination) |
| `GET` | `/api/v1/products/{id}` | Get a specific product |
| `PUT` | `/api/v1/products/{id}` | Update a product |
| `DELETE` | `/api/v1/products/{id}` | Delete a product |

### General

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Welcome message |
| `GET` | `/health` | Health check |

### Example Requests

**Create a product:**
```bash
curl -X POST "http://localhost:8000/api/v1/products/" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Laptop",
       "quantity": 50,
       "category": "Electronics"
     }'
```

**Search products:**
```bash
curl "http://localhost:8000/api/v1/products/?category=Electronics&limit=10"
```

## 🧪 Testing

The project includes comprehensive tests with 94% code coverage.

### Test Structure

```
tests/
├── conftest.py                     # Pytest fixtures and configuration
├── test_app.py                     # Main FastAPI app tests
├── test_integration.py             # Integration tests
├── api/v1/endpoints/
│   └── test_product.py             # API endpoint tests
├── models/
│   └── test_product.py             # Database model tests
├── schemas/
│   └── test_product.py             # Pydantic schema tests
└── services/
    └── test_product_service.py     # Business logic tests
```

### Running Tests

#### Using pytest directly

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run only unit tests
pytest -m "not integration"

# Run only integration tests
pytest -m integration

# Run specific test file
pytest tests/test_app.py

# Run with verbose output
pytest -v
```

#### Using Make commands

```bash
# Run all tests
make test

# Run unit tests only
make test-unit

# Run integration tests only
make test-integration

# Run tests with coverage report
make test-cov

# Run specific test file
make test-file FILE=tests/test_app.py
```

#### Using the Python test runner

```bash
# Run all tests
python run_tests.py

# Install dependencies and run tests
python run_tests.py --install

# Run specific test types
python run_tests.py unit
python run_tests.py integration
python run_tests.py coverage

# Run with code quality checks
python run_tests.py --quality
```

### Test Categories

- **Unit Tests**: Test individual components (models, schemas, services)
- **Integration Tests**: Test complete workflows and API endpoints
- **API Tests**: Test HTTP endpoints with various scenarios

### Coverage Report

Current test coverage: **94%**

Generate an HTML coverage report:
```bash
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

## 📁 Project Structure

```
inventory-v1/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   └── product.py      # Product API endpoints
│   │   │   └── api_router.py       # API router configuration
│   │   └── main.py                 # Alternative app entry (unused)
│   ├── core/
│   │   └── config.py               # Application configuration
│   ├── db/
│   │   ├── base.py                 # SQLAlchemy base class
│   │   └── session.py              # Database session management
│   ├── models/
│   │   └── product.py              # Product database model
│   ├── schemas/
│   │   └── product.py              # Pydantic schemas
│   ├── services/
│   │   └── product_service.py      # Business logic
│   └── app.py                      # Main FastAPI application
├── tests/                          # Test suite
├── docker-compose.yml              # Docker services configuration
├── Dockerfile                      # Docker image configuration
├── requirements.txt                # Python dependencies
├── requirements-dev.txt            # Development dependencies
├── create_tables.py               # Database initialization script
└── run_tests.py                   # Test runner script
```

## 🔧 Development

### Code Quality

The project uses several tools for code quality:

```bash
# Format code
black app/ tests/
isort app/ tests/

# Lint code
flake8 app/ tests/
mypy app/

# Security checks
bandit -r app/
safety check

# Run all quality checks
make quality
```

### Pre-commit Hooks

Install pre-commit hooks to automatically format and check code:

```bash
pip install pre-commit
pre-commit install
```

### Database Management

**Create tables:**
```bash
python create_tables.py
```

**Reset database (Docker):**
```bash
docker-compose down -v
docker-compose up --build
```

## 🌟 Key Features

### Product Management
- Full CRUD operations for products
- Data validation with Pydantic schemas
- SQLAlchemy ORM for database operations

### Search & Pagination
- Search by product name or category
- Configurable pagination with skip/limit
- Query parameter validation

### Error Handling
- Comprehensive HTTP error responses
- Input validation with detailed error messages
- Database error handling

### Testing
- Fixtures for test data and database sessions
- Integration tests for complete workflows
- High test coverage (94%)

## 🐳 Docker Support

The application includes full Docker support:

- **Multi-stage Dockerfile** for optimized images
- **Docker Compose** with PostgreSQL database
- **Health checks** for container monitoring
- **Non-root user** for security

## 📝 Environment Variables

Create a `.env` file with the following variables:

```bash
DATABASE_URL=postgresql://username:password@localhost:5432/inventory
OPENAI_API_KEY=your_openai_api_key  # Optional, for future AI features
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔮 Future Enhancements

- AI chatbot integration for inventory queries
- Advanced inventory analytics and reporting
- Multi-location inventory tracking
- Barcode scanning support
- Real-time inventory notifications

---

## 🆘 Troubleshooting

### Common Issues

**Database connection errors:**
- Ensure PostgreSQL is running
- Check database credentials in `.env`
- Verify database exists

**Import errors:**
- Ensure virtual environment is activated
- Install dependencies: `pip install -r requirements.txt`

**Test failures:**
- Check that test database is properly configured
- Ensure no other processes are using test ports

### Getting Help

1. Check the [API documentation](http://localhost:8000/docs)
2. Review the [test examples](tests/)
3. Check existing issues in the repository
4. Create a new issue with detailed error information

Happy coding! 🎉