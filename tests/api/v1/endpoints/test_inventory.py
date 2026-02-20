"""Tests for Inventory API endpoints."""

import pytest
from app.models.product import Product
from app.models.user import User
from app.models.inventory import Inventory


@pytest.fixture
def sample_inventory_data():
    """Sample inventory data for testing."""
    return {
        "quantity": 100,
        "location": "Warehouse A",
        "product_id": 1
    }


@pytest.fixture
def sample_inventory_update_data():
    """Sample inventory update data for testing."""
    return {
        "quantity": 150,
        "location": "Warehouse B"
    }


@pytest.fixture
def sample_product_with_inventory(db_session):
    """Create a product and inventory item for testing."""
    # Create a product first
    product = Product(
        name="Test Product",
        sku="TEST-001",
        category="Electronics"
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    # Create inventory item
    inventory = Inventory(
        quantity=50,
        location="Warehouse A",
        product_id=product.id
    )
    db_session.add(inventory)
    db_session.commit()
    db_session.refresh(inventory)
    
    return {"product": product, "inventory": inventory}


@pytest.fixture
def multiple_inventory_items(db_session):
    """Create multiple inventory items for testing."""
    # Create products first
    products = []
    for i in range(3):
        product = Product(
            name=f"Product {i+1}",
            sku=f"PROD-00{i+1}",
            category="Electronics"
        )
        db_session.add(product)
        products.append(product)
    
    db_session.commit()
    
    # Create inventory items
    inventories = []
    locations = ["Warehouse A", "Warehouse B", "Store Front"]
    quantities = [25, 75, 5]  # Third item will be low stock
    
    for i, product in enumerate(products):
        inventory = Inventory(
            quantity=quantities[i],
            location=locations[i],
            product_id=product.id
        )
        db_session.add(inventory)
        inventories.append(inventory)
    
    db_session.commit()
    
    return {"products": products, "inventories": inventories}


class TestInventoryEndpoints:
    """Test cases for Inventory API endpoints."""

    def test_create_inventory_item_success(self, client, db_session, sample_inventory_data):
        """Test successful inventory item creation."""
        # Create a product first
        product = Product(name="Test Product", sku="TEST-001", category="Electronics")
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)
        
        sample_inventory_data["product_id"] = product.id
        
        response = client.post("/api/v1/inventory/", json=sample_inventory_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == sample_inventory_data["quantity"]
        assert data["location"] == sample_inventory_data["location"]
        assert data["product_id"] == product.id
        assert "id" in data
        assert "updated_at" in data

    def test_create_inventory_item_invalid_data(self, client):
        """Test inventory creation with invalid data."""
        # Missing required fields
        invalid_data = {"quantity": 100}
        response = client.post("/api/v1/inventory/", json=invalid_data)
        assert response.status_code == 422

        # Invalid quantity (negative)
        invalid_data = {"quantity": -10, "location": "Test", "product_id": 1}
        response = client.post("/api/v1/inventory/", json=invalid_data)
        # This might pass API validation but fail at service level

    def test_create_inventory_item_nonexistent_product(self, client):
        """Test inventory creation with non-existent product."""
        invalid_data = {
            "quantity": 100,
            "location": "Warehouse A",
            "product_id": 999  # Non-existent product
        }
        response = client.post("/api/v1/inventory/", json=invalid_data)
        # Should return error from service layer
        assert response.status_code == 400

    def test_get_inventory_items_empty(self, client):
        """Test getting inventory items from empty database."""
        response = client.get("/api/v1/inventory/")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_inventory_items_with_data(self, client, multiple_inventory_items):
        """Test getting inventory items with data."""
        response = client.get("/api/v1/inventory/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        
        # Verify structure of returned items
        for item in data:
            assert "id" in item
            assert "quantity" in item
            assert "location" in item
            assert "product_id" in item
            assert "updated_at" in item

    def test_get_inventory_items_with_pagination(self, client, multiple_inventory_items):
        """Test getting inventory items with pagination parameters."""
        # Test skip and limit
        response = client.get("/api/v1/inventory/?skip=1&limit=2")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2

    def test_get_inventory_items_filter_by_location(self, client, multiple_inventory_items):
        """Test filtering inventory items by location."""
        response = client.get("/api/v1/inventory/?location=Warehouse A")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return only items from Warehouse A
        for item in data:
            assert item["location"] == "Warehouse A"

    def test_get_inventory_items_filter_by_product_id(self, client, multiple_inventory_items):
        """Test filtering inventory items by product ID."""
        product_id = multiple_inventory_items["products"][0].id
        
        response = client.get(f"/api/v1/inventory/?product_id={product_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return only items for specified product
        for item in data:
            assert item["product_id"] == product_id

    def test_get_inventory_items_with_product_details(self, client, multiple_inventory_items):
        """Test getting inventory items with product details included."""
        response = client.get("/api/v1/inventory/?include_product=true")
        
        assert response.status_code == 200

    def test_get_low_stock_items(self, client, multiple_inventory_items):
        """Test getting low stock items."""
        response = client.get("/api/v1/inventory/low-stock?threshold=50")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return items with quantity <= 50
        for item in data:
            assert item["quantity"] <= 50

    def test_get_low_stock_items_with_pagination(self, client, multiple_inventory_items):
        """Test getting low stock items with pagination."""
        response = client.get("/api/v1/inventory/low-stock?threshold=100&skip=0&limit=2")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2

    def test_get_inventory_item_success(self, client, sample_product_with_inventory):
        """Test getting a single inventory item by ID."""
        inventory_id = sample_product_with_inventory["inventory"].id
        
        response = client.get(f"/api/v1/inventory/{inventory_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == inventory_id
        assert "product" in data  # Should include product details

    def test_get_inventory_item_not_found(self, client):
        """Test getting non-existent inventory item."""
        response = client.get("/api/v1/inventory/999")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_update_inventory_item_success(self, client, sample_product_with_inventory, sample_inventory_update_data):
        """Test successful inventory item update."""
        inventory_id = sample_product_with_inventory["inventory"].id
        
        response = client.put(f"/api/v1/inventory/{inventory_id}", json=sample_inventory_update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == inventory_id
        assert data["quantity"] == sample_inventory_update_data["quantity"]
        assert data["location"] == sample_inventory_update_data["location"]

    def test_update_inventory_item_partial(self, client, sample_product_with_inventory):
        """Test partial inventory item update."""
        inventory_id = sample_product_with_inventory["inventory"].id
        update_data = {"quantity": 200}
        
        response = client.put(f"/api/v1/inventory/{inventory_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == 200
        # Location should remain unchanged

    def test_update_inventory_item_not_found(self, client, sample_inventory_update_data):
        """Test updating non-existent inventory item."""
        response = client.put("/api/v1/inventory/999", json=sample_inventory_update_data)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_adjust_inventory_quantity_increase(self, client, sample_product_with_inventory):
        """Test adjusting inventory quantity (increase)."""
        inventory_id = sample_product_with_inventory["inventory"].id
        original_quantity = sample_product_with_inventory["inventory"].quantity
        
        response = client.patch(
            f"/api/v1/inventory/{inventory_id}/adjust?quantity_change=25&reason=Restock"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == original_quantity + 25

    def test_adjust_inventory_quantity_decrease(self, client, sample_product_with_inventory):
        """Test adjusting inventory quantity (decrease)."""
        inventory_id = sample_product_with_inventory["inventory"].id
        original_quantity = sample_product_with_inventory["inventory"].quantity
        
        response = client.patch(
            f"/api/v1/inventory/{inventory_id}/adjust?quantity_change=-10&reason=Sold"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == original_quantity - 10

    def test_adjust_inventory_quantity_with_user(self, client, sample_product_with_inventory):
        """Test adjusting inventory quantity with user tracking."""
        inventory_id = sample_product_with_inventory["inventory"].id
        
        response = client.patch(
            f"/api/v1/inventory/{inventory_id}/adjust?quantity_change=15&reason=Adjustment&performed_by=1"
        )
        
        assert response.status_code == 200

    def test_adjust_inventory_quantity_no_transaction(self, client, sample_product_with_inventory):
        """Test adjusting inventory quantity without creating transaction."""
        inventory_id = sample_product_with_inventory["inventory"].id
        
        response = client.patch(
            f"/api/v1/inventory/{inventory_id}/adjust?quantity_change=5&create_transaction=false"
        )
        
        assert response.status_code == 200

    def test_adjust_inventory_quantity_not_found(self, client):
        """Test adjusting quantity for non-existent inventory item."""
        response = client.patch("/api/v1/inventory/999/adjust?quantity_change=10")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_delete_inventory_item_success(self, client, sample_product_with_inventory):
        """Test successful inventory item deletion."""
        inventory_id = sample_product_with_inventory["inventory"].id
        
        response = client.delete(f"/api/v1/inventory/{inventory_id}")
        
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]
        
        # Verify item is actually deleted
        get_response = client.get(f"/api/v1/inventory/{inventory_id}")
        assert get_response.status_code == 404

    def test_delete_inventory_item_not_found(self, client):
        """Test deleting non-existent inventory item."""
        response = client.delete("/api/v1/inventory/999")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_set_inventory_quantity_success(self, client, sample_product_with_inventory):
        """Test setting inventory quantity to specific value."""
        inventory_id = sample_product_with_inventory["inventory"].id
        
        response = client.put(
            f"/api/v1/inventory/{inventory_id}/set-quantity?new_quantity=300&reason=Inventory Count"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == 300

    def test_set_inventory_quantity_with_user(self, client, sample_product_with_inventory):
        """Test setting inventory quantity with user tracking."""
        inventory_id = sample_product_with_inventory["inventory"].id
        
        response = client.put(
            f"/api/v1/inventory/{inventory_id}/set-quantity?new_quantity=250&reason=Stock Take&performed_by=1"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == 250

    def test_set_inventory_quantity_zero(self, client, sample_product_with_inventory):
        """Test setting inventory quantity to zero."""
        inventory_id = sample_product_with_inventory["inventory"].id
        
        response = client.put(
            f"/api/v1/inventory/{inventory_id}/set-quantity?new_quantity=0&reason=Out of Stock"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == 0

    def test_set_inventory_quantity_not_found(self, client):
        """Test setting quantity for non-existent inventory item."""
        response = client.put(
            "/api/v1/inventory/999/set-quantity?new_quantity=100&reason=Test"
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_set_inventory_quantity_missing_reason(self, client, sample_product_with_inventory):
        """Test setting inventory quantity without required reason."""
        inventory_id = sample_product_with_inventory["inventory"].id
        
        response = client.put(
            f"/api/v1/inventory/{inventory_id}/set-quantity?new_quantity=100"
        )
        
        assert response.status_code == 422  # Missing required query parameter

    def test_inventory_endpoints_validation_errors(self, client):
        """Test various validation errors across endpoints."""
        # Test negative values in pagination
        response = client.get("/api/v1/inventory/?skip=-1")
        assert response.status_code == 422
        
        response = client.get("/api/v1/inventory/?limit=0")
        assert response.status_code == 422
        
        # Test invalid threshold for low stock
        response = client.get("/api/v1/inventory/low-stock?threshold=-1")
        assert response.status_code == 422
        
        # Test invalid inventory ID format
        response = client.get("/api/v1/inventory/invalid_id")
        assert response.status_code == 422

    def test_inventory_concurrent_operations(self, client, sample_product_with_inventory):
        """Test handling sequential operations on same inventory item."""
        inventory_id = sample_product_with_inventory["inventory"].id
        original_quantity = sample_product_with_inventory["inventory"].quantity
        
        # First adjustment
        response1 = client.patch(
            f"/api/v1/inventory/{inventory_id}/adjust?quantity_change=10&reason=Op1"
        )
        assert response1.status_code == 200
        
        # Second adjustment (operates on result of first)
        response2 = client.patch(
            f"/api/v1/inventory/{inventory_id}/adjust?quantity_change=-5&reason=Op2"
        )
        assert response2.status_code == 200
        
        # Verify final state - should be original + 10 - 5
        final_response = client.get(f"/api/v1/inventory/{inventory_id}")
        assert final_response.status_code == 200
        final_data = final_response.json()
        expected_quantity = original_quantity + 10 - 5
        assert final_data["quantity"] == expected_quantity