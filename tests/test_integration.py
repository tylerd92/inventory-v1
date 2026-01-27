"""Integration tests for the API."""

import pytest
from fastapi.testclient import TestClient


class TestIntegration:
    """Integration tests for the inventory API."""

    @pytest.mark.integration
    def test_full_product_workflow(self, client):
        """Test a complete product management workflow."""
        # Step 1: Create multiple products
        products_to_create = [
            {"name": "Integration Laptop", "sku": "INT-LAP-001", "category": "Electronics"},
            {"name": "Integration Chair", "sku": "INT-CHR-001", "category": "Furniture"},
            {"name": "Integration Phone", "sku": "INT-PHN-001", "category": "Electronics"},
        ]

        created_products = []
        for product_data in products_to_create:
            response = client.post("/api/v1/products/", json=product_data)
            assert response.status_code == 200
            created_products.append(response.json())

        # Step 2: Verify all products were created
        response = client.get("/api/v1/products/")
        assert response.status_code == 200
        all_products = response.json()
        assert len(all_products) == 3

        # Step 3: Search for electronics
        response = client.get("/api/v1/products/?category=Electronics")
        assert response.status_code == 200
        electronics = response.json()
        assert len(electronics) == 2

        # Step 4: Update a product
        laptop = next(p for p in created_products if p["name"] == "Integration Laptop")
        laptop_id = laptop["id"]
        update_data = {"sku": "INT-LAP-UPD"}
        response = client.put(f"/api/v1/products/{laptop_id}", json=update_data)
        assert response.status_code == 200
        updated_laptop = response.json()
        assert updated_laptop["sku"] == "INT-LAP-UPD"

        # Step 5: Delete a product
        chair = next(p for p in created_products if p["name"] == "Integration Chair")
        response = client.delete(f"/api/v1/products/{chair['id']}")
        assert response.status_code == 200

        # Step 6: Verify deletion
        response = client.get("/api/v1/products/")
        assert response.status_code == 200
        remaining_products = response.json()
        assert len(remaining_products) == 2
        
        # Ensure the chair is not in the remaining products
        remaining_names = [p["name"] for p in remaining_products]
        assert "Integration Chair" not in remaining_names

    @pytest.mark.integration
    def test_search_and_pagination_workflow(self, client):
        """Test search and pagination functionality together."""
        # Create many test products
        for i in range(15):
            category = "Electronics" if i % 2 == 0 else "Furniture"
            product_data = {
                "name": f"Test Product {i:02d}",
                "sku": f"TST-{i:03d}",
                "category": category
            }
            response = client.post("/api/v1/products/", json=product_data)
            assert response.status_code == 200

        # Test pagination on all products
        response = client.get("/api/v1/products/?limit=10")
        assert response.status_code == 200
        page1 = response.json()
        assert len(page1) == 10

        response = client.get("/api/v1/products/?skip=10&limit=10")
        assert response.status_code == 200
        page2 = response.json()
        assert len(page2) == 5

        # Test pagination on search results
        response = client.get("/api/v1/products/?category=Electronics&limit=5")
        assert response.status_code == 200
        electronics_page1 = response.json()
        assert len(electronics_page1) == 5
        assert all(p["category"] == "Electronics" for p in electronics_page1)

        response = client.get("/api/v1/products/?category=Electronics&skip=5&limit=5")
        assert response.status_code == 200
        electronics_page2 = response.json()
        assert len(electronics_page2) == 3  # 8 total electronics - 5 from first page
        assert all(p["category"] == "Electronics" for p in electronics_page2)

    @pytest.mark.integration
    def test_error_handling_workflow(self, client):
        """Test error handling across different operations."""
        # Test creating product with invalid data
        response = client.post("/api/v1/products/", json={"name": "Invalid"})
        assert response.status_code == 422

        # Test getting non-existent product
        response = client.get("/api/v1/products/999")
        assert response.status_code == 404

        # Test updating non-existent product
        response = client.put("/api/v1/products/999", json={"name": "Updated"})
        assert response.status_code == 404

        # Test deleting non-existent product
        response = client.delete("/api/v1/products/999")
        assert response.status_code == 404

        # Test invalid pagination parameters
        response = client.get("/api/v1/products/?skip=-1")
        assert response.status_code == 422

        response = client.get("/api/v1/products/?limit=2000")
        assert response.status_code == 422