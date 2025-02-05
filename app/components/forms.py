"""Form components for the inventory management system."""

from typing import Any, Dict, Optional, Callable
import streamlit as st

from ..utils.constants import (
    ITEM_FORM_FIELDS,
    TRANSACTION_FORM_FIELDS,
    TransactionType,
    CategoryType,
    UnitType,
    SUPPLIER_FORM_FIELDS
)
from ..utils.helpers import (
    generate_sku,
    validate_quantity,
    format_currency
)

# Form field definitions for suppliers
SUPPLIER_FORM_FIELDS = {
    "name": {
        "help": "The name of the supplier company or business"
    },
    "contact_email": {
        "help": "Primary contact email for the supplier"
    },
    "phone": {
        "help": "Contact phone number for the supplier"
    },
    "address": {
        "help": "Physical or mailing address of the supplier"
    },
    "remarks": {
        "help": "Any additional notes or information about the supplier"
    }
}

class ItemForm:
    """Form for creating and editing inventory items."""
    
    def __init__(
        self,
        on_submit: Callable[[Dict[str, Any]], None],
        existing_item: Optional[Dict[str, Any]] = None
    ):
        """Initialize the ItemForm.
        
        Args:
            on_submit: Callback function to handle form submission
            existing_item: Optional dictionary containing existing item data for editing
        """
        self.on_submit = on_submit
        self.existing_item = existing_item

    def render(self):
        """Render the item form."""
        # Use a unique form key based on whether we're editing or adding
        form_key = f"edit_item_{self.existing_item['id']}" if self.existing_item else "add_item_form"
        
        with st.form(form_key):
            # Left and right columns for better organization
            left_col, right_col = st.columns([3, 2])
            
            with left_col:
                # Essential fields group
                st.subheader("Essential Information")
                
                # Quick category selection with icons
                category_icons = {
                    "raw_materials": "🥩",
                    "finished_goods": "🍱",
                    "packaging": "📦",
                    "supplies": "🧰",
                    "equipment": "⚙️",
                    "spare_parts": "🔧",
                    "consumables": "🧪",
                    "other": "📎"
                }
                
                category = st.selectbox(
                    "Category",
                    options=[e.value for e in CategoryType],
                    format_func=lambda x: f"{category_icons.get(x, '•')} {x.replace('_', ' ').title()}",
                    help=ITEM_FORM_FIELDS["category"]["help"]
                )
                
                # Name with auto-complete from existing items
                existing_items = st.session_state.db_manager.get_items()
                existing_names = [item["name"] for item in existing_items]
                name = st.text_input(
                    "Item Name",
                    value=self.existing_item.get("name", "") if self.existing_item else "",
                    help="Start typing to see similar items"
                ).strip()
                
                if name and not self.existing_item:
                    similar_items = [n for n in existing_names if name.lower() in n.lower()]
                    if similar_items:
                        st.info(f"📝 Similar items: {', '.join(similar_items)}")
                
                # Quantity fields in a single row
                q_col1, q_col2, q_col3 = st.columns(3)
                
                with q_col1:
                    min_quantity = st.number_input(
                        "Min Qty",
                        value=int(self.existing_item["min_quantity"]) if self.existing_item and "min_quantity" in self.existing_item else 0,
                        min_value=0,
                        help=ITEM_FORM_FIELDS["min_quantity"]["help"]
                    )
                
                with q_col2:
                    max_quantity = st.number_input(
                        "Max Qty",
                        value=int(self.existing_item["max_quantity"]) if self.existing_item and "max_quantity" in self.existing_item else 0,
                        min_value=0,
                        help=ITEM_FORM_FIELDS["max_quantity"]["help"]
                    )
                
                with q_col3:
                    initial_qty = st.number_input(
                        "Initial Qty",
                        value=int(self.existing_item["quantity"]) if self.existing_item and "quantity" in self.existing_item else 0,
                        min_value=0,
                        help="Initial stock quantity",
                        step=1
                    )
            
            with right_col:
                # Additional details group
                st.subheader("Additional Details")
                
                # Unit type with icons
                unit_icons = {
                    "piece": "🔢",
                    "kg": "⚖️",
                    "gram": "⚖️",
                    "liter": "🧪",
                    "meter": "📏",
                    "box": "📦",
                    "pack": "🎁",
                    "set": "🎯",
                    "pair": "👥",
                    "unit": "📍"
                }
                
                unit_type = st.selectbox(
                    "Unit Type",
                    options=[e.value for e in UnitType],
                    format_func=lambda x: f"{unit_icons.get(x, '•')} {x.title()}",
                    help=ITEM_FORM_FIELDS["unit_type"]["help"]
                )
                
                # Cost with peso symbol
                st.markdown("**Unit Cost** (₱)")
                unit_cost = st.number_input(
                    "Unit Cost",
                    value=float(self.existing_item["unit_cost"]) if self.existing_item and "unit_cost" in self.existing_item else 0.0,
                    min_value=0.0,
                    help=ITEM_FORM_FIELDS["unit_cost"]["help"],
                    format="%.2f",
                    label_visibility="collapsed"
                )
                
                # Optional supplier selection
                suppliers = st.session_state.db_manager.get_suppliers()
                supplier_options = [(s["id"], s["name"]) for s in suppliers if s["is_active"]]
                supplier_id = None
                
                if supplier_options:
                    current_supplier = None
                    if self.existing_item and "supplier_id" in self.existing_item:
                        current_supplier = self.existing_item["supplier_id"]
                    
                    supplier_id = st.selectbox(
                        "Supplier",
                        options=[""] + [s[0] for s in supplier_options],
                        format_func=lambda x: "Select Supplier" if not x else next((s[1] for s in supplier_options if s[0] == x), x),
                        index=0 if not current_supplier else [i for i, s in enumerate([""] + [s[0] for s in supplier_options]) if s == current_supplier][0],
                        help="Select the primary supplier for this item"
                    )
                
                # Optional description
                description = st.text_area(
                    "Description",
                    value=self.existing_item.get("description", "") if self.existing_item else "",
                    help=ITEM_FORM_FIELDS["description"]["help"],
                    placeholder="Enter any additional notes or details about the item"
                )
                
                # Hidden SKU field for editing
                sku = ""
                if self.existing_item and "sku" in self.existing_item:
                    sku = st.text_input(
                        "SKU",
                        value=self.existing_item["sku"],
                        disabled=True,
                        help="SKU cannot be changed once assigned"
                    )
            
            # Submit button with keyboard shortcut
            submit_label = "Update Item" if self.existing_item else "Add Item"
            submitted = st.form_submit_button(
                f"{submit_label} (⌘/Ctrl + Enter)",
                use_container_width=True,
                type="primary"
            )
            
            if submitted:
                # Validate required fields
                required_fields = {
                    "name": name,
                    "category": category,
                    "unit_type": unit_type,
                    "unit_cost": unit_cost,
                    "min_quantity": min_quantity
                }
                
                missing_fields = [
                    field for field, value in required_fields.items() 
                    if not value and ITEM_FORM_FIELDS[field]["required"]
                ]
                
                if missing_fields:
                    st.error(f"❌ Required fields missing: {', '.join(missing_fields)}")
                    return None
                
                # Generate SKU if not provided
                if not sku:
                    existing_items = st.session_state.db_manager.get_items()
                    existing_skus = [item["sku"] for item in existing_items if item["sku"]]
                    sku = generate_sku(category, name, existing_skus)
                
                data = {
                    "name": name,
                    "description": description,
                    "category": category,
                    "unit_type": unit_type,
                    "sku": sku,
                    "unit_cost": unit_cost,
                    "min_quantity": min_quantity,
                    "max_quantity": max_quantity if max_quantity > 0 else None,
                    "supplier_id": supplier_id if supplier_id else None,
                    "quantity": initial_qty
                }
                
                # Include the ID if we're editing an existing item
                if self.existing_item and "id" in self.existing_item:
                    data["id"] = self.existing_item["id"]
                
                # Call the submit callback and handle the result
                if self.on_submit(data):
                    if "id" in data:
                        st.session_state.show_success = "✅ Item updated successfully!"
                    else:
                        st.session_state.show_success = "✅ Item created successfully!"
                    return data
                return None
            return None

class TransactionForm:
    """Form for creating inventory transactions."""
    
    def __init__(self, on_submit: Callable[[Dict[str, Any]], None]):
        """Initialize the TransactionForm.
        
        Args:
            on_submit: Callback function to handle form submission
        """
        self.on_submit = on_submit
    
    def _render_item_search(self, items):
        """Render the item search interface.
        
        Args:
            items: List of items to search through
            
        Returns:
            selected_item: The selected item or None
        """
        # Initialize session state for selected item
        if "selected_transaction_item" not in st.session_state:
            st.session_state.selected_transaction_item = None
        
        # Item search and selection
        search_col, info_col = st.columns([2, 1])
        
        with search_col:
            # Create a container for search to prevent form submission
            with st.container():
                # Search box for items (outside the form)
                search_query = st.text_input(
                    "Search Items",
                    value=st.session_state.get("item_search", ""),
                    help="Search by item name, SKU, or category",
                    placeholder="Start typing to search...",
                    key="transaction_search"  # Unique key to prevent conflicts
                ).strip().lower()
                
                # Filter items based on search
                filtered_items = items
                if search_query:
                    filtered_items = [
                        item for item in items
                        if search_query in item["name"].lower()
                        or search_query in (item.get("sku", "")).lower()
                        or search_query in item["category"].lower()
                    ]
                
                # Format items for display
                item_options = {
                    item["id"]: f"{item['name']} ({item['category']}) - {item['quantity']} {item['unit_type']}"
                    for item in filtered_items
                }
                
                # Item selection from filtered list
                default_item_index = 0
                if st.session_state.get("selected_item_id"):
                    try:
                        default_item_index = list(item_options.keys()).index(st.session_state.selected_item_id)
                    except ValueError:
                        pass
                
                item_id = st.selectbox(
                    "Select Item",
                    options=list(item_options.keys()) if filtered_items else [""],
                    format_func=lambda x: item_options.get(x, "No items found"),
                    help="Select the item for this transaction",
                    index=default_item_index if filtered_items else 0,
                    key="transaction_item_select"  # Unique key to prevent conflicts
                ) if filtered_items else None
        
        # Get selected item details for reference
        selected_item = next((item for item in items if item["id"] == item_id), None) if item_id else None
        
        if selected_item:
            with info_col:
                st.markdown("**Item Details**")
                st.info(f"""
                • Stock: {selected_item['quantity']} {selected_item['unit_type']}
                • Cost: {format_currency(selected_item['unit_cost'])}
                • Category: {selected_item['category']}
                """)
            
            # Add a "Proceed" button to confirm item selection
            if st.button("✅ Use Selected Item", key="confirm_item_selection"):
                st.session_state.selected_transaction_item = selected_item
                st.rerun()
        
        # Save search query to session state
        st.session_state["item_search"] = search_query
        return st.session_state.get("selected_transaction_item")

    def render(self):
        """Render the transaction form."""
        # Get items for selection
        items = st.session_state.db_manager.get_items()
        if not items:
            st.warning("No items available. Please add items first.")
            return False
        
        st.markdown("### 🔄 New Transaction")
        
        # If we have a selected item, show a summary and allow changing
        if st.session_state.get("selected_transaction_item"):
            item = st.session_state.selected_transaction_item
            st.success(f"Selected Item: {item['name']} ({item['category']})")
            if st.button("🔄 Change Item", key="change_transaction_item"):
                st.session_state.selected_transaction_item = None
                st.rerun()
        
        # Render search interface first if no item is selected
        selected_item = st.session_state.get("selected_transaction_item")
        if not selected_item:
            self._render_item_search(items)
            return False
            
        # Now render the transaction form
        with st.form("transaction_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                # Transaction type with radio buttons
                transaction_type_icons = {
                    "purchase": "🛍️",
                    "sale": "💰",
                    "transfer_in": "📥",
                    "transfer_out": "📤"
                }
                
                # Get default transaction type from session state
                default_type = st.session_state.get("default_transaction_type", "purchase")
                
                st.write("**Transaction Type**")
                transaction_type = st.radio(
                    "Select Transaction Type",
                    options=[e.value for e in TransactionType],
                    format_func=lambda x: f"{transaction_type_icons.get(x, '•')} {x.replace('_', ' ').title()}",
                    horizontal=True,
                    label_visibility="collapsed",
                    index=[e.value for e in TransactionType].index(default_type) if default_type in [e.value for e in TransactionType] else 0
                )
                
                # Quantity with validation
                quantity = st.number_input(
                    "Quantity",
                    min_value=1,
                    value=1,
                    help=f"Current stock: {selected_item['quantity']} {selected_item['unit_type']}"
                )
                
                # Show warning if selling more than available
                if transaction_type == "sale" and quantity > selected_item["quantity"]:
                    st.warning(f"⚠️ Not enough stock! Available: {selected_item['quantity']} {selected_item['unit_type']}")
            
            with col2:
                # Unit price with peso symbol
                st.markdown("**Unit Price** (₱)")
                unit_price = st.number_input(
                    "Unit Price",
                    min_value=0.0,
                    value=float(selected_item["unit_cost"]),
                    format="%.2f",
                    help="Price per unit",
                    label_visibility="collapsed"
                )
                
                # Optional notes
                notes = st.text_area(
                    "Notes",
                    placeholder="Enter any additional notes about this transaction",
                    help="Optional notes or remarks"
                )
            
            # Show total amount
            total_amount = quantity * unit_price
            st.info(f"Total Amount: {format_currency(total_amount)}")
            
            # Submit button
            submitted = st.form_submit_button("Submit Transaction")
            if submitted:
                # Validate quantity for sales
                if transaction_type == "sale" and quantity > selected_item["quantity"]:
                    st.error("❌ Not enough stock for this sale!")
                    return False
                
                # Prepare transaction data
                transaction_data = {
                    "item_id": selected_item["id"],
                    "transaction_type": transaction_type,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "notes": notes.strip() if notes else None
                }
                
                # Submit the transaction
                if self.on_submit(transaction_data):
                    return True
                
                return False

class SupplierForm:
    """Form for creating and editing suppliers."""
    
    def __init__(self, on_submit: Callable[[Dict[str, Any]], None], existing_supplier: Optional[Dict[str, Any]] = None):
        """Initialize the SupplierForm.
        
        Args:
            on_submit: Callback function to handle form submission
            existing_supplier: Optional dictionary containing existing supplier data for editing
        """
        self.on_submit = on_submit
        self.existing_supplier = existing_supplier

    def render(self):
        """Render the supplier form."""
        # Generate a unique form key
        form_key = f"supplier_form_{self.existing_supplier['id'] if self.existing_supplier else 'new'}"
        
        # Prepare success message key
        success_key = f"success_{form_key}"
        if success_key not in st.session_state:
            st.session_state[success_key] = False
        
        with st.form(form_key, clear_on_submit=True):
            # Essential Information
            st.subheader("Essential Information")
            
            name = st.text_input(
                "Supplier Name",
                value=self.existing_supplier.get("name", "") if self.existing_supplier else "",
                help=SUPPLIER_FORM_FIELDS["name"]["help"]
            ).strip()
            
            # Contact Information
            st.subheader("Contact Information")
            
            col1, col2 = st.columns(2)
            with col1:
                email = st.text_input(
                    "Email",
                    value=self.existing_supplier.get("contact_email", "") if self.existing_supplier else "",
                    help=SUPPLIER_FORM_FIELDS["contact_email"]["help"]
                ).strip()
            
            with col2:
                phone = st.text_input(
                    "Phone",
                    value=self.existing_supplier.get("phone", "") if self.existing_supplier else "",
                    help=SUPPLIER_FORM_FIELDS["phone"]["help"]
                ).strip()
            
            address = st.text_area(
                "Address",
                value=self.existing_supplier.get("address", "") if self.existing_supplier else "",
                help=SUPPLIER_FORM_FIELDS["address"]["help"]
            ).strip()
            
            remarks = st.text_area(
                "Notes",
                value=self.existing_supplier.get("remarks", "") if self.existing_supplier else "",
                help=SUPPLIER_FORM_FIELDS["remarks"]["help"],
                placeholder="Enter any additional notes about this supplier"
            ).strip()
            
            # Submit button
            submit_label = "Update Supplier" if self.existing_supplier else "Add Supplier"
            if st.form_submit_button(
                submit_label,
                use_container_width=True,
                type="primary"
            ):
                # Validate required fields
                if not name:
                    st.error("❌ Supplier name is required")
                    return None
                
                data = {
                    "name": name,
                    "contact_email": email,
                    "phone": phone,
                    "address": address,
                    "remarks": remarks
                }
                
                # Include ID if editing
                if self.existing_supplier and "id" in self.existing_supplier:
                    data["id"] = self.existing_supplier["id"]
                
                # Call submit callback and handle result
                if self.on_submit(data):
                    st.session_state[success_key] = True
                    return data
                return None
        
        # Show success message outside the form
        if st.session_state[success_key]:
            st.success("✅ Supplier updated successfully!" if self.existing_supplier else "✅ Supplier created successfully!")
            st.session_state[success_key] = False
            st.rerun()
        
        return None
