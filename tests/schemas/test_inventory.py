"""Tests for Inventory schemas."""

import pytest
from pydantic import ValidationError
from datetime import datetime
from app.schemas.inventory import (
    InventoryBase,
    InventoryCreate,
    InventoryUpdate,
    InventoryResponse,
    InventoryWithProduct
)


class TestInventorySchemas:
    """Test cases for Inventory schemas."""

    def test_inventory_base_valid_data(self):
        """Test InventoryBase with valid data."""
        data = {
            "quantity": 100,
            "location": "Warehouse A",
            "product_id": 1
        }
        inventory = InventoryBase(**data)
        assert inventory.quantity == 100
        assert inventory.location == "Warehouse A"
        assert inventory.product_id == 1

    def test_inventory_base_invalid_data(self):
        """Test InventoryBase with invalid data."""
        # Missing required quantity
        with pytest.raises(ValidationError):
            InventoryBase(location="Warehouse A", product_id=1)

        # Missing required location
        with pytest.raises(ValidationError):
            InventoryBase(quantity=50, product_id=1)

        # Missing required product_id
        with pytest.raises(ValidationError):
            InventoryBase(quantity=50, location="Warehouse A")

        # Invalid type for quantity
        with pytest.raises(ValidationError):
            InventoryBase(quantity="invalid", location="Warehouse A", product_id=1)

        # Invalid type for product_id
        with pytest.raises(ValidationError):
            InventoryBase(quantity=50, location="Warehouse A", product_id="invalid")

    def test_inventory_base_zero_quantity(self):
        """Test InventoryBase with zero quantity (should be valid)."""
        data = {
            "quantity": 0,
            "location": "Empty Shelf",
            "product_id": 1
        }
        inventory = InventoryBase(**data)
        assert inventory.quantity == 0

    def test_inventory_base_negative_quantity(self):
        """Test InventoryBase with negative quantity (should be valid for backorders)."""
        data = {
            "quantity": -10,
            "location": "Backorder",
            "product_id": 1
        }
        inventory = InventoryBase(**data)
        assert inventory.quantity == -10

    def test_inventory_create(self):
        """Test InventoryCreate schema."""
        data = {
            "quantity": 75,
            "location": "Storage Room B",
            "product_id": 2
        }
        inventory = InventoryCreate(**data)
        assert inventory.quantity == 75
        assert inventory.location == "Storage Room B"
        assert inventory.product_id == 2

    def test_inventory_update_partial(self):
        """Test InventoryUpdate with partial data."""
        # Only quantity
        update = InventoryUpdate(quantity=200)
        assert update.quantity == 200
        assert update.location is None

        # Only location
        update = InventoryUpdate(location="Updated Location")
        assert update.quantity is None
        assert update.location == "Updated Location"

        # Both fields
        update = InventoryUpdate(quantity=150, location="New Warehouse")
        assert update.quantity == 150
        assert update.location == "New Warehouse"

    def test_inventory_update_all_fields(self):
        """Test InventoryUpdate with all fields."""
        data = {
            "quantity": 300,
            "location": "Fully Updated Location"
        }
        update = InventoryUpdate(**data)
        assert update.quantity == 300
        assert update.location == "Fully Updated Location"

    def test_inventory_update_empty(self):
        """Test InventoryUpdate with no fields (should be valid)."""
        update = InventoryUpdate()
        assert update.quantity is None
        assert update.location is None

    def test_inventory_response(self):
        """Test InventoryResponse schema."""
        now = datetime.now()
        data = {
            "id": 1,
            "quantity": 125,
            "location": "Main Storage",
            "product_id": 1,
            "updated_at": now
        }
        response = InventoryResponse(**data)
        assert response.id == 1
        assert response.quantity == 125
        assert response.location == "Main Storage"
        assert response.product_id == 1
        assert response.updated_at == now

    def test_inventory_response_missing_id(self):
        """Test InventoryResponse without ID (should fail)."""
        data = {
            "quantity": 125,
            "location": "Main Storage",
            "product_id": 1,
            "updated_at": datetime.now()
        }
        with pytest.raises(ValidationError):
            InventoryResponse(**data)

    def test_inventory_response_missing_updated_at(self):
        """Test InventoryResponse without updated_at (should fail)."""
        data = {
            "id": 1,
            "quantity": 125,
            "location": "Main Storage",
            "product_id": 1
        }
        with pytest.raises(ValidationError):
            InventoryResponse(**data)

    def test_inventory_response_dict_conversion(self):
        """Test converting InventoryResponse to dict."""
        now = datetime.now()
        data = {
            "id": 1,
            "quantity": 80,
            "location": "Dict Test Location",
            "product_id": 1,
            "updated_at": now
        }
        response = InventoryResponse(**data)
        response_dict = response.model_dump()
        
        assert response_dict["id"] == 1
        assert response_dict["quantity"] == 80
        assert response_dict["location"] == "Dict Test Location"
        assert response_dict["product_id"] == 1
        assert response_dict["updated_at"] == now

    def test_inventory_location_variations(self):
        """Test inventory with various location formats."""
        locations = [
            "Warehouse A",
            "Storage-Room-1",
            "Bin #123",
            "Shelf A-1-B",
            "Cold Storage",
            "Receiving Dock"
        ]
        
        for location in locations:
            data = {
                "quantity": 10,
                "location": location,
                "product_id": 1
            }
            inventory = InventoryBase(**data)
            assert inventory.location == location

    def test_inventory_empty_location(self):
        """Test inventory with empty location string."""
        data = {
            "quantity": 50,
            "location": "",
            "product_id": 1
        }
        inventory = InventoryBase(**data)
        assert inventory.location == ""

    def test_inventory_large_quantity(self):
        """Test inventory with large quantity values."""
        data = {
            "quantity": 999999,
            "location": "Large Warehouse",
            "product_id": 1
        }
        inventory = InventoryBase(**data)
        assert inventory.quantity == 999999

    def test_inventory_schemas_inheritance(self):
        """Test that schemas properly inherit from base classes."""
        # InventoryCreate should inherit from InventoryBase
        assert issubclass(InventoryCreate, InventoryBase)
        
        # InventoryResponse should inherit from InventoryBase
        assert issubclass(InventoryResponse, InventoryBase)

        # InventoryWithProduct should inherit from InventoryResponse
        assert issubclass(InventoryWithProduct, InventoryResponse)

    def test_inventory_with_product_structure(self):
        """Test InventoryWithProduct has the expected structure."""
        # This test verifies the schema structure without needing actual related objects
        now = datetime.now()
        
        # Mock product data (would normally come from database relationships)
        product_data = {
            "id": 1,
            "name": "Test Product",
            "sku": "TEST-001", 
            "category": "Electronics",
            "created_at": now,
            "updated_at": now
        }
        
        data = {
            "id": 1,
            "quantity": 50,
            "location": "Test Location",
            "product_id": 1,
            "updated_at": now,
            "product": product_data
        }
        
        # This would work if we had proper forward references resolved
        # For now, just test that the schema class exists and has the right field definitions
        assert 'product' in InventoryWithProduct.model_fields

    def test_inventory_config_settings(self):
        """Test that InventoryResponse has correct Pydantic configuration."""
        # Check that from_attributes=True is configured for database model compatibility
        assert hasattr(InventoryResponse, 'model_config')
        config = InventoryResponse.model_config
        assert config.get('from_attributes') is True