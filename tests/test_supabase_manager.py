"""Tests for SupabaseManager class."""

import unittest
from unittest.mock import Mock, patch
import os
from dotenv import load_dotenv
from app.database.supabase_manager import SupabaseManager

class TestSupabaseManager(unittest.TestCase):
    """Test cases for SupabaseManager."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures that are reused across all tests."""
        load_dotenv()
        if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
            raise ValueError("Supabase credentials not found in environment variables")
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock Supabase client
        self.mock_client = Mock()
        
        # Mock the create_client function
        with patch('app.database.supabase_manager.create_client') as mock_create_client:
            mock_create_client.return_value = self.mock_client
            self.manager = SupabaseManager()
    
    def test_create_item_valid_data(self):
        """Test creating an item with valid data."""
        # Setup
        test_item = {
            "name": "Test Item",
            "category": "finished_goods",
            "unit_type": "piece",
            "quantity": 10,
            "unit_cost": 5.00,
            "min_quantity": 2
        }
        
        # Mock the insert response
        mock_response = Mock()
        mock_response.data = [{"id": "123", **test_item}]
        self.mock_client.table().insert().execute.return_value = mock_response
        
        # Execute
        result = self.manager.create_item(test_item)
        
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], test_item["name"])
        self.mock_client.table.assert_called_with("items")
        
        # Verify the insert was called with the correct data
        insert_args = self.mock_client.table().insert.call_args.args[0]
        self.assertEqual(insert_args["name"], test_item["name"])
        self.assertEqual(insert_args["category"], test_item["category"])
        self.assertEqual(insert_args["unit_type"], test_item["unit_type"])
        self.assertEqual(insert_args["quantity"], test_item["quantity"])
        self.assertEqual(insert_args["unit_cost"], test_item["unit_cost"])
        self.assertEqual(insert_args["min_quantity"], test_item["min_quantity"])
    
    def test_create_item_missing_fields(self):
        """Test creating an item with missing required fields."""
        # Setup
        test_item = {
            "name": "Test Item",
            # Missing required fields
        }
        
        # Execute and Assert
        with self.assertRaises(ValueError):
            self.manager.create_item(test_item)
    
    def test_create_item_invalid_numeric(self):
        """Test creating an item with invalid numeric values."""
        # Setup
        test_item = {
            "name": "Test Item",
            "category": "finished_goods",
            "unit_type": "piece",
            "quantity": "invalid",  # Should be int
            "unit_cost": 5.00,
            "min_quantity": 2
        }
        
        # Execute and Assert
        with self.assertRaises(ValueError):
            self.manager.create_item(test_item)
    
    def test_get_items(self):
        """Test retrieving items with filters."""
        # Setup
        mock_response = Mock()
        mock_response.data = [{"id": "123", "name": "Test Item"}]
        self.mock_client.table().select().execute.return_value = mock_response
        
        # Execute
        result = self.manager.get_items()
        
        # Assert
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Test Item")
        self.mock_client.table.assert_called_with("items")

if __name__ == '__main__':
    unittest.main()
