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
            "sku": "TEST-001",
            "category": "Electronics"
        }
        product = ProductBase(**data)
        assert product.name == "Test Product"
        assert product.sku == "TEST-001"
        assert product.category == "Electronics"

    def test_product_base_invalid_data(self):
        """Test ProductBase with invalid data."""
        # Missing required fields
        with pytest.raises(ValidationError):
            ProductBase(name="Test Product")

        # Invalid types - test with missing sku
        with pytest.raises(ValidationError):
            ProductBase(name="Test Product", category="Electronics")

    def test_product_create(self):
        """Test ProductCreate schema."""
        data = {
            "name": "New Product",
            "sku": "NEW-001",
            "category": "Books"
        }
        product = ProductCreate(**data)
        assert product.name == "New Product"
        assert product.sku == "NEW-001"
        assert product.category == "Books"

    def test_product_update_partial(self):
        """Test ProductUpdate with partial data."""
        # Only name
        product_update = ProductUpdate(name="Updated Name")
        assert product_update.name == "Updated Name"
        assert product_update.sku is None
        assert product_update.category is None
        assert product_update.category is None

        # Only sku
        product_update = ProductUpdate(sku="NEW-SKU-002")
        assert product_update.name is None
        assert product_update.sku == "NEW-SKU-002"
        assert product_update.category is None

        # Only category
        product_update = ProductUpdate(category="Updated Category")
        assert product_update.name is None
        assert product_update.sku is None
        assert product_update.category == "Updated Category"

    def test_product_update_all_fields(self):
        """Test ProductUpdate with all fields."""
        data = {
            "name": "Fully Updated Product",
            "sku": "FULL-UPD-150",
            "category": "Updated Category"
        }
        product_update = ProductUpdate(**data)
        assert product_update.name == "Fully Updated Product"
        assert product_update.sku == "FULL-UPD-150"
        assert product_update.category == "Updated Category"

    def test_product_update_empty(self):
        """Test ProductUpdate with no fields (should be valid)."""
        product_update = ProductUpdate()
        assert product_update.name is None
        assert product_update.sku is None
        assert product_update.category is None

    def test_product_response(self):
        """Test ProductResponse schema."""
        from datetime import datetime
        data = {
            "id": 1,
            "name": "Response Product",
            "sku": "RESP-075",
            "category": "Test Category",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        product_response = ProductResponse(**data)
        assert product_response.id == 1
        assert product_response.name == "Response Product"
        assert product_response.sku == "RESP-075"
        assert product_response.category == "Test Category"
        assert product_response.created_at is not None
        assert product_response.updated_at is not None

    def test_product_response_missing_id(self):
        """Test ProductResponse without ID (should fail)."""
        from datetime import datetime
        data = {
            "name": "Response Product",
            "sku": "RESP-075",
            "category": "Test Category",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        with pytest.raises(ValidationError):
            ProductResponse(**data)

    def test_product_response_dict_conversion(self):
        """Test converting ProductResponse to dict."""
        from datetime import datetime
        now = datetime.now()
        data = {
            "id": 1,
            "name": "Dict Product",
            "sku": "DICT-030",
            "category": "Dict Category",
            "created_at": now,
            "updated_at": now
        }
        product_response = ProductResponse(**data)
        product_dict = product_response.model_dump()
        
        assert product_dict["id"] == 1
        assert product_dict["name"] == "Dict Product"
        assert product_dict["sku"] == "DICT-030"
        assert product_dict["category"] == "Dict Category"
        assert product_dict["created_at"] == now
        assert product_dict["updated_at"] == now

    def test_product_schemas_inheritance(self):
        """Test that schemas properly inherit from base classes."""
        # ProductCreate should inherit from ProductBase
        assert issubclass(ProductCreate, ProductBase)
        
        # ProductResponse should inherit from ProductBase
        assert issubclass(ProductResponse, ProductBase)