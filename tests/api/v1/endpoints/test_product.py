"""Tests for Product API endpoints."""
from app.models.product import Product


class TestProductEndpoints:
    """Test cases for Product API endpoints."""

    def test_create_product_success(self, client, sample_product_data):
        """Test successful product creation."""
        response = client.post("/api/v1/products/", json=sample_product_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_product_data["name"]
        assert data["sku"] == sample_product_data["sku"]
        assert data["category"] == sample_product_data["category"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_product_invalid_data(self, client):
        """Test product creation with invalid data."""
        # Missing required fields
        invalid_data = {"name": "Test Product"}
        response = client.post("/api/v1/products/", json=invalid_data)
        assert response.status_code == 422

        # Invalid data types - missing required sku field
        invalid_data = {"name": "Test", "category": "Test"}
        response = client.post("/api/v1/products/", json=invalid_data)
        assert response.status_code == 422

    def test_get_products_empty(self, client):
        """Test getting products from empty database."""
        response = client.get("/api/v1/products/")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_products_with_data(self, client, db_session, sample_products_data):
        """Test getting products with data."""
        # Add sample products to database
        for product_data in sample_products_data:
            product = Product(**product_data)
            db_session.add(product)
        db_session.commit()

        response = client.get("/api/v1/products/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4

    def test_get_products_pagination(self, client, db_session, sample_products_data):
        """Test products pagination."""
        # Add sample products
        for product_data in sample_products_data:
            product = Product(**product_data)
            db_session.add(product)
        db_session.commit()

        # Test pagination
        response = client.get("/api/v1/products/?skip=0&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

        response = client.get("/api/v1/products/?skip=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_products_search_by_name(self, client, db_session, sample_products_data):
        """Test searching products by name."""
        # Add sample products
        for product_data in sample_products_data:
            product = Product(**product_data)
            db_session.add(product)
        db_session.commit()

        response = client.get("/api/v1/products/?name=Laptop")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Laptop"

    def test_get_products_search_by_category(self, client, db_session, sample_products_data):
        """Test searching products by category."""
        # Add sample products
        for product_data in sample_products_data:
            product = Product(**product_data)
            db_session.add(product)
        db_session.commit()

        response = client.get("/api/v1/products/?category=Electronics")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        electronics_names = [item["name"] for item in data]
        assert "Laptop" in electronics_names
        assert "Phone" in electronics_names

    def test_get_product_by_id_success(self, client, db_session, sample_product_data):
        """Test getting a product by ID successfully."""
        # Create a product
        product = Product(**sample_product_data)
        db_session.add(product)
        db_session.commit()
        product_id = product.id

        response = client.get(f"/api/v1/products/{product_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == product_id
        assert data["name"] == sample_product_data["name"]

    def test_get_product_by_id_not_found(self, client):
        """Test getting a non-existent product."""
        response = client.get("/api/v1/products/999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Product not found"

    def test_update_product_success(self, client, db_session, sample_product_data):
        """Test successful product update."""
        # Create a product
        product = Product(**sample_product_data)
        db_session.add(product)
        db_session.commit()
        product_id = product.id

        # Update the product
        update_data = {"name": "Updated Product", "sku": "UPD-200"}
        response = client.put(f"/api/v1/products/{product_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Product"
        assert data["sku"] == "UPD-200"
        assert data["category"] == sample_product_data["category"]  # Should remain unchanged

    def test_update_product_partial(self, client, db_session, sample_product_data):
        """Test partial product update."""
        # Create a product
        product = Product(**sample_product_data)
        db_session.add(product)
        db_session.commit()
        product_id = product.id

        # Update only sku
        update_data = {"sku": "UPD-300"}
        response = client.put(f"/api/v1/products/{product_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_product_data["name"]  # Should remain unchanged
        assert data["sku"] == "UPD-300"
        assert data["category"] == sample_product_data["category"]  # Should remain unchanged

    def test_update_product_not_found(self, client):
        """Test updating a non-existent product."""
        update_data = {"name": "Should Not Work"}
        response = client.put("/api/v1/products/999", json=update_data)
        assert response.status_code == 404
        assert response.json()["detail"] == "Product not found"

    def test_delete_product_success(self, client, db_session, sample_product_data):
        """Test successful product deletion."""
        # Create a product
        product = Product(**sample_product_data)
        db_session.add(product)
        db_session.commit()
        product_id = product.id

        # Delete the product
        response = client.delete(f"/api/v1/products/{product_id}")
        assert response.status_code == 200
        assert response.json()["message"] == "Product deleted successfully"

        # Verify it's deleted
        get_response = client.get(f"/api/v1/products/{product_id}")
        assert get_response.status_code == 404

    def test_delete_product_not_found(self, client):
        """Test deleting a non-existent product."""
        response = client.delete("/api/v1/products/999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Product not found"

    def test_pagination_invalid_params(self, client):
        """Test pagination with invalid parameters."""
        # Negative skip
        response = client.get("/api/v1/products/?skip=-1")
        assert response.status_code == 422

        # Limit too high
        response = client.get("/api/v1/products/?limit=2000")
        assert response.status_code == 422

        # Limit too low
        response = client.get("/api/v1/products/?limit=0")
        assert response.status_code == 422

    def test_complete_product_lifecycle(self, client):
        """Test complete product lifecycle: create, read, update, delete."""
        # Create
        create_data = {"name": "Lifecycle Product", "sku": "LIFECYCLE-001", "category": "Test"}
        create_response = client.post("/api/v1/products/", json=create_data)
        assert create_response.status_code == 200
        product_id = create_response.json()["id"]

        # Read
        get_response = client.get(f"/api/v1/products/{product_id}")
        assert get_response.status_code == 200
        assert get_response.json()["name"] == "Lifecycle Product"

        # Update
        update_data = {"name": "Updated Lifecycle Product", "sku": "LIFECYCLE-UPD"}
        update_response = client.put(f"/api/v1/products/{product_id}", json=update_data)
        assert update_response.status_code == 200
        assert update_response.json()["name"] == "Updated Lifecycle Product"
        assert update_response.json()["sku"] == "LIFECYCLE-UPD"

        # Delete
        delete_response = client.delete(f"/api/v1/products/{product_id}")
        assert delete_response.status_code == 200

        # Verify deletion
        final_get_response = client.get(f"/api/v1/products/{product_id}")
        assert final_get_response.status_code == 404