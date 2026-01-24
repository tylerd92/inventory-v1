"""Tests for Product service."""

import pytest
from app.services.product_service import (
    create_product,
    get_product,
    get_products,
    update_product,
    delete_product,
    search_products
)
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


class TestProductService:
    """Test cases for the Product service."""

    def test_create_product(self, db_session):
        """Test creating a product through service."""
        product_data = ProductCreate(
            name="Service Test Product",
            quantity=100,
            category="Test Category"
        )
        
        created_product = create_product(db_session, product_data)
        
        assert created_product.id is not None
        assert created_product.name == "Service Test Product"
        assert created_product.quantity == 100
        assert created_product.category == "Test Category"

    def test_get_product_existing(self, db_session):
        """Test getting an existing product."""
        # Create a product first
        product = Product(name="Get Test Product", quantity=50, category="Get Category")
        db_session.add(product)
        db_session.commit()
        product_id = product.id

        # Get the product
        retrieved_product = get_product(db_session, product_id)
        
        assert retrieved_product is not None
        assert retrieved_product.id == product_id
        assert retrieved_product.name == "Get Test Product"

    def test_get_product_nonexistent(self, db_session):
        """Test getting a non-existent product."""
        retrieved_product = get_product(db_session, 999)
        assert retrieved_product is None

    def test_get_products_empty(self, db_session):
        """Test getting products from empty database."""
        products = get_products(db_session)
        assert products == []

    def test_get_products_with_data(self, db_session, sample_products_data):
        """Test getting products with data."""
        # Add sample products
        for product_data in sample_products_data:
            product = Product(**product_data)
            db_session.add(product)
        db_session.commit()

        products = get_products(db_session)
        assert len(products) == 4

    def test_get_products_pagination(self, db_session, sample_products_data):
        """Test products pagination."""
        # Add sample products
        for product_data in sample_products_data:
            product = Product(**product_data)
            db_session.add(product)
        db_session.commit()

        # Test skip and limit
        products_page1 = get_products(db_session, skip=0, limit=2)
        products_page2 = get_products(db_session, skip=2, limit=2)
        
        assert len(products_page1) == 2
        assert len(products_page2) == 2
        
        # Verify different products
        page1_ids = [p.id for p in products_page1]
        page2_ids = [p.id for p in products_page2]
        assert not set(page1_ids).intersection(set(page2_ids))

    def test_update_product_existing(self, db_session):
        """Test updating an existing product."""
        # Create a product
        product = Product(name="Original Name", quantity=100, category="Original")
        db_session.add(product)
        db_session.commit()
        product_id = product.id

        # Update the product
        update_data = ProductUpdate(name="Updated Name", quantity=200)
        updated_product = update_product(db_session, product_id, update_data)

        assert updated_product is not None
        assert updated_product.name == "Updated Name"
        assert updated_product.quantity == 200
        assert updated_product.category == "Original"  # Should remain unchanged

    def test_update_product_partial(self, db_session):
        """Test partially updating a product."""
        # Create a product
        product = Product(name="Original Name", quantity=100, category="Original")
        db_session.add(product)
        db_session.commit()
        product_id = product.id

        # Update only quantity
        update_data = ProductUpdate(quantity=300)
        updated_product = update_product(db_session, product_id, update_data)

        assert updated_product is not None
        assert updated_product.name == "Original Name"  # Should remain unchanged
        assert updated_product.quantity == 300
        assert updated_product.category == "Original"  # Should remain unchanged

    def test_update_product_nonexistent(self, db_session):
        """Test updating a non-existent product."""
        update_data = ProductUpdate(name="Should Not Work")
        updated_product = update_product(db_session, 999, update_data)
        assert updated_product is None

    def test_delete_product_existing(self, db_session):
        """Test deleting an existing product."""
        # Create a product
        product = Product(name="To Delete", quantity=50, category="Delete Category")
        db_session.add(product)
        db_session.commit()
        product_id = product.id

        # Delete the product
        result = delete_product(db_session, product_id)
        assert result is True

        # Verify it's deleted
        deleted_product = get_product(db_session, product_id)
        assert deleted_product is None

    def test_delete_product_nonexistent(self, db_session):
        """Test deleting a non-existent product."""
        result = delete_product(db_session, 999)
        assert result is False

    def test_search_products_by_name(self, db_session, sample_products_data):
        """Test searching products by name."""
        # Add sample products
        for product_data in sample_products_data:
            product = Product(**product_data)
            db_session.add(product)
        db_session.commit()

        # Search for products containing "Lap"
        products = search_products(db_session, name="Lap")
        assert len(products) == 1
        assert products[0].name == "Laptop"

    def test_search_products_by_category(self, db_session, sample_products_data):
        """Test searching products by category."""
        # Add sample products
        for product_data in sample_products_data:
            product = Product(**product_data)
            db_session.add(product)
        db_session.commit()

        # Search for Electronics category
        products = search_products(db_session, category="Electronics")
        assert len(products) == 2
        electronics_names = [p.name for p in products]
        assert "Laptop" in electronics_names
        assert "Phone" in electronics_names

    def test_search_products_by_name_and_category(self, db_session, sample_products_data):
        """Test searching products by both name and category."""
        # Add sample products
        for product_data in sample_products_data:
            product = Product(**product_data)
            db_session.add(product)
        db_session.commit()

        # Search for products with "Phone" in name and "Electronics" category
        products = search_products(db_session, name="Phone", category="Electronics")
        assert len(products) == 1
        assert products[0].name == "Phone"

    def test_search_products_no_results(self, db_session, sample_products_data):
        """Test searching products with no matching results."""
        # Add sample products
        for product_data in sample_products_data:
            product = Product(**product_data)
            db_session.add(product)
        db_session.commit()

        # Search for non-existent product
        products = search_products(db_session, name="NonExistent")
        assert products == []

    def test_search_products_pagination(self, db_session):
        """Test search products with pagination."""
        # Create multiple products with similar names
        for i in range(5):
            product = Product(name=f"Test Product {i}", quantity=10, category="Test")
            db_session.add(product)
        db_session.commit()

        # Search with pagination
        products_page1 = search_products(db_session, name="Test", skip=0, limit=3)
        products_page2 = search_products(db_session, name="Test", skip=3, limit=3)
        
        assert len(products_page1) == 3
        assert len(products_page2) == 2