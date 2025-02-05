"""Integration tests for the inventory system."""

import unittest
import os
from dotenv import load_dotenv
from app.database.supabase_manager import SupabaseManager

class TestInventoryIntegration(unittest.TestCase):
    """Integration tests for the inventory system."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures that are reused across all tests."""
        load_dotenv()
        if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
            raise ValueError("Supabase credentials not found in environment variables")
            
        cls.db_manager = SupabaseManager()
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_item = {
            "name": "Integration Test Item",
            "category": "finished_goods",
            "unit_type": "piece",
            "quantity": 10,
            "unit_cost": 5.00,
            "min_quantity": 2,
            "description": "Test item for integration tests"
        }
    
    def test_full_item_lifecycle(self):
        """Test the complete lifecycle of an item: create, read, update, delete."""
        # Create item
        created_item = self.db_manager.create_item(self.test_item)
        self.assertIsNotNone(created_item, "Failed to create item")
        self.assertEqual(created_item["name"], self.test_item["name"])
        
        # Store the item ID
        item_id = created_item["id"]
        
        # Read item
        retrieved_item = self.db_manager.get_item(item_id)
        self.assertIsNotNone(retrieved_item, "Failed to retrieve item")
        self.assertEqual(retrieved_item["name"], self.test_item["name"])
        
        # Update item
        update_data = {"quantity": 20}
        updated_item = self.db_manager.update_item(item_id, update_data)
        self.assertIsNotNone(updated_item, "Failed to update item")
        self.assertEqual(updated_item["quantity"], 20)
        
        # Delete item
        delete_success = self.db_manager.delete_item(item_id)
        self.assertTrue(delete_success, "Failed to delete item")
        
        # Verify deletion
        deleted_item = self.db_manager.get_item(item_id)
        self.assertIsNone(deleted_item, "Item still exists after deletion")
    
    def test_get_items_with_filters(self):
        """Test retrieving items with filters."""
        # Create test item
        created_item = self.db_manager.create_item(self.test_item)
        self.assertIsNotNone(created_item)
        
        try:
            # Test filtering
            filters = {"category": "finished_goods"}
            items = self.db_manager.get_items(filters)
            self.assertIsInstance(items, list)
            self.assertTrue(any(item["name"] == self.test_item["name"] for item in items))
            
            # Test filtering with non-existent category
            filters = {"category": "non_existent"}
            items = self.db_manager.get_items(filters)
            self.assertEqual(len(items), 0)
            
        finally:
            # Cleanup
            if created_item:
                self.db_manager.delete_item(created_item["id"])
    
    def test_low_stock_alerts(self):
        """Test low stock alert functionality."""
        # Create item with quantity at minimum
        low_stock_item = dict(self.test_item)
        low_stock_item["quantity"] = low_stock_item["min_quantity"]
        created_item = self.db_manager.create_item(low_stock_item)
        self.assertIsNotNone(created_item)
        
        try:
            # Get low stock items
            low_stock_items = self.db_manager.get_low_stock_items()
            self.assertTrue(any(item["id"] == created_item["id"] for item in low_stock_items))
            
        finally:
            # Cleanup
            if created_item:
                self.db_manager.delete_item(created_item["id"])

if __name__ == '__main__':
    unittest.main()
