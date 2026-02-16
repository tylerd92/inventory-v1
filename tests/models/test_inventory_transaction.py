"""Tests for InventoryTransaction model."""

import pytest
from app.models.inventory_transaction import InventoryTransaction
from app.models.product import Product
from app.models.user import User


class TestInventoryTransactionModel:
    """Test cases for the InventoryTransaction model."""

    def test_inventory_transaction_creation(self, db_session):
        """Test creating an InventoryTransaction instance."""
        # Create a product
        product = Product(
            name="Test Product",
            sku="TEST-001",
            category="Electronics"
        )
        db_session.add(product)
        db_session.commit()

        # Create a user
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            role="admin"
        )
        db_session.add(user)
        db_session.commit()

        transaction = InventoryTransaction(
            product_id=product.id,
            change_amount=50,
            reason="Initial stock",
            performed_by=user.id
        )
        db_session.add(transaction)
        db_session.commit()

        assert transaction.id is not None
        assert transaction.product_id == product.id
        assert transaction.change_amount == 50
        assert transaction.reason == "Initial stock"
        assert transaction.performed_by == user.id
        assert transaction.created_at is not None

    def test_inventory_transaction_table_name(self):
        """Test that the InventoryTransaction model has correct table name."""
        assert InventoryTransaction.__tablename__ == "inventory_transactions"

    def test_inventory_transaction_columns(self):
        """Test that the InventoryTransaction model has all required columns."""
        columns = [column.name for column in InventoryTransaction.__table__.columns]
        expected_columns = ["id", "product_id", "change_amount", "reason", "performed_by", "created_at"]
        for column in expected_columns:
            assert column in columns

    def test_inventory_transaction_product_relationship(self, db_session):
        """Test the relationship between InventoryTransaction and Product."""
        # Create a product
        product = Product(
            name="Related Product",
            sku="REL-001",
            category="Test Category"
        )
        db_session.add(product)
        db_session.commit()

        # Create a transaction for the product
        transaction = InventoryTransaction(
            product_id=product.id,
            change_amount=-10,
            reason="Sales"
        )
        db_session.add(transaction)
        db_session.commit()

        # Test the relationship
        assert transaction.product is not None
        assert transaction.product.name == "Related Product"
        assert transaction.product.sku == "REL-001"

    def test_inventory_transaction_user_relationship(self, db_session):
        """Test the relationship between InventoryTransaction and User."""
        # Create a product
        product = Product(name="Product", sku="PROD-001", category="Test")
        db_session.add(product)
        db_session.commit()

        # Create a user
        user = User(
            email="user@example.com",
            password_hash="hashed_password",
            role="manager"
        )
        db_session.add(user)
        db_session.commit()

        # Create a transaction performed by the user
        transaction = InventoryTransaction(
            product_id=product.id,
            change_amount=25,
            reason="Restock",
            performed_by=user.id
        )
        db_session.add(transaction)
        db_session.commit()

        # Test the relationship
        assert transaction.user is not None
        assert transaction.user.email == "user@example.com"
        assert transaction.user.role == "manager"

    def test_inventory_transaction_without_user(self, db_session):
        """Test creating a transaction without associating a user."""
        # Create a product
        product = Product(name="Product", sku="PROD-002", category="Test")
        db_session.add(product)
        db_session.commit()

        # Create a transaction without a user (performed_by is nullable)
        transaction = InventoryTransaction(
            product_id=product.id,
            change_amount=15,
            reason="System adjustment"
        )
        db_session.add(transaction)
        db_session.commit()

        assert transaction.id is not None
        assert transaction.performed_by is None
        assert transaction.user is None
        assert transaction.reason == "System adjustment"

    def test_inventory_transaction_query(self, db_session):
        """Test querying inventory transactions from the database."""
        # Create a product
        product = Product(name="Query Product", sku="QUERY-001", category="Test")
        db_session.add(product)
        db_session.commit()

        # Create test transactions
        transaction1 = InventoryTransaction(
            product_id=product.id,
            change_amount=100,
            reason="Initial stock"
        )
        transaction2 = InventoryTransaction(
            product_id=product.id,
            change_amount=-20,
            reason="Sales"
        )
        
        db_session.add(transaction1)
        db_session.add(transaction2)
        db_session.commit()

        # Query all transactions
        transactions = db_session.query(InventoryTransaction).all()
        assert len(transactions) == 2

        # Query by reason
        transaction = db_session.query(InventoryTransaction).filter(
            InventoryTransaction.reason == "Initial stock"
        ).first()
        assert transaction is not None
        assert transaction.change_amount == 100
        assert transaction.reason == "Initial stock"

        # Query by change amount (positive vs negative)
        positive_transactions = db_session.query(InventoryTransaction).filter(
            InventoryTransaction.change_amount > 0
        ).all()
        assert len(positive_transactions) == 1
        assert positive_transactions[0].change_amount == 100

    def test_inventory_transaction_update(self, db_session):
        """Test updating an inventory transaction in the database."""
        # Create a product
        product = Product(name="Update Product", sku="UPD-001", category="Test")
        db_session.add(product)
        db_session.commit()

        transaction = InventoryTransaction(
            product_id=product.id,
            change_amount=30,
            reason="Original reason"
        )
        db_session.add(transaction)
        db_session.commit()

        # Update the transaction
        transaction.change_amount = 60
        transaction.reason = "Updated reason"
        db_session.commit()

        # Verify the update
        updated_transaction = db_session.query(InventoryTransaction).filter(
            InventoryTransaction.id == transaction.id
        ).first()
        assert updated_transaction.change_amount == 60
        assert updated_transaction.reason == "Updated reason"
        assert updated_transaction.product_id == product.id

    def test_inventory_transaction_delete(self, db_session):
        """Test deleting an inventory transaction from the database."""
        # Create a product
        product = Product(name="Delete Product", sku="DEL-001", category="Test")
        db_session.add(product)
        db_session.commit()

        transaction = InventoryTransaction(
            product_id=product.id,
            change_amount=15,
            reason="To delete"
        )
        db_session.add(transaction)
        db_session.commit()
        transaction_id = transaction.id

        # Delete the transaction
        db_session.delete(transaction)
        db_session.commit()

        # Verify the transaction is deleted
        deleted_transaction = db_session.query(InventoryTransaction).filter(
            InventoryTransaction.id == transaction_id
        ).first()
        assert deleted_transaction is None

    def test_inventory_transaction_multiple_for_product(self, db_session):
        """Test that a product can have multiple transactions."""
        # Create a product
        product = Product(name="Multi Transaction Product", sku="MULTI-001", category="Test")
        db_session.add(product)
        db_session.commit()

        # Create multiple transactions for the same product
        transactions = [
            InventoryTransaction(product_id=product.id, change_amount=100, reason="Initial stock"),
            InventoryTransaction(product_id=product.id, change_amount=-10, reason="Sale 1"),
            InventoryTransaction(product_id=product.id, change_amount=-5, reason="Sale 2"),
            InventoryTransaction(product_id=product.id, change_amount=20, reason="Restock"),
        ]
        
        db_session.add_all(transactions)
        db_session.commit()

        # Query transactions for this product
        product_transactions = db_session.query(InventoryTransaction).filter(
            InventoryTransaction.product_id == product.id
        ).all()
        assert len(product_transactions) == 4

        # Calculate net change
        net_change = sum(t.change_amount for t in product_transactions)
        assert net_change == 105  # 100 - 10 - 5 + 20

    def test_inventory_transaction_negative_change_amount(self, db_session):
        """Test that transactions can have negative change amounts."""
        # Create a product
        product = Product(name="Negative Test Product", sku="NEG-001", category="Test")
        db_session.add(product)
        db_session.commit()

        # Create a transaction with negative change (e.g., sale, damage, theft)
        transaction = InventoryTransaction(
            product_id=product.id,
            change_amount=-50,
            reason="Damaged goods removed"
        )
        db_session.add(transaction)
        db_session.commit()

        assert transaction.change_amount == -50
        assert transaction.reason == "Damaged goods removed"

    def test_inventory_transaction_zero_change_amount(self, db_session):
        """Test that transactions can have zero change amounts."""
        # Create a product
        product = Product(name="Zero Test Product", sku="ZERO-001", category="Test")
        db_session.add(product)
        db_session.commit()

        # Create a transaction with zero change (e.g., audit confirmation)
        transaction = InventoryTransaction(
            product_id=product.id,
            change_amount=0,
            reason="Audit confirmation - no change"
        )
        db_session.add(transaction)
        db_session.commit()

        assert transaction.change_amount == 0
        assert transaction.reason == "Audit confirmation - no change"