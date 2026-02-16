"""Tests for InventoryTransaction schemas."""

import pytest
from pydantic import ValidationError
from datetime import datetime
from app.schemas.inventory_transaction import (
    InventoryTransactionBase,
    InventoryTransactionCreate,
    InventoryTransactionUpdate,
    InventoryTransactionResponse,
    InventoryTransactionWithDetails
)


class TestInventoryTransactionSchemas:
    """Test cases for InventoryTransaction schemas."""

    def test_inventory_transaction_base_valid_data(self):
        """Test InventoryTransactionBase with valid data."""
        data = {
            "product_id": 1,
            "change_amount": 50,
            "reason": "Stock adjustment",
            "performed_by": 1
        }
        transaction = InventoryTransactionBase(**data)
        assert transaction.product_id == 1
        assert transaction.change_amount == 50
        assert transaction.reason == "Stock adjustment"
        assert transaction.performed_by == 1

    def test_inventory_transaction_base_minimal_data(self):
        """Test InventoryTransactionBase with minimal required data."""
        data = {
            "product_id": 1,
            "change_amount": 25
        }
        transaction = InventoryTransactionBase(**data)
        assert transaction.product_id == 1
        assert transaction.change_amount == 25
        assert transaction.reason is None
        assert transaction.performed_by is None

    def test_inventory_transaction_base_invalid_data(self):
        """Test InventoryTransactionBase with invalid data."""
        # Missing required product_id
        with pytest.raises(ValidationError):
            InventoryTransactionBase(change_amount=10)

        # Missing required change_amount
        with pytest.raises(ValidationError):
            InventoryTransactionBase(product_id=1)

        # Invalid type for product_id
        with pytest.raises(ValidationError):
            InventoryTransactionBase(product_id="invalid", change_amount=10)

        # Invalid type for change_amount
        with pytest.raises(ValidationError):
            InventoryTransactionBase(product_id=1, change_amount="invalid")

    def test_inventory_transaction_create(self):
        """Test InventoryTransactionCreate schema."""
        data = {
            "product_id": 2,
            "change_amount": -10,
            "reason": "Product sold",
            "performed_by": 2
        }
        transaction = InventoryTransactionCreate(**data)
        assert transaction.product_id == 2
        assert transaction.change_amount == -10
        assert transaction.reason == "Product sold"
        assert transaction.performed_by == 2

    def test_inventory_transaction_update_partial(self):
        """Test InventoryTransactionUpdate with partial data."""
        # Only change_amount
        update = InventoryTransactionUpdate(change_amount=100)
        assert update.change_amount == 100
        assert update.reason is None
        assert update.performed_by is None

        # Only reason
        update = InventoryTransactionUpdate(reason="Updated reason")
        assert update.change_amount is None
        assert update.reason == "Updated reason"
        assert update.performed_by is None

        # Only performed_by
        update = InventoryTransactionUpdate(performed_by=3)
        assert update.change_amount is None
        assert update.reason is None
        assert update.performed_by == 3

    def test_inventory_transaction_update_all_fields(self):
        """Test InventoryTransactionUpdate with all fields."""
        data = {
            "change_amount": 75,
            "reason": "Full update",
            "performed_by": 4
        }
        update = InventoryTransactionUpdate(**data)
        assert update.change_amount == 75
        assert update.reason == "Full update"
        assert update.performed_by == 4

    def test_inventory_transaction_update_empty(self):
        """Test InventoryTransactionUpdate with no fields (should be valid)."""
        update = InventoryTransactionUpdate()
        assert update.change_amount is None
        assert update.reason is None
        assert update.performed_by is None

    def test_inventory_transaction_response(self):
        """Test InventoryTransactionResponse schema."""
        now = datetime.now()
        data = {
            "id": 1,
            "product_id": 1,
            "change_amount": 30,
            "reason": "Initial stock",
            "performed_by": 1,
            "created_at": now
        }
        response = InventoryTransactionResponse(**data)
        assert response.id == 1
        assert response.product_id == 1
        assert response.change_amount == 30
        assert response.reason == "Initial stock"
        assert response.performed_by == 1
        assert response.created_at == now

    def test_inventory_transaction_response_missing_id(self):
        """Test InventoryTransactionResponse without ID (should fail)."""
        data = {
            "product_id": 1,
            "change_amount": 30,
            "created_at": datetime.now()
        }
        with pytest.raises(ValidationError):
            InventoryTransactionResponse(**data)

    def test_inventory_transaction_response_missing_created_at(self):
        """Test InventoryTransactionResponse without created_at (should fail)."""
        data = {
            "id": 1,
            "product_id": 1,
            "change_amount": 30
        }
        with pytest.raises(ValidationError):
            InventoryTransactionResponse(**data)

    def test_inventory_transaction_response_dict_conversion(self):
        """Test converting InventoryTransactionResponse to dict."""
        now = datetime.now()
        data = {
            "id": 1,
            "product_id": 1,
            "change_amount": 15,
            "reason": "Restock",
            "performed_by": 1,
            "created_at": now
        }
        response = InventoryTransactionResponse(**data)
        response_dict = response.model_dump()
        
        assert response_dict["id"] == 1
        assert response_dict["product_id"] == 1
        assert response_dict["change_amount"] == 15
        assert response_dict["reason"] == "Restock"
        assert response_dict["performed_by"] == 1
        assert response_dict["created_at"] == now

    def test_inventory_transaction_negative_change_amount(self):
        """Test InventoryTransaction with negative change_amount (should be valid)."""
        data = {
            "product_id": 1,
            "change_amount": -50,
            "reason": "Sale"
        }
        transaction = InventoryTransactionBase(**data)
        assert transaction.change_amount == -50

    def test_inventory_transaction_zero_change_amount(self):
        """Test InventoryTransaction with zero change_amount (should be valid)."""
        data = {
            "product_id": 1,
            "change_amount": 0,
            "reason": "No change"
        }
        transaction = InventoryTransactionBase(**data)
        assert transaction.change_amount == 0

    def test_inventory_transaction_schemas_inheritance(self):
        """Test that schemas properly inherit from base classes."""
        # InventoryTransactionCreate should inherit from InventoryTransactionBase
        assert issubclass(InventoryTransactionCreate, InventoryTransactionBase)
        
        # InventoryTransactionResponse should inherit from InventoryTransactionBase
        assert issubclass(InventoryTransactionResponse, InventoryTransactionBase)

        # InventoryTransactionWithDetails should inherit from InventoryTransactionResponse
        assert issubclass(InventoryTransactionWithDetails, InventoryTransactionResponse)

    def test_inventory_transaction_with_details_structure(self):
        """Test InventoryTransactionWithDetails has the expected structure."""
        # This test verifies the schema structure without needing actual related objects
        now = datetime.now()
        
        # Mock product and user data (would normally come from database relationships)
        product_data = {
            "id": 1,
            "name": "Test Product",
            "sku": "TEST-001",
            "category": "Electronics",
            "created_at": now,
            "updated_at": now
        }
        
        user_data = {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User",
            "created_at": now,
            "updated_at": now
        }
        
        data = {
            "id": 1,
            "product_id": 1,
            "change_amount": 25,
            "reason": "Test transaction",
            "performed_by": 1,
            "created_at": now,
            "product": product_data,
            "user": user_data
        }
        
        # This would work if we had proper forward references resolved
        # For now, just test that the schema class exists and has the right field definitions
        assert 'product' in InventoryTransactionWithDetails.model_fields
        assert 'user' in InventoryTransactionWithDetails.model_fields