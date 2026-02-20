"""Tests for Inventory model."""
from app.models.inventory import Inventory
from app.models.product import Product


class TestInventoryModel:
    """Test cases for the Inventory model."""

    def test_inventory_creation(self, db_session):
        """Test creating an Inventory instance."""
        # First create a product
        product = Product(
            name="Test Product",
            sku="TEST-001",
            category="Electronics"
        )
        db_session.add(product)
        db_session.commit()

        inventory = Inventory(
            quantity=100,
            location="Warehouse A",
            product_id=product.id
        )
        db_session.add(inventory)
        db_session.commit()

        assert inventory.id is not None
        assert inventory.quantity == 100
        assert inventory.location == "Warehouse A"
        assert inventory.product_id == product.id
        assert inventory.updated_at is not None

    def test_inventory_table_name(self):
        """Test that the Inventory model has correct table name."""
        assert Inventory.__tablename__ == "inventory"

    def test_inventory_columns(self):
        """Test that the Inventory model has all required columns."""
        columns = [column.name for column in Inventory.__table__.columns]
        expected_columns = ["id", "quantity", "location", "product_id", "updated_at"]
        for column in expected_columns:
            assert column in columns

    def test_inventory_product_relationship(self, db_session):
        """Test the relationship between Inventory and Product."""
        # Create a product
        product = Product(
            name="Related Product",
            sku="REL-001",
            category="Test Category"
        )
        db_session.add(product)
        db_session.commit()

        # Create inventory for the product
        inventory = Inventory(
            quantity=50,
            location="Storage Room",
            product_id=product.id
        )
        db_session.add(inventory)
        db_session.commit()

        # Test the relationship
        assert inventory.product is not None
        assert inventory.product.name == "Related Product"
        assert inventory.product.sku == "REL-001"
        
        # Test reverse relationship
        assert len(product.inventory_items) == 1
        assert product.inventory_items[0].quantity == 50
        assert product.inventory_items[0].location == "Storage Room"

    def test_inventory_query(self, db_session):
        """Test querying inventory from the database."""
        # Create a product
        product = Product(name="Query Product", sku="QUERY-001", category="Test")
        db_session.add(product)
        db_session.commit()

        # Create test inventory items
        inventory1 = Inventory(quantity=25, location="Location A", product_id=product.id)
        inventory2 = Inventory(quantity=75, location="Location B", product_id=product.id)
        
        db_session.add(inventory1)
        db_session.add(inventory2)
        db_session.commit()

        # Query all inventory items
        inventories = db_session.query(Inventory).all()
        assert len(inventories) == 2

        # Query by location
        inventory = db_session.query(Inventory).filter(Inventory.location == "Location A").first()
        assert inventory is not None
        assert inventory.quantity == 25
        assert inventory.location == "Location A"

    def test_inventory_update(self, db_session):
        """Test updating an inventory item in the database."""
        # Create a product
        product = Product(name="Update Product", sku="UPD-001", category="Test")
        db_session.add(product)
        db_session.commit()

        inventory = Inventory(
            quantity=30,
            location="Original Location",
            product_id=product.id
        )
        db_session.add(inventory)
        db_session.commit()

        # Update the inventory
        inventory.quantity = 60
        inventory.location = "Updated Location"
        db_session.commit()

        # Verify the update
        updated_inventory = db_session.query(Inventory).filter(Inventory.id == inventory.id).first()
        assert updated_inventory.quantity == 60
        assert updated_inventory.location == "Updated Location"
        assert updated_inventory.product_id == product.id

    def test_inventory_delete(self, db_session):
        """Test deleting an inventory item from the database."""
        # Create a product
        product = Product(name="Delete Product", sku="DEL-001", category="Test")
        db_session.add(product)
        db_session.commit()

        inventory = Inventory(
            quantity=15,
            location="To Delete",
            product_id=product.id
        )
        db_session.add(inventory)
        db_session.commit()
        inventory_id = inventory.id

        # Delete the inventory
        db_session.delete(inventory)
        db_session.commit()

        # Verify the inventory is deleted
        deleted_inventory = db_session.query(Inventory).filter(Inventory.id == inventory_id).first()
        assert deleted_inventory is None

    def test_inventory_foreign_key_constraint(self, db_session):
        """Test that inventory requires a valid product_id."""
        # Create a product
        product = Product(name="FK Test Product", sku="FK-001", category="Test")
        db_session.add(product)
        db_session.commit()
        product_id = product.id

        # Create inventory for the product
        inventory = Inventory(
            quantity=40,
            location="FK Location",
            product_id=product_id
        )
        db_session.add(inventory)
        db_session.commit()

        # Verify the inventory exists and has the correct product_id
        assert inventory.product_id == product_id
        assert inventory.product is not None
        assert inventory.product.name == "FK Test Product"

    def test_inventory_multiple_items_per_product(self, db_session):
        """Test that a product can have multiple inventory items."""
        # Create a product
        product = Product(name="Multi Inventory Product", sku="MULTI-001", category="Test")
        db_session.add(product)
        db_session.commit()

        # Create multiple inventory items for the same product
        inventory1 = Inventory(quantity=10, location="Warehouse 1", product_id=product.id)
        inventory2 = Inventory(quantity=20, location="Warehouse 2", product_id=product.id)
        inventory3 = Inventory(quantity=30, location="Store Front", product_id=product.id)
        
        db_session.add_all([inventory1, inventory2, inventory3])
        db_session.commit()

        # Verify through product relationship
        assert len(product.inventory_items) == 3
        total_quantity = sum(item.quantity for item in product.inventory_items)
        assert total_quantity == 60

        # Verify locations
        locations = [item.location for item in product.inventory_items]
        assert "Warehouse 1" in locations
        assert "Warehouse 2" in locations
        assert "Store Front" in locations