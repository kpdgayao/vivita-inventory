"""Tests for form components."""

import unittest
from unittest.mock import Mock, patch
import streamlit as st
from app.components.forms import ItemForm
from app.utils.constants import CategoryType, UnitType

class TestItemForm(unittest.TestCase):
    """Test cases for ItemForm."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_on_submit = Mock()
        self.form = ItemForm(self.mock_on_submit)
    
    @patch('streamlit.form')
    @patch('streamlit.text_input')
    @patch('streamlit.text_area')
    @patch('streamlit.selectbox')
    @patch('streamlit.number_input')
    @patch('streamlit.form_submit_button')
    def test_form_submission_valid(self, mock_submit, mock_number, mock_select, mock_area, mock_text, mock_form):
        """Test form submission with valid data."""
        # Setup form values
        mock_text.side_effect = ["Test Item", "TEST123"]  # name, sku
        mock_area.return_value = "Test Description"  # description
        mock_select.side_effect = ["finished_goods", "piece"]  # category, unit_type
        mock_number.side_effect = [10, 2, 5.00, 20]  # quantity, min_quantity, unit_cost, max_quantity
        mock_submit.return_value = True
        
        # Mock form context manager
        mock_form.return_value.__enter__.return_value = None
        mock_form.return_value.__exit__.return_value = None
        
        # Expected form data
        expected_data = {
            "name": "Test Item",
            "sku": "TEST123",
            "description": "Test Description",
            "category": "finished_goods",
            "unit_type": "piece",
            "quantity": 10,
            "min_quantity": 2,
            "unit_cost": 5.00,
            "max_quantity": 20
        }
        
        # Execute
        self.form.render()
        
        # Assert
        self.mock_on_submit.assert_called_once()
        actual_data = self.mock_on_submit.call_args[0][0]
        for key, value in expected_data.items():
            self.assertEqual(actual_data[key], value, f"Mismatch in {key}")
    
    @patch('streamlit.form')
    @patch('streamlit.text_input')
    @patch('streamlit.text_area')
    @patch('streamlit.selectbox')
    @patch('streamlit.number_input')
    @patch('streamlit.form_submit_button')
    def test_form_submission_missing_name(self, mock_submit, mock_number, mock_select, mock_area, mock_text, mock_form):
        """Test form submission with missing name."""
        # Setup form values
        mock_text.side_effect = ["", "TEST123"]  # Empty name
        mock_area.return_value = "Test Description"  # description
        mock_select.side_effect = ["finished_goods", "piece"]
        mock_number.side_effect = [10, 2, 5.00, 20]  # quantity, min_quantity, unit_cost, max_quantity
        mock_submit.return_value = True
        
        # Mock form context manager
        mock_form.return_value.__enter__.return_value = None
        mock_form.return_value.__exit__.return_value = None
        
        # Execute
        self.form.render()
        
        # Assert
        self.mock_on_submit.assert_not_called()
    
    @patch('streamlit.form')
    @patch('streamlit.text_input')
    @patch('streamlit.text_area')
    @patch('streamlit.selectbox')
    @patch('streamlit.number_input')
    @patch('streamlit.form_submit_button')
    def test_form_submission_invalid_quantity(self, mock_submit, mock_number, mock_select, mock_area, mock_text, mock_form):
        """Test form submission with invalid quantity values."""
        # Setup form values
        mock_text.side_effect = ["Test Item", "TEST123"]  # name, sku
        mock_area.return_value = "Test Description"  # description
        mock_select.side_effect = ["finished_goods", "piece"]
        mock_number.side_effect = [1, 2, 5.00, 20]  # quantity < min_quantity
        mock_submit.return_value = True
        
        # Mock form context manager
        mock_form.return_value.__enter__.return_value = None
        mock_form.return_value.__exit__.return_value = None
        
        # Execute
        self.form.render()
        
        # Assert
        self.mock_on_submit.assert_not_called()

if __name__ == '__main__':
    unittest.main()
