"""Tests for Inventory service."""

import pytest
from unittest.mock import patch
from app.services.inventory_service import (
    create_inventory_item,
    get_inventory_item,
    get_inventory_item_with_product,
    get_inventory_items,
    get_inventory_by_product,
    get_inventory_by_location,
    update_inventory_item,
    delete_inventory_item,
    adjust_inventory_quantity,
    get_low_stock_items,
    update_inventory_with_transaction
)
from app.models.inventory import Inventory
from app.models.product import Product
from app.schemas.inventory import InventoryCreate, InventoryUpdate


@pytest.fixture
def sample_product(db_session):
    """Create a sample product for inventory testing."""
    product = Product(name="Test Product", sku="TEST-001", category="Electronics")
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


@pytest.fixture
def sample_inventory_data(sample_product):
    """Sample inventory data for testing."""
    return InventoryCreate(
        quantity=100,
        location="Warehouse A",
        product_id=sample_product.id
    )


@pytest.fixture
def multiple_products(db_session):
    """Create multiple products for testing."""
    products = []
    for i in range(3):
        product = Product(name=f"Product {i+1}", sku=f"PROD-{i+1:03d}", category="Test")
        db_session.add(product)
        products.append(product)
    db_session.commit()
    for product in products:
        db_session.refresh(product)
    return products


