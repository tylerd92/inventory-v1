"""Tests for Product model."""
from app.models.product import Product


class TestProductModel:
    """Test cases for the Product model."""

    def test_product_creation(self, db_session):
        """Test creating a Product instance."""
        product = Product(
            name="Test Product",
            sku="TEST-001",
            category="Electronics"
        )
        db_session.add(product)
        db_session.commit()

        assert product.id is not None
        assert product.name == "Test Product"
        assert product.sku == "TEST-001"
        assert product.category == "Electronics"
        assert product.created_at is not None
        assert product.updated_at is not None

    def test_product_table_name(self):
        """Test that the Product model has correct table name."""
        assert Product.__tablename__ == "products"

    def test_product_columns(self):
        """Test that the Product model has all required columns."""
        columns = [column.name for column in Product.__table__.columns]
        expected_columns = ["id", "name", "sku", "category", "created_at", "updated_at"]
        for column in expected_columns:
            assert column in columns

    def test_product_query(self, db_session):
        """Test querying products from the database."""
        # Create test products
        product1 = Product(name="Product 1", sku="PROD-001", category="Category 1")
        product2 = Product(name="Product 2", sku="PROD-002", category="Category 2")
        
        db_session.add(product1)
        db_session.add(product2)
        db_session.commit()

        # Query all products
        products = db_session.query(Product).all()
        assert len(products) == 2

        # Query by name
        product = db_session.query(Product).filter(Product.name == "Product 1").first()
        assert product is not None
        assert product.name == "Product 1"
        assert product.sku == "PROD-001"

    def test_product_update(self, db_session):
        """Test updating a product in the database."""
        product = Product(name="Original Name", sku="ORIG-001", category="Original Category")
        db_session.add(product)
        db_session.commit()

        # Update the product
        product.name = "Updated Name"
        product.sku = "UPD-001"
        db_session.commit()

        # Verify the update
        updated_product = db_session.query(Product).filter(Product.id == product.id).first()
        assert updated_product.name == "Updated Name"
        assert updated_product.sku == "UPD-001"
        assert updated_product.category == "Original Category"

    def test_product_delete(self, db_session):
        """Test deleting a product from the database."""
        product = Product(name="To Delete", sku="DEL-001", category="Test")
        db_session.add(product)
        db_session.commit()
        product_id = product.id

        # Delete the product
        db_session.delete(product)
        db_session.commit()

        # Verify the product is deleted
        deleted_product = db_session.query(Product).filter(Product.id == product_id).first()
        assert deleted_product is None