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
                
                self.on_submit(data)
                return data
            return None

class TransactionForm:
    """Form for creating inventory transactions."""
    
    def __init__(self, on_submit: Callable[[Dict[str, Any]], None]):
        """Initialize the TransactionForm.
        
        Args:
            on_submit: Callback function to handle form submission
        """
        self.on_submit = on_submit
    
    def render(self):
        """Render the transaction form."""
        # Get items for selection
        items = st.session_state.db_manager.get_items()
        if not items:
            st.warning("No items available. Please add items first.")
            return False
        
        st.markdown("### 🔄 New Transaction")
        
        with st.form("transaction_form", clear_on_submit=True):
            # Item search and selection
            search_col, info_col = st.columns([2, 1])
            
            with search_col:
                # Search box for items
                search_query = st.text_input(
                    "Search Items",
                    value=st.session_state.get("item_search", ""),
                    help="Search by item name, SKU, or category",
                    placeholder="Start typing to search..."
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
                    options=list(item_options.keys()),
                    format_func=lambda x: item_options[x],
                    help="Select the item for this transaction",
                    index=default_item_index if filtered_items else 0
                ) if filtered_items else None
            
            # Get selected item details for reference
            selected_item = next((item for item in items if item["id"] == item_id), None)
            if selected_item:
                with info_col:
                    st.markdown("**Item Details**")
                    st.info(f"""
                    • Stock: {selected_item['quantity']} {selected_item['unit_type']}
                    • Cost: {format_currency(selected_item['unit_cost'])}
                    • Category: {selected_item['category']}
                    """)
            
            if not item_id:
                st.warning("Please select an item to continue")
                submit_disabled = True
            else:
                submit_disabled = False
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Transaction type with default from session state
                default_type_index = 0
                transaction_types = ["purchase", "sale", "adjustment"]
                if st.session_state.get("default_transaction_type"):
                    try:
                        default_type_index = transaction_types.index(
                            st.session_state.default_transaction_type
                        )
                    except ValueError:
                        pass
                
                transaction_type = st.selectbox(
                    "Transaction Type",
                    options=transaction_types,
                    help="Select the type of transaction",
                    index=default_type_index
                )
                
                quantity = st.number_input(
                    "Quantity",
                    min_value=1,
                    value=1,
                    step=1,
                    help=f"Enter the quantity in {selected_item['unit_type'] if selected_item else 'units'}"
                )
            
            with col2:
                st.markdown("**Unit Price** (₱)")
                unit_price = st.number_input(
                    "Unit Price",
                    min_value=0.0,
                    value=float(selected_item['unit_cost']) if selected_item else 0.0,
                    step=0.01,
                    format="%.2f",
                    help="Enter the price per unit in Philippine Pesos",
                    label_visibility="collapsed"
                )
                
                reference_number = st.text_input(
                    "Reference Number",
                    help="Enter a reference number (e.g., PO number, invoice number)"
                )
            
            notes = st.text_area(
                "Notes",
                help="Enter any additional notes for this transaction"
            )
            
            submitted = st.form_submit_button(
                "Submit Transaction",
                disabled=submit_disabled,
                help="Submit the transaction" if not submit_disabled else "Please select an item first"
            )
            
            if submitted and not submit_disabled:
                # Save search query to session state
                st.session_state["item_search"] = search_query
                
                # Prepare transaction data
                data = {
                    "item_id": item_id,
                    "transaction_type": transaction_type,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "reference_number": reference_number,
                    "notes": notes
                }
                
                self.on_submit(data)
                return data
            return None

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
        st.markdown("### 🏢 Supplier Details")
        
        with st.form("supplier_form", clear_on_submit=True):
            form_container = st.container()
            with form_container:
                col1, col2 = st.columns(2)
                
                with col1:
                    name = st.text_input(
                        SUPPLIER_FORM_FIELDS["name"]["label"],
                        value=self.existing_supplier.get("name", "") if self.existing_supplier else "",
                        help=SUPPLIER_FORM_FIELDS["name"]["help"]
                    )
                    
                    contact_email = st.text_input(
                        SUPPLIER_FORM_FIELDS["contact_email"]["label"],
                        value=self.existing_supplier.get("contact_email", "") if self.existing_supplier else "",
                        help=SUPPLIER_FORM_FIELDS["contact_email"]["help"]
                    )
                    
                    phone = st.text_input(
                        SUPPLIER_FORM_FIELDS["phone"]["label"],
                        value=self.existing_supplier.get("phone", "") if self.existing_supplier else "",
                        help=SUPPLIER_FORM_FIELDS["phone"]["help"]
                    )
                
                with col2:
                    address = st.text_area(
                        SUPPLIER_FORM_FIELDS["address"]["label"],
                        value=self.existing_supplier.get("address", "") if self.existing_supplier else "",
                        help=SUPPLIER_FORM_FIELDS["address"]["help"],
                        height=100
                    )
                    
                    remarks = st.text_area(
                        SUPPLIER_FORM_FIELDS["remarks"]["label"],
                        value=self.existing_supplier.get("remarks", "") if self.existing_supplier else "",
                        help=SUPPLIER_FORM_FIELDS["remarks"]["help"],
                        height=100
                    )
            
            col_submit1, col_submit2, col_submit3 = st.columns([1, 2, 1])
            with col_submit2:
                submitted = st.form_submit_button(
                    "💾 Save Supplier",
                    use_container_width=True,
                    type="primary"
                )
            
            if submitted:
                # Validate required fields
                if not name:
                    st.error("❌ Supplier name is required")
                    return None
                
                data = {
                    "name": name,
                    "contact_email": contact_email,
                    "phone": phone,
                    "address": address,
                    "remarks": remarks
                }
                
                # Add id if editing existing supplier
                if self.existing_supplier and "id" in self.existing_supplier:
                    data["id"] = self.existing_supplier["id"]
                
                self.on_submit(data)
                return data
            return None
