"""Tests for Inventory Transaction service."""

import pytest
from typing import List
from app.services.inventory_transaction_service import (
    create_transaction,
    get_transaction,
    get_transaction_with_details,
    get_transactions,
    get_transactions_by_product,
    get_transactions_by_user,
    get_transactions_by_reason,
    update_transaction,
    delete_transaction,
    get_product_transaction_summary
)
from app.models.inventory_transaction import InventoryTransaction
from app.models.product import Product
from app.models.user import User
from app.schemas.inventory_transaction import InventoryTransactionCreate, InventoryTransactionUpdate


class TestInventoryTransactionService:
    """Test cases for the Inventory Transaction service."""

    @pytest.fixture
    def sample_product(self, db_session):
        """Create a sample product for testing."""
        product = Product(name="Test Product", sku="TEST-001", category="Test Category")
        db_session.add(product)
        db_session.commit()
        return product

    @pytest.fixture
    def sample_user(self, db_session):
        """Create a sample user for testing."""
        user = User(email="test@example.com", password_hash="hashed_password", role="user")
        db_session.add(user)
        db_session.commit()
        return user

    @pytest.fixture
    def sample_transactions(self, db_session, sample_product, sample_user):
        """Create sample transactions for testing."""
        transactions = [
            InventoryTransaction(
                product_id=sample_product.id,
                change_amount=10,
                reason="Initial stock",
                performed_by=sample_user.id
            ),
            InventoryTransaction(
                product_id=sample_product.id,
                change_amount=-3,
                reason="Sale",
                performed_by=sample_user.id
            ),
            InventoryTransaction(
                product_id=sample_product.id,
                change_amount=5,
                reason="Restock",
                performed_by=sample_user.id
            )
        ]
        
        for transaction in transactions:
            db_session.add(transaction)
        db_session.commit()
        
        return transactions

    def test_create_transaction(self, db_session, sample_product, sample_user):
        """Test creating a transaction through service."""
        transaction_data = InventoryTransactionCreate(
            product_id=sample_product.id,
            change_amount=10,
            reason="Test creation",
            performed_by=sample_user.id
        )
        
        created_transaction = create_transaction(db_session, transaction_data)
        
        assert created_transaction.id is not None
        assert created_transaction.product_id == sample_product.id
        assert created_transaction.change_amount == 10
        assert created_transaction.reason == "Test creation"
        assert created_transaction.performed_by == sample_user.id
        assert created_transaction.created_at is not None

    def test_create_transaction_minimal_data(self, db_session, sample_product):
        """Test creating a transaction with minimal required data."""
        transaction_data = InventoryTransactionCreate(
            product_id=sample_product.id,
            change_amount=-5
        )
        
        created_transaction = create_transaction(db_session, transaction_data)
        
        assert created_transaction.id is not None
        assert created_transaction.product_id == sample_product.id
        assert created_transaction.change_amount == -5
        assert created_transaction.reason is None
        assert created_transaction.performed_by is None

    def test_get_transaction_existing(self, db_session, sample_transactions):
        """Test getting an existing transaction."""
        transaction = sample_transactions[0]
        
        retrieved_transaction = get_transaction(db_session, transaction.id)
        
        assert retrieved_transaction is not None
        assert retrieved_transaction.id == transaction.id
        assert retrieved_transaction.product_id == transaction.product_id
        assert retrieved_transaction.change_amount == transaction.change_amount

    def test_get_transaction_nonexistent(self, db_session):
        """Test getting a non-existent transaction."""
        retrieved_transaction = get_transaction(db_session, 999)
        
        assert retrieved_transaction is None

    def test_get_transaction_with_details(self, db_session, sample_transactions):
        """Test getting a transaction with related product and user details."""
        transaction = sample_transactions[0]
        
        retrieved_transaction = get_transaction_with_details(db_session, transaction.id)
        
        assert retrieved_transaction is not None
        assert retrieved_transaction.id == transaction.id
        assert retrieved_transaction.product is not None
        assert retrieved_transaction.product.name == "Test Product"
        assert retrieved_transaction.user is not None
        assert retrieved_transaction.user.email == "test@example.com"

    def test_get_transactions_pagination(self, db_session, sample_transactions):
        """Test getting transactions with pagination."""
        # Test default pagination
        transactions = get_transactions(db_session)
        assert len(transactions) == 3
        assert isinstance(transactions, list)
        
        # Test with limit
        transactions = get_transactions(db_session, limit=2)
        assert len(transactions) == 2
        
        # Test with skip
        transactions = get_transactions(db_session, skip=1, limit=2)
        assert len(transactions) == 2

    def test_get_transactions_ordering(self, db_session, sample_transactions):
        """Test that transactions are ordered by most recent first."""
        transactions = get_transactions(db_session)
        
        # Should be ordered by created_at desc
        assert len(transactions) == 3
        for i in range(len(transactions) - 1):
            assert transactions[i].created_at >= transactions[i + 1].created_at

    def test_get_transactions_by_product(self, db_session, sample_transactions, sample_product):
        """Test getting transactions filtered by product."""
        # Create another product with transactions
        other_product = Product(name="Other Product", sku="OTHER-001", category="Other")
        db_session.add(other_product)
        db_session.commit()
        
        other_transaction = InventoryTransaction(
            product_id=other_product.id,
            change_amount=20,
            reason="Other product transaction"
        )
        db_session.add(other_transaction)
        db_session.commit()
        
        # Get transactions for the sample product
        transactions = get_transactions_by_product(db_session, sample_product.id)
        
        assert len(transactions) == 3
        for transaction in transactions:
            assert transaction.product_id == sample_product.id

    def test_get_transactions_by_user(self, db_session, sample_transactions, sample_user):
        """Test getting transactions filtered by user."""
        # Create another user with transactions
        other_user = User(email="other@example.com", password_hash="hashed", role="user")
        db_session.add(other_user)
        db_session.commit()
        
        other_transaction = InventoryTransaction(
            product_id=sample_transactions[0].product_id,
            change_amount=15,
            reason="Other user transaction",
            performed_by=other_user.id
        )
        db_session.add(other_transaction)
        db_session.commit()
        
        # Get transactions for the sample user
        transactions = get_transactions_by_user(db_session, sample_user.id)
        
        assert len(transactions) == 3
        for transaction in transactions:
            assert transaction.performed_by == sample_user.id

    def test_get_transactions_by_reason(self, db_session, sample_transactions):
        """Test getting transactions filtered by reason (partial match)."""
        # Test partial match
        transactions = get_transactions_by_reason(db_session, "stock")
        assert len(transactions) == 2  # "Initial stock" and "Restock"
        
        # Test case insensitive
        transactions = get_transactions_by_reason(db_session, "SALE")
        assert len(transactions) == 1
        assert transactions[0].reason == "Sale"
        
        # Test no matches
        transactions = get_transactions_by_reason(db_session, "nonexistent")
        assert len(transactions) == 0

    def test_update_transaction_allowed_fields(self, db_session, sample_transactions):
        """Test updating a transaction with allowed fields."""
        transaction = sample_transactions[0]
        original_change_amount = transaction.change_amount
        
        update_data = InventoryTransactionUpdate(
            reason="Updated reason",
            performed_by=999,
            change_amount=100  # This should not be updated
        )
        
        updated_transaction = update_transaction(db_session, transaction.id, update_data)
        
        assert updated_transaction is not None
        assert updated_transaction.reason == "Updated reason"
        assert updated_transaction.performed_by == 999
        # change_amount should remain unchanged
        assert updated_transaction.change_amount == original_change_amount

    def test_update_transaction_partial_update(self, db_session, sample_transactions):
        """Test partially updating a transaction."""
        transaction = sample_transactions[0]
        original_reason = transaction.reason
        
        update_data = InventoryTransactionUpdate(performed_by=888)
        
        updated_transaction = update_transaction(db_session, transaction.id, update_data)
        
        assert updated_transaction is not None
        assert updated_transaction.performed_by == 888
        assert updated_transaction.reason == original_reason  # Should remain unchanged

    def test_update_transaction_nonexistent(self, db_session):
        """Test updating a non-existent transaction."""
        update_data = InventoryTransactionUpdate(reason="New reason")
        
        updated_transaction = update_transaction(db_session, 999, update_data)
        
        assert updated_transaction is None

    def test_delete_transaction_existing(self, db_session, sample_transactions):
        """Test deleting an existing transaction."""
        transaction = sample_transactions[0]
        transaction_id = transaction.id
        
        result = delete_transaction(db_session, transaction_id)
        
        assert result is True
        
        # Verify transaction is deleted
        deleted_transaction = get_transaction(db_session, transaction_id)
        assert deleted_transaction is None

    def test_delete_transaction_nonexistent(self, db_session):
        """Test deleting a non-existent transaction."""
        result = delete_transaction(db_session, 999)
        
        assert result is False

    def test_get_product_transaction_summary_with_transactions(self, db_session, sample_transactions, sample_product):
        """Test getting transaction summary for a product with transactions."""
        # sample_transactions: +10, -3, +5 = net +12
        summary = get_product_transaction_summary(db_session, sample_product.id)
        
        assert summary["product_id"] == sample_product.id
        assert summary["total_in"] == 15  # 10 + 5
        assert summary["total_out"] == 3   # abs(-3)
        assert summary["net_change"] == 12  # 15 - 3
        assert summary["transaction_count"] == 3

    def test_get_product_transaction_summary_no_transactions(self, db_session, sample_product):
        """Test getting transaction summary for a product with no transactions."""
        summary = get_product_transaction_summary(db_session, sample_product.id)
        
        assert summary["product_id"] == sample_product.id
        assert summary["total_in"] == 0
        assert summary["total_out"] == 0
        assert summary["net_change"] == 0
        assert summary["transaction_count"] == 0

    def test_get_product_transaction_summary_only_positive_changes(self, db_session, sample_product):
        """Test transaction summary with only positive changes."""
        transactions = [
            InventoryTransaction(product_id=sample_product.id, change_amount=10, reason="Stock 1"),
            InventoryTransaction(product_id=sample_product.id, change_amount=20, reason="Stock 2"),
        ]
        
        for transaction in transactions:
            db_session.add(transaction)
        db_session.commit()
        
        summary = get_product_transaction_summary(db_session, sample_product.id)
        
        assert summary["total_in"] == 30
        assert summary["total_out"] == 0
        assert summary["net_change"] == 30
        assert summary["transaction_count"] == 2

    def test_get_product_transaction_summary_only_negative_changes(self, db_session, sample_product):
        """Test transaction summary with only negative changes."""
        transactions = [
            InventoryTransaction(product_id=sample_product.id, change_amount=-5, reason="Sale 1"),
            InventoryTransaction(product_id=sample_product.id, change_amount=-7, reason="Sale 2"),
        ]
        
        for transaction in transactions:
            db_session.add(transaction)
        db_session.commit()
        
        summary = get_product_transaction_summary(db_session, sample_product.id)
        
        assert summary["total_in"] == 0
        assert summary["total_out"] == 12  # 5 + 7
        assert summary["net_change"] == -12
        assert summary["transaction_count"] == 2

    def test_transactions_pagination_edge_cases(self, db_session):
        """Test pagination edge cases."""
        # Test empty results
        transactions = get_transactions(db_session)
        assert len(transactions) == 0
        
        # Test with skip greater than available records
        transactions = get_transactions(db_session, skip=100)
        assert len(transactions) == 0