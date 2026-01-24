"""Tests for Product schemas."""

import pytest
from pydantic import ValidationError
from app.schemas.product import ProductBase, ProductCreate, ProductUpdate, ProductResponse


class TestProductSchemas:
    """Test cases for Product schemas."""

    def test_product_base_valid_data(self):
        """Test ProductBase with valid data."""
        data = {
            "name": "Test Product",
            "quantity": 100,
            "category": "Electronics"
        }
        product = ProductBase(**data)
        assert product.name == "Test Product"
        assert product.quantity == 100
        assert product.category == "Electronics"

    def test_product_base_invalid_data(self):
        """Test ProductBase with invalid data."""
        # Missing required fields
        with pytest.raises(ValidationError):
            ProductBase(name="Test Product")

        # Invalid types
        with pytest.raises(ValidationError):
            ProductBase(name="Test Product", quantity="invalid", category="Electronics")

    def test_product_create(self):
        """Test ProductCreate schema."""
        data = {
            "name": "New Product",
            "quantity": 50,
            "category": "Books"
        }
        product = ProductCreate(**data)
        assert product.name == "New Product"
        assert product.quantity == 50
        assert product.category == "Books"

    def test_product_update_partial(self):
        """Test ProductUpdate with partial data."""
        # Only name
        product_update = ProductUpdate(name="Updated Name")
        assert product_update.name == "Updated Name"
        assert product_update.quantity is None
        assert product_update.category is None

        # Only quantity
        product_update = ProductUpdate(quantity=200)
        assert product_update.name is None
        assert product_update.quantity == 200
        assert product_update.category is None

        # Only category
        product_update = ProductUpdate(category="Updated Category")
        assert product_update.name is None
        assert product_update.quantity is None
        assert product_update.category == "Updated Category"

    def test_product_update_all_fields(self):
        """Test ProductUpdate with all fields."""
        data = {
            "name": "Fully Updated Product",
            "quantity": 150,
            "category": "Updated Category"
        }
        product_update = ProductUpdate(**data)
        assert product_update.name == "Fully Updated Product"
        assert product_update.quantity == 150
        assert product_update.category == "Updated Category"

    def test_product_update_empty(self):
        """Test ProductUpdate with no fields (should be valid)."""
        product_update = ProductUpdate()
        assert product_update.name is None
        assert product_update.quantity is None
        assert product_update.category is None

    def test_product_response(self):
        """Test ProductResponse schema."""
        data = {
            "id": 1,
            "name": "Response Product",
            "quantity": 75,
            "category": "Test Category"
        }
        product_response = ProductResponse(**data)
        assert product_response.id == 1
        assert product_response.name == "Response Product"
        assert product_response.quantity == 75
        assert product_response.category == "Test Category"

    def test_product_response_missing_id(self):
        """Test ProductResponse without ID (should fail)."""
        data = {
            "name": "Response Product",
            "quantity": 75,
            "category": "Test Category"
        }
        with pytest.raises(ValidationError):
            ProductResponse(**data)

    def test_product_response_dict_conversion(self):
        """Test converting ProductResponse to dict."""
        data = {
            "id": 1,
            "name": "Dict Product",
            "quantity": 30,
            "category": "Dict Category"
        }
        product_response = ProductResponse(**data)
        product_dict = product_response.model_dump()
        
        assert product_dict["id"] == 1
        assert product_dict["name"] == "Dict Product"
        assert product_dict["quantity"] == 30
        assert product_dict["category"] == "Dict Category"

    def test_product_schemas_inheritance(self):
        """Test that schemas properly inherit from base classes."""
        # ProductCreate should inherit from ProductBase
        assert issubclass(ProductCreate, ProductBase)
        
        # ProductResponse should inherit from ProductBase
        assert issubclass(ProductResponse, ProductBase)