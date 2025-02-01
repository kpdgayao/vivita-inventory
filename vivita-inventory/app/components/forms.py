"""Form components for the inventory management system."""

from typing import Any, Dict, Optional, Callable
import streamlit as st

from ..utils.constants import (
    ITEM_FORM_FIELDS,
    TRANSACTION_FORM_FIELDS,
    TransactionType,
    CategoryType,
    UnitType
)
from ..utils.helpers import generate_sku, validate_quantity

class ItemForm:
    """Form for creating and editing inventory items."""
    
    def __init__(
        self,
        on_submit: Callable[[Dict[str, Any]], None],
        existing_item: Optional[Dict[str, Any]] = None
    ):
        """Initialize the form."""
        self.on_submit = on_submit
        self.existing_item = existing_item

    def render(self):
        """Render the item form."""
        with st.form("item_form"):
            form_data = {}
            
            # Basic Information
            st.subheader("Basic Information")
            col1, col2 = st.columns(2)
            
            with col1:
                form_data["name"] = st.text_input(
                    ITEM_FORM_FIELDS["name"]["label"],
                    value=self.existing_item.get("name", "") if self.existing_item else "",
                    help=ITEM_FORM_FIELDS["name"]["help"]
                )
                
                form_data["category"] = st.selectbox(
                    ITEM_FORM_FIELDS["category"]["label"],
                    options=[e.value for e in CategoryType],
                    index=[e.value for e in CategoryType].index(self.existing_item["category"])
                    if self.existing_item and "category" in self.existing_item
                    else 0,
                    help=ITEM_FORM_FIELDS["category"]["help"]
                )
            
            with col2:
                form_data["sku"] = st.text_input(
                    ITEM_FORM_FIELDS["sku"]["label"],
                    value=self.existing_item.get("sku", "") if self.existing_item else "",
                    help=ITEM_FORM_FIELDS["sku"]["help"],
                    disabled=bool(self.existing_item)
                )
                
                form_data["unit_type"] = st.selectbox(
                    ITEM_FORM_FIELDS["unit_type"]["label"],
                    options=[e.value for e in UnitType],
                    index=[e.value for e in UnitType].index(self.existing_item["unit_type"])
                    if self.existing_item and "unit_type" in self.existing_item
                    else 0,
                    help=ITEM_FORM_FIELDS["unit_type"]["help"]
                )
            
            # Description
            form_data["description"] = st.text_area(
                ITEM_FORM_FIELDS["description"]["label"],
                value=self.existing_item.get("description", "") if self.existing_item else "",
                help=ITEM_FORM_FIELDS["description"]["help"]
            )
            
            # Quantity Management
            st.subheader("Quantity Management")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                form_data["min_quantity"] = st.number_input(
                    ITEM_FORM_FIELDS["min_quantity"]["label"],
                    min_value=0,
                    value=int(self.existing_item.get("min_quantity", 0))
                    if self.existing_item else 0,
                    help=ITEM_FORM_FIELDS["min_quantity"]["help"]
                )
            
            with col2:
                form_data["max_quantity"] = st.number_input(
                    ITEM_FORM_FIELDS["max_quantity"]["label"],
                    min_value=0,
                    value=int(self.existing_item.get("max_quantity", 0))
                    if self.existing_item else 0,
                    help=ITEM_FORM_FIELDS["max_quantity"]["help"]
                )
            
            with col3:
                form_data["unit_cost"] = st.number_input(
                    ITEM_FORM_FIELDS["unit_cost"]["label"],
                    min_value=0.0,
                    value=float(self.existing_item.get("unit_cost", 0.0))
                    if self.existing_item else 0.0,
                    help=ITEM_FORM_FIELDS["unit_cost"]["help"]
                )
            
            submit_button = st.form_submit_button(
                "Update Item" if self.existing_item else "Create Item"
            )
            
            if submit_button:
                if not form_data["name"]:
                    st.error("Item name is required")
                    return
                
                if not self.existing_item and not form_data["sku"]:
                    form_data["sku"] = generate_sku(
                        form_data["category"],
                        form_data["name"]
                    )
                
                if not validate_quantity(
                    form_data.get("min_quantity", 0),
                    max_quantity=form_data.get("max_quantity")
                ):
                    st.error("Invalid quantity values")
                    return
                
                self.on_submit(form_data)

class TransactionForm:
    """Form for creating inventory transactions."""
    
    def __init__(
        self,
        on_submit: Callable[[Dict[str, Any]], None],
        item_id: str,
        current_quantity: int
    ):
        """Initialize the form."""
        self.on_submit = on_submit
        self.item_id = item_id
        self.current_quantity = current_quantity

    def render(self):
        """Render the transaction form."""
        with st.form("transaction_form"):
            form_data = {"item_id": self.item_id}
            
            # Transaction Type
            form_data["transaction_type"] = st.selectbox(
                TRANSACTION_FORM_FIELDS["transaction_type"]["label"],
                options=[e.value for e in TransactionType],
                help=TRANSACTION_FORM_FIELDS["transaction_type"]["help"]
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                form_data["quantity"] = st.number_input(
                    TRANSACTION_FORM_FIELDS["quantity"]["label"],
                    min_value=1,
                    help=TRANSACTION_FORM_FIELDS["quantity"]["help"]
                )
            
            with col2:
                form_data["unit_price"] = st.number_input(
                    TRANSACTION_FORM_FIELDS["unit_price"]["label"],
                    min_value=0.0,
                    help=TRANSACTION_FORM_FIELDS["unit_price"]["help"]
                )
            
            form_data["reference_number"] = st.text_input(
                TRANSACTION_FORM_FIELDS["reference_number"]["label"],
                help=TRANSACTION_FORM_FIELDS["reference_number"]["help"]
            )
            
            form_data["notes"] = st.text_area(
                TRANSACTION_FORM_FIELDS["notes"]["label"],
                help=TRANSACTION_FORM_FIELDS["notes"]["help"]
            )
            
            # Calculate and display total
            form_data["total_amount"] = form_data["quantity"] * form_data["unit_price"]
            st.info(f"Total Amount: ${form_data['total_amount']:.2f}")
            
            submit_button = st.form_submit_button("Create Transaction")
            
            if submit_button:
                # Validate quantity for outgoing transactions
                if form_data["transaction_type"] in [
                    TransactionType.SALE,
                    TransactionType.TRANSFER_OUT,
                    TransactionType.LOSS
                ]:
                    if form_data["quantity"] > self.current_quantity:
                        st.error("Insufficient quantity available")
                        return
                
                self.on_submit(form_data)