class TestInventoryService:
    """Test cases for the Inventory service."""

    def test_create_inventory_item(self, db_session, sample_inventory_data):
        """Test creating an inventory item."""
        created_inventory = create_inventory_item(db_session, sample_inventory_data)
        
        assert created_inventory.id is not None
        assert created_inventory.quantity == 100
        assert created_inventory.location == "Warehouse A"
        assert created_inventory.product_id == sample_inventory_data.product_id
        assert created_inventory.updated_at is not None

    def test_get_inventory_item_existing(self, db_session, sample_product):
        """Test getting an existing inventory item."""
        # Create inventory item directly
        inventory = Inventory(quantity=50, location="Storage B", product_id=sample_product.id)
        db_session.add(inventory)
        db_session.commit()
        inventory_id = inventory.id

        # Get the inventory item
        retrieved_inventory = get_inventory_item(db_session, inventory_id)
        
        assert retrieved_inventory is not None
        assert retrieved_inventory.id == inventory_id
        assert retrieved_inventory.quantity == 50
        assert retrieved_inventory.location == "Storage B"

    def test_get_inventory_item_nonexistent(self, db_session):
        """Test getting a non-existent inventory item."""
        retrieved_inventory = get_inventory_item(db_session, 999)
        assert retrieved_inventory is None

    def test_get_inventory_item_with_product(self, db_session, sample_product):
        """Test getting an inventory item with product details."""
        inventory = Inventory(quantity=25, location="Store Front", product_id=sample_product.id)
        db_session.add(inventory)
        db_session.commit()
        inventory_id = inventory.id

        retrieved_inventory = get_inventory_item_with_product(db_session, inventory_id)
        
        assert retrieved_inventory is not None
        assert retrieved_inventory.product is not None
        assert retrieved_inventory.product.name == "Test Product"
        assert retrieved_inventory.product.sku == "TEST-001"

    def test_get_inventory_items_empty(self, db_session):
        """Test getting inventory items from empty database."""
        items = get_inventory_items(db_session)
        assert items == []

    def test_get_inventory_items_with_data(self, db_session, multiple_products):
        """Test getting inventory items with data."""
        # Add inventory items for each product
        for i, product in enumerate(multiple_products):
            inventory = Inventory(quantity=i*10 + 10, location=f"Location {i+1}", product_id=product.id)
            db_session.add(inventory)
        db_session.commit()

        items = get_inventory_items(db_session)
        assert len(items) == 3

    def test_get_inventory_items_pagination(self, db_session, multiple_products):
        """Test inventory items pagination."""
        # Add inventory items
        for i, product in enumerate(multiple_products):
            inventory = Inventory(quantity=i*10 + 10, location=f"Location {i+1}", product_id=product.id)
            db_session.add(inventory)
        db_session.commit()

        # Test skip and limit
        items_page1 = get_inventory_items(db_session, skip=0, limit=2)
        items_page2 = get_inventory_items(db_session, skip=2, limit=2)
        
        assert len(items_page1) == 2
        assert len(items_page2) == 1
        
        # Verify different items
        page1_ids = [item.id for item in items_page1]
        page2_ids = [item.id for item in items_page2]
        assert not set(page1_ids).intersection(set(page2_ids))

    def test_get_inventory_items_include_product(self, db_session, sample_product):
        """Test getting inventory items with product information."""
        inventory = Inventory(quantity=30, location="Warehouse C", product_id=sample_product.id)
        db_session.add(inventory)
        db_session.commit()

        items = get_inventory_items(db_session, include_product=True)
        
        assert len(items) == 1
        assert items[0].product is not None
        assert items[0].product.name == "Test Product"

    def test_get_inventory_by_product(self, db_session, sample_product):
        """Test getting inventory items by product."""
        # Add multiple inventory items for the same product
        for i in range(3):
            inventory = Inventory(quantity=i*5 + 5, location=f"Loc {i+1}", product_id=sample_product.id)
            db_session.add(inventory)
        db_session.commit()

        items = get_inventory_by_product(db_session, sample_product.id)
        
        assert len(items) == 3
        for item in items:
            assert item.product_id == sample_product.id

    def test_get_inventory_by_product_nonexistent(self, db_session):
        """Test getting inventory by non-existent product."""
        items = get_inventory_by_product(db_session, 999)
        assert items == []

    def test_get_inventory_by_location(self, db_session, multiple_products):
        """Test getting inventory items by location."""
        # Add inventory items with different locations
        locations = ["Warehouse Main", "Warehouse East", "Store Main"]
        for i, product in enumerate(multiple_products):
            inventory = Inventory(quantity=20, location=locations[i], product_id=product.id)
            db_session.add(inventory)
        db_session.commit()

        # Test exact location match
        items = get_inventory_by_location(db_session, "Main")
        assert len(items) == 2  # Should match "Warehouse Main" and "Store Main"

    def test_get_inventory_by_location_with_pagination(self, db_session, multiple_products):
        """Test getting inventory by location with pagination."""
        # Add multiple items with same location pattern
        for i, product in enumerate(multiple_products):
            inventory = Inventory(quantity=15, location="Central Warehouse", product_id=product.id)
            db_session.add(inventory)
        db_session.commit()

        items = get_inventory_by_location(db_session, "Central", skip=0, limit=2)
        assert len(items) == 2

        items_page2 = get_inventory_by_location(db_session, "Central", skip=2, limit=2)
        assert len(items_page2) == 1

    def test_update_inventory_item_existing(self, db_session, sample_product):
        """Test updating an existing inventory item."""
        # Create inventory item
        inventory = Inventory(quantity=40, location="Old Location", product_id=sample_product.id)
        db_session.add(inventory)
        db_session.commit()
        inventory_id = inventory.id

        # Update the inventory item
        update_data = InventoryUpdate(quantity=60, location="New Location")
        updated_inventory = update_inventory_item(db_session, inventory_id, update_data)
        
        assert updated_inventory is not None
        assert updated_inventory.quantity == 60
        assert updated_inventory.location == "New Location"
        assert updated_inventory.product_id == sample_product.id

    def test_update_inventory_item_partial(self, db_session, sample_product):
        """Test partial update of inventory item."""
        # Create inventory item
        inventory = Inventory(quantity=35, location="Original Spot", product_id=sample_product.id)
        db_session.add(inventory)
        db_session.commit()
        inventory_id = inventory.id

        # Update only quantity
        update_data = InventoryUpdate(quantity=45)
        updated_inventory = update_inventory_item(db_session, inventory_id, update_data)
        
        assert updated_inventory is not None
        assert updated_inventory.quantity == 45
        assert updated_inventory.location == "Original Spot"  # Should remain unchanged

    def test_update_inventory_item_nonexistent(self, db_session):
        """Test updating a non-existent inventory item."""
        update_data = InventoryUpdate(quantity=100)
        updated_inventory = update_inventory_item(db_session, 999, update_data)
        
        assert updated_inventory is None

    def test_delete_inventory_item_existing(self, db_session, sample_product):
        """Test deleting an existing inventory item."""
        # Create inventory item
        inventory = Inventory(quantity=20, location="To Be Deleted", product_id=sample_product.id)
        db_session.add(inventory)
        db_session.commit()
        inventory_id = inventory.id

        # Delete the inventory item
        result = delete_inventory_item(db_session, inventory_id)
        
        assert result is True
        
        # Verify it's deleted
        deleted_inventory = get_inventory_item(db_session, inventory_id)
        assert deleted_inventory is None

    def test_delete_inventory_item_nonexistent(self, db_session):
        """Test deleting a non-existent inventory item."""
        result = delete_inventory_item(db_session, 999)
        assert result is False

    def test_adjust_inventory_quantity_positive(self, db_session, sample_product):
        """Test adjusting inventory quantity with positive change."""
        # Create inventory item
        inventory = Inventory(quantity=50, location="Test Loc", product_id=sample_product.id)
        db_session.add(inventory)
        db_session.commit()
        inventory_id = inventory.id

        # Mock the transaction service to avoid circular imports during testing
        with patch('app.services.inventory_transaction_service.create_transaction') as mock_create_transaction:
            adjusted_inventory = adjust_inventory_quantity(
                db_session, 
                inventory_id, 
                quantity_change=25,
                reason="Stock replenishment",
                performed_by=1
            )
            
            assert adjusted_inventory is not None
            assert adjusted_inventory.quantity == 75
            
            # Verify transaction was created
            mock_create_transaction.assert_called_once()

    def test_adjust_inventory_quantity_negative(self, db_session, sample_product):
        """Test adjusting inventory quantity with negative change."""
        inventory = Inventory(quantity=30, location="Test Loc", product_id=sample_product.id)
        db_session.add(inventory)
        db_session.commit()
        inventory_id = inventory.id

        with patch('app.services.inventory_transaction_service.create_transaction') as mock_create_transaction:
            adjusted_inventory = adjust_inventory_quantity(
                db_session, 
                inventory_id, 
                quantity_change=-15,
                reason="Sale",
                performed_by=1
            )
            
            assert adjusted_inventory is not None
            assert adjusted_inventory.quantity == 15
            mock_create_transaction.assert_called_once()

    def test_adjust_inventory_quantity_negative_overflow(self, db_session, sample_product):
        """Test adjusting inventory quantity that would go negative."""
        inventory = Inventory(quantity=10, location="Test Loc", product_id=sample_product.id)
        db_session.add(inventory)
        db_session.commit()
        inventory_id = inventory.id

        with patch('app.services.inventory_transaction_service.create_transaction') as mock_create_transaction:
            adjusted_inventory = adjust_inventory_quantity(
                db_session, 
                inventory_id, 
                quantity_change=-20,  # More than available
                reason="Large order",
                performed_by=1
            )
            
            assert adjusted_inventory is not None
            assert adjusted_inventory.quantity == 0  # Should not go negative
            # Transaction should record actual change (-10, not -20)
            mock_create_transaction.assert_called_once()

    def test_adjust_inventory_quantity_no_transaction(self, db_session, sample_product):
        """Test adjusting inventory quantity without creating transaction."""
        inventory = Inventory(quantity=40, location="Test Loc", product_id=sample_product.id)
        db_session.add(inventory)
        db_session.commit()
        inventory_id = inventory.id

        with patch('app.services.inventory_transaction_service.create_transaction') as mock_create_transaction:
            adjusted_inventory = adjust_inventory_quantity(
                db_session, 
                inventory_id, 
                quantity_change=10,
                create_transaction=False
            )
            
            assert adjusted_inventory is not None
            assert adjusted_inventory.quantity == 50
            
            # Verify no transaction was created
            mock_create_transaction.assert_not_called()

    def test_adjust_inventory_quantity_nonexistent(self, db_session):
        """Test adjusting quantity of non-existent inventory item."""
        result = adjust_inventory_quantity(db_session, 999, 10)
        assert result is None

    def test_get_low_stock_items(self, db_session, multiple_products):
        """Test getting low stock items."""
        # Create inventory items with different quantities
        quantities = [5, 15, 8]  # 5 and 8 are below default threshold of 10
        for i, product in enumerate(multiple_products):
            inventory = Inventory(quantity=quantities[i], location=f"Loc {i+1}", product_id=product.id)
            db_session.add(inventory)
        db_session.commit()

        low_stock_items = get_low_stock_items(db_session)
        
        assert len(low_stock_items) == 2
        low_stock_quantities = [item.quantity for item in low_stock_items]
        assert 5 in low_stock_quantities
        assert 8 in low_stock_quantities
        assert 15 not in low_stock_quantities

    def test_get_low_stock_items_custom_threshold(self, db_session, multiple_products):
        """Test getting low stock items with custom threshold."""
        quantities = [5, 15, 8]
        for i, product in enumerate(multiple_products):
            inventory = Inventory(quantity=quantities[i], location=f"Loc {i+1}", product_id=product.id)
            db_session.add(inventory)
        db_session.commit()

        # Use threshold of 6, so only quantity 5 should be returned
        low_stock_items = get_low_stock_items(db_session, threshold=6)
        
        assert len(low_stock_items) == 1
        assert low_stock_items[0].quantity == 5

    def test_get_low_stock_items_with_pagination(self, db_session, multiple_products):
        """Test getting low stock items with pagination."""
        # Create multiple low stock items
        for i, product in enumerate(multiple_products):
            inventory = Inventory(quantity=i+1, location=f"Loc {i+1}", product_id=product.id)  # quantities: 1, 2, 3
            db_session.add(inventory)
        db_session.commit()

        # All should be low stock (threshold 10), test pagination
        items_page1 = get_low_stock_items(db_session, skip=0, limit=2)
        items_page2 = get_low_stock_items(db_session, skip=2, limit=2)
        
        assert len(items_page1) == 2
        assert len(items_page2) == 1

    def test_update_inventory_with_transaction(self, db_session, sample_product):
        """Test updating inventory with transaction creation."""
        inventory = Inventory(quantity=100, location="Main Store", product_id=sample_product.id)
        db_session.add(inventory)
        db_session.commit()
        inventory_id = inventory.id

        with patch('app.services.inventory_transaction_service.create_transaction') as mock_create_transaction:
            updated_inventory = update_inventory_with_transaction(
                db_session,
                inventory_id,
                new_quantity=85,
                reason="Customer purchase",
                performed_by=2
            )
            
            assert updated_inventory is not None
            assert updated_inventory.quantity == 85
            
            # Verify transaction creation with correct change amount
            mock_create_transaction.assert_called_once()
            call_args = mock_create_transaction.call_args
            transaction_data = call_args.kwargs['transaction']
            assert transaction_data.change_amount == -15  # 85 - 100
            assert transaction_data.reason == "Customer purchase"
            assert transaction_data.performed_by == 2

    def test_update_inventory_with_transaction_no_change(self, db_session, sample_product):
        """Test updating inventory with same quantity (no transaction needed)."""
        inventory = Inventory(quantity=75, location="Branch Store", product_id=sample_product.id)
        db_session.add(inventory)
        db_session.commit()
        inventory_id = inventory.id

        with patch('app.services.inventory_transaction_service.create_transaction') as mock_create_transaction:
            updated_inventory = update_inventory_with_transaction(
                db_session,
                inventory_id,
                new_quantity=75,  # Same quantity
                reason="No change test"
            )
            
            assert updated_inventory is not None
            assert updated_inventory.quantity == 75
            
            # No transaction should be created for zero change
            mock_create_transaction.assert_not_called()

    def test_update_inventory_with_transaction_nonexistent(self, db_session):
        """Test updating non-existent inventory with transaction."""
        with patch('app.services.inventory_transaction_service.create_transaction') as mock_create_transaction:
            result = update_inventory_with_transaction(
                db_session,
                999,
                new_quantity=50,
                reason="Test"
            )
            
            assert result is None
            mock_create_transaction.assert_not_called()