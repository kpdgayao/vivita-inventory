"""Main application file for the Vivita Inventory Management System."""

import os
from typing import Dict, Any
import streamlit as st
import pandas as pd
from app.components.forms import ItemForm, TransactionForm, SupplierForm
from app.components.sidebar import Sidebar
from app.components.dashboard import Dashboard
from app.utils.helpers import format_currency, generate_sku, format_timestamp, calculate_weighted_average_cost
from app.utils.constants import CategoryType, TransactionType, UnitType
from dotenv import load_dotenv
from datetime import datetime

from app.database.supabase_manager import SupabaseManager
from app.analytics.analytics_manager import AnalyticsManager

# Load environment variables
load_dotenv()

# Page configuration - must be the first Streamlit command
st.set_page_config(
    page_title="Vivita Inventory",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_managers():
    """Initialize database and analytics managers."""
    if "db_manager" not in st.session_state:
        st.session_state.db_manager = SupabaseManager()
    
    if "analytics_manager" not in st.session_state:
        st.session_state.analytics_manager = AnalyticsManager(st.session_state.db_manager)

def handle_page_change(new_page: str):
    """Handle page navigation."""
    st.session_state.page = new_page

def handle_item_submit(item_data: Dict[str, Any]):
    """Handle item form submission."""
    db = st.session_state.db_manager
    
    # Ensure quantity is an integer
    if "quantity" in item_data:
        try:
            item_data["quantity"] = int(item_data["quantity"])
        except (ValueError, TypeError):
            item_data["quantity"] = 0
    
    if "id" in item_data:
        # Update existing item
        result = db.update_item(item_data["id"], item_data)
        if result:
            st.session_state.show_success = "✅ Item updated successfully!"
            st.session_state.show_new_item_form = False  # Close the form
        else:
            st.error("❌ Failed to update item")
            return
    else:
        # Create new item
        try:
            result = db.create_item(item_data)
            if result:
                st.session_state.show_success = "✅ Item created successfully!"
                st.session_state.show_new_item_form = False  # Close the form
            else:
                st.error("❌ Failed to create item. Please check all required fields are filled correctly.")
                return
        except ValueError as e:
            st.error(f"❌ {str(e)}")
            return
        except Exception as e:
            st.error(f"❌ An unexpected error occurred: {str(e)}")
            return
    
    # Only rerun if we had a success
    st.rerun()

def handle_transaction_submit(transaction_data: Dict[str, Any]):
    """Handle transaction form submission."""
    try:
        print(f"Submitting transaction: {transaction_data}")  # Debug log
        
        # Validate required fields
        required_fields = ['item_id', 'transaction_type', 'quantity', 'unit_price']
        missing_fields = [field for field in required_fields if not transaction_data.get(field)]
        if missing_fields:
            st.error(f"❌ Missing required fields: {', '.join(missing_fields)}")
            return False
        
        # Get current item details
        item = st.session_state.db_manager.get_item(transaction_data['item_id'])
        if not item:
            st.error("❌ Selected item not found.")
            return False
            
        # Validate quantity for sales
        if transaction_data['transaction_type'] == 'sale' and transaction_data['quantity'] > item['quantity']:
            st.error(f"❌ Not enough stock. Current stock: {item['quantity']} {item['unit_type']}")
            return False
        
        # Create the transaction
        result = st.session_state.db_manager.create_transaction(transaction_data)
        
        if result:
            st.success("✅ Transaction recorded successfully!")
            st.session_state.show_new_transaction_form = False
            st.rerun()
            return True
        else:
            st.error("❌ Failed to record transaction. Please check the logs for details.")
            return False
            
    except ValueError as ve:
        st.error(f"❌ {str(ve)}")
        return False
    except Exception as e:
        st.error(f"❌ An unexpected error occurred: {str(e)}")
        print(f"Error in handle_transaction_submit: {e}")  # Debug log
        return False

def handle_supplier_submit(supplier_data: Dict[str, Any]):
    """Handle supplier form submission."""
    db = st.session_state.db_manager
    
    if "id" in supplier_data:
        # Update existing supplier
        result = db.update_supplier(supplier_data["id"], supplier_data)
        if result:
            st.session_state.show_success = "✅ Supplier updated successfully!"
            st.session_state.editing_supplier = None  # Clear editing state
            st.rerun()
        else:
            st.error("❌ Failed to update supplier")
    else:
        # Create new supplier
        result = db.create_supplier(supplier_data)
        if result:
            st.session_state.show_success = "✅ Supplier created successfully!"
            st.session_state.show_new_supplier_form = False  # Close the form
            st.rerun()
        else:
            st.error("❌ Failed to create supplier")

def render_inventory_page():
    """Render the inventory management page."""
    st.title("📦 Inventory Management")
    
    # Show success message if present
    if "show_success" in st.session_state:
        st.success(st.session_state.show_success)
        del st.session_state.show_success
    
    # Initialize session state variables
    if "editing_item" not in st.session_state:
        st.session_state.editing_item = None
    if "quick_update_item" not in st.session_state:
        st.session_state.quick_update_item = None
    
    # Tabs for different inventory views
    tab1, tab2 = st.tabs([
        "🗂️ Item List",
        "➕ Add Items"
    ])
    
    with tab1:
        # Search and filter
        col1, col2 = st.columns([3, 1])
        with col1:
            search = st.text_input("🔍 Search items by name, SKU, or description")
        with col2:
            sort_by = st.selectbox(
                "Sort by",
                ["Name ↑", "Name ↓", "Stock ↑", "Stock ↓", "Category"]
            )
        
        # Get and filter items
        items = st.session_state.db_manager.get_items()
        if search:
            search = search.lower()
            items = [
                item for item in items
                if search in item["name"].lower()
                or search in (item.get("sku", "")).lower()
                or search in (item.get("description", "")).lower()
            ]
        
        # Sort items
        if sort_by == "Name ↑":
            items.sort(key=lambda x: x["name"])
        elif sort_by == "Name ↓":
            items.sort(key=lambda x: x["name"], reverse=True)
        elif sort_by == "Stock ↑":
            items.sort(key=lambda x: x["quantity"])
        elif sort_by == "Stock ↓":
            items.sort(key=lambda x: x["quantity"], reverse=True)
        elif sort_by == "Category":
            items.sort(key=lambda x: (x["category"], x["name"]))
        
        # Display items in a scrollable container
        with st.container():
            for item in items:
                with st.expander(
                    f"{item['name']} ({item['quantity']} {item['unit_type']})",
                    expanded=st.session_state.editing_item == item["id"] or st.session_state.quick_update_item == item["id"]
                ):
                    if st.session_state.editing_item == item["id"]:
                        # Show edit form
                        st.subheader("📝 Edit Item")
                        edit_form = ItemForm(handle_item_submit, item)
                        edit_form.render()
                        if st.button("Cancel Edit", key=f"cancel_edit_{item['id']}"):
                            st.session_state.editing_item = None
                            st.rerun()
                    elif st.session_state.quick_update_item == item["id"]:
                        # Show quick update form
                        st.subheader("🔄 Quick Update")
                        with st.form(key=f"quick_update_{item['id']}"):
                            new_qty = st.number_input(
                                "New Quantity",
                                value=item["quantity"],
                                min_value=0,
                                step=1
                            )
                            col1, col2 = st.columns([1, 1])
                            with col1:
                                if st.form_submit_button("Update"):
                                    result = st.session_state.db_manager.update_item(
                                        item["id"],
                                        {"quantity": new_qty}
                                    )
                                    if result:
                                        st.session_state.show_success = "✅ Quantity updated successfully!"
                                        st.session_state.quick_update_item = None
                                        st.rerun()
                                    else:
                                        st.error("Failed to update quantity")
                            with col2:
                                if st.form_submit_button("Cancel"):
                                    st.session_state.quick_update_item = None
                                    st.rerun()
                    else:
                        # Show item details
                        col1, col2, col3 = st.columns([2, 2, 1])
                        
                        with col1:
                            st.caption("Details")
                            st.write(f"**Category:** {item['category'].replace('_', ' ').title()}")
                            st.write(f"**SKU:** {item.get('sku', 'N/A')}")
                            if item.get('description'):
                                st.write(f"**Description:** {item['description']}")
                        
                        with col2:
                            st.write("**Stock Info**")
                            st.write(f"**Unit Cost:** {format_currency(item['unit_cost'])}")
                            st.write(f"**Min Quantity:** {item['min_quantity']}")
                            if item.get('max_quantity'):
                                st.write(f"**Max Quantity:** {item['max_quantity']}")
                        
                        with col3:
                            st.write("**Actions**")
                            if st.button("📝 Edit", key=f"edit_{item['id']}"):
                                st.session_state.editing_item = item["id"]
                                st.rerun()
                            
                            if st.button("🔄 Quick Update", key=f"quick_{item['id']}"):
                                st.session_state.quick_update_item = item["id"]
                                st.rerun()
    
    with tab2:
        # Single item form
        form = ItemForm(handle_item_submit)
        form.render()

def render_transactions_page():
    """Render the transactions page."""
    st.title("Transaction History")
    
    # Initialize session state
    if "show_new_transaction_form" not in st.session_state:
        st.session_state.show_new_transaction_form = False
    
    # Add new transaction button
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("➕ New Transaction", use_container_width=True):
            st.session_state.show_new_transaction_form = True
            st.rerun()
    
    # Show transaction form if requested
    if st.session_state.show_new_transaction_form:
        st.subheader("New Transaction")
        form = TransactionForm(handle_transaction_submit)
        if form.render():
            # Form submission is handled in the form's render method
            pass
        if st.button("Cancel"):
            st.session_state.show_new_transaction_form = False
            st.session_state.selected_item_id = None
            st.rerun()
        st.divider()
    
    # Get transactions and items
    transactions = st.session_state.db_manager.get_transactions()
    items = st.session_state.db_manager.get_items()
    
    if not transactions:
        st.info("No transactions found.")
        return
    
    # Create tabs for different views
    tab1, tab2 = st.tabs(["📅 Chronological View", "📦 Item View"])
    
    with tab1:
        st.markdown("#### Recent Transactions")
        # Sort transactions by date (newest first)
        sorted_transactions = sorted(
            transactions,
            key=lambda x: x.get("created_at", ""),
            reverse=True
        )
        
        for transaction in sorted_transactions:
            # Get item details
            item = next((i for i in items if i["id"] == transaction["item_id"]), None)
            if not item:
                continue
            
            # Format the transaction date
            formatted_date = format_timestamp(transaction["created_at"])
            
            # Determine transaction icon and color
            icon_map = {
                "purchase": "📥",
                "sale": "📤",
                "adjustment": "🔄"
            }
            icon = icon_map.get(transaction["transaction_type"], "❓")
            
            # Create an expander for each transaction
            with st.expander(f"{icon} {formatted_date} - {item['name']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Item Details:**")
                    st.write(f"- Name: {item['name']}")
                    st.write(f"- Category: {item['category']}")
                    st.write(f"- SKU: {item.get('sku', 'N/A')}")
                
                with col2:
                    st.write("**Transaction Details:**")
                    st.write(f"- Type: {transaction['transaction_type'].title()}")
                    st.write(f"- Quantity: {transaction['quantity']} {item['unit_type']}")
                    st.write(f"- Unit Price: {format_currency(transaction['unit_price'])}")
                
                if transaction.get("reference_number"):
                    st.write(f"**Reference:** {transaction['reference_number']}")
                if transaction.get("notes"):
                    st.write(f"**Notes:** {transaction['notes']}")
    
    with tab2:
        st.markdown("#### Transactions by Item")
        
        # Group transactions by item
        item_transactions = {}
        for transaction in transactions:
            if transaction["item_id"] not in item_transactions:
                item_transactions[transaction["item_id"]] = []
            item_transactions[transaction["item_id"]].append(transaction)
        
        # Sort items alphabetically
        sorted_items = sorted(items, key=lambda x: x["name"].lower())
        
        # Display transactions for each item
        for item in sorted_items:
            if item["id"] not in item_transactions:
                continue
                
            # Sort transactions chronologically (oldest first) for running balance
            item_trans = sorted(
                item_transactions[item["id"]],
                key=lambda x: x.get("created_at", ""),
                reverse=False
            )
            
            with st.expander(f"📦 {item['name']} ({len(item_trans)} transactions)"):
                # Show item details
                st.markdown(f"**{item['name']}** ({item['category']})")
                st.write(f"SKU: {item.get('sku', 'N/A')}")
                st.write(f"Current Quantity: {item['quantity']} {item['unit_type']}")
                
                # Show transactions in a table
                if item_trans:
                    # Calculate initial balance by working backwards from current quantity
                    current_balance = item['quantity']
                    for t in reversed(item_trans):
                        if t['transaction_type'] == 'purchase':
                            current_balance -= t['quantity']
                        elif t['transaction_type'] == 'sale':
                            current_balance += t['quantity']
                        elif t['transaction_type'] == 'adjustment':
                            current_balance -= t['quantity']  # Subtract adjustment to get to previous state
                    
                    initial_balance = current_balance
                    st.write(f"Initial Balance: {initial_balance} {item['unit_type']}")
                    
                    # Now calculate running balance forward from initial state
                    data = []
                    running_balance = initial_balance
                    for t in item_trans:
                        # Calculate balance change
                        quantity_change = t['quantity']
                        if t['transaction_type'] == 'sale':
                            quantity_change = -quantity_change
                        running_balance += quantity_change
                        
                        # Format quantity with sign
                        quantity_str = (
                            f"+{t['quantity']}" if t['transaction_type'] == 'purchase'
                            else f"-{t['quantity']}" if t['transaction_type'] == 'sale'
                            else f"±{t['quantity']}"
                        )
                        
                        data.append({
                            "Date": format_timestamp(t["created_at"]),
                            "Type": t["transaction_type"].title(),
                            "Change": f"{quantity_str} {item['unit_type']}",
                            "Balance": f"{running_balance} {item['unit_type']}",
                            "Unit Price": format_currency(t["unit_price"]),
                            "Reference": t.get("reference_number", ""),
                            "Notes": t.get("notes", "")
                        })
                    
                    # Reverse the data to show newest first while maintaining correct balance
                    data.reverse()
                    
                    st.markdown("##### Transaction History")
                    st.dataframe(
                        data,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Date": st.column_config.DatetimeColumn(
                                "Date",
                                format="MMM DD, YYYY h:mm a"
                            ),
                            "Change": st.column_config.Column(
                                "Quantity Change",
                                help="+ for purchases, - for sales, ± for adjustments"
                            ),
                            "Balance": st.column_config.Column(
                                "Running Balance",
                                help="Quantity after this transaction"
                            )
                        }
                    )

def render_suppliers_page():
    """Render the supplier management page."""
    st.title("Supplier Management")
    
    # Show success message if present
    if "show_success" in st.session_state:
        st.success(st.session_state.show_success)
        del st.session_state.show_success
    
    # Initialize session state
    if "show_new_supplier_form" not in st.session_state:
        st.session_state.show_new_supplier_form = False
    if "editing_supplier" not in st.session_state:
        st.session_state.editing_supplier = None
    
    # Add new supplier button (only show if not editing)
    if not st.session_state.editing_supplier and not st.session_state.show_new_supplier_form:
        if st.button("➕ Add New Supplier"):
            st.session_state.show_new_supplier_form = True
            st.rerun()
    
    # Edit form
    if st.session_state.editing_supplier:
        st.subheader("✏️ Edit Supplier")
        edit_form = SupplierForm(handle_supplier_submit, st.session_state.editing_supplier)
        edit_form.render()
        if st.button("Cancel Edit"):
            st.session_state.editing_supplier = None
            st.rerun()
        return
    
    # New supplier form
    if st.session_state.show_new_supplier_form:
        st.subheader("➕ New Supplier")
        new_form = SupplierForm(handle_supplier_submit)
        new_form.render()
        if st.button("Cancel"):
            st.session_state.show_new_supplier_form = False
            st.rerun()
        return
    
    # Supplier list
    suppliers = st.session_state.db_manager.get_suppliers()
    
    if not suppliers:
        st.info("No suppliers found. Add your first supplier!")
        return
    
    for supplier in suppliers:
        with st.expander(f"{supplier['name']}"):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write("**Contact Information**")
                if supplier.get("contact_email"):
                    st.write(f"📧 Email: {supplier['contact_email']}")
                if supplier.get("phone"):
                    st.write(f"📞 Phone: {supplier['phone']}")
                if supplier.get("address"):
                    st.write(f"📍 Address: {supplier['address']}")
            
            with col2:
                st.write("**Notes**")
                if supplier.get("remarks"):
                    st.write(supplier["remarks"])
                else:
                    st.write("No remarks")
            
            with col3:
                st.write("**Actions**")
                if st.button("✏️ Edit", key=f"edit_{supplier['id']}"):
                    st.session_state.editing_supplier = supplier
                    st.rerun()
                
                if st.button("❌ Delete", key=f"delete_{supplier['id']}"):
                    if st.session_state.db_manager.delete_supplier(supplier["id"]):
                        st.success("Supplier deleted successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to delete supplier")

def render_analytics_page():
    """Render the analytics page."""
    st.title("📊 Detailed Analytics")
    analytics = st.session_state.analytics_manager
    
    # Category Distribution with percentage
    st.subheader("📦 Category Distribution")
    categories = analytics.get_category_distribution()
    
    if categories:
        total_value = sum(cat['value'] for cat in categories)
        for category in categories:
            percentage = (category['value'] / total_value * 100) if total_value > 0 else 0
            st.write(
                f"**{category['category']}**\n\n"
                f"Value: ₱{category['value']:,.2f} ({percentage:.1f}%)"
            )
            st.progress(percentage / 100)
    else:
        st.info("No items found in inventory.")
    
    # Transaction Analysis
    st.subheader("📈 Transaction Analysis")
    trends = analytics.get_transaction_trends(days=30)
    
    if trends and trends['transaction_types']:
        st.write("Transaction Distribution by Type:")
        for t_type in trends['transaction_types']:
            st.write(f"- {t_type['type'].title()}: {t_type['count']} transactions")
    else:
        st.info("No transaction data available.")
    
    # Low Stock Items
    st.subheader("⚠️ Low Stock Items")
    low_stock = analytics.get_stock_alerts()
    
    if low_stock:
        for item in low_stock:
            st.write(
                f"**{item['name']}**\n\n"
                f"Current Stock: {item['quantity']} {item['unit_type']} | "
                f"Minimum Required: {item['min_quantity']} {item['unit_type']}"
            )
    else:
        st.info("No items are currently low in stock.")

def export_data_to_csv():
    """Export inventory data to CSV format."""
    try:
        import pandas as pd
        from io import StringIO
        from decimal import Decimal
        from app.utils.helpers import calculate_weighted_average_cost
        
        db = st.session_state.db_manager
        
        # Get all data
        items = pd.DataFrame(db.get_items())
        all_transactions = db.get_transactions()
        transactions = pd.DataFrame(all_transactions)
        
        if transactions.empty:
            st.warning("No transaction data available to export.")
            return None
            
        # Process transactions data
        if not transactions.empty:
            # Convert timestamps to readable format
            transactions['created_at'] = pd.to_datetime(transactions['created_at'])
            transactions = transactions.sort_values('created_at')
            
            # Add item details to transactions
            items_dict = {item['id']: item for item in db.get_items()}
            transactions['item_name'] = transactions['item_id'].map(lambda x: items_dict[x]['name'])
            transactions['unit_type'] = transactions['item_id'].map(lambda x: items_dict[x]['unit_type'])
            
            # Calculate transaction values
            transactions['value'] = transactions.apply(
                lambda row: Decimal(str(row['quantity'])) * Decimal(str(row['unit_price'])), 
                axis=1
            )
            
            # Initialize balance columns
            transactions['balance_qty'] = 0
            transactions['balance_value'] = 0
            transactions['weighted_avg_cost'] = 0
            
            # Calculate running balances for each item
            for item_id in transactions['item_id'].unique():
                item_mask = transactions['item_id'] == item_id
                item_trans = transactions[item_mask].copy()
                
                # Get initial balance from items table
                initial_qty = Decimal(str(items_dict[item_id]['quantity']))
                initial_cost = Decimal(str(items_dict[item_id]['unit_cost']))
                initial_value = initial_qty * initial_cost
                
                # Add initial balance row
                initial_row = pd.DataFrame([{
                    'created_at': transactions['created_at'].min(),
                    'item_id': item_id,
                    'item_name': items_dict[item_id]['name'],
                    'transaction_type': 'initial',
                    'quantity': float(initial_qty),
                    'unit_price': float(initial_cost),
                    'value': float(initial_value),
                    'unit_type': items_dict[item_id]['unit_type'],
                    'notes': 'Initial Balance',
                    'weighted_avg_cost': float(initial_cost)
                }])
                
                # Calculate running balances
                qty_balance = initial_qty
                value_balance = initial_value
                running_transactions = []
                
                for _, row in item_trans.iterrows():
                    trans_qty = Decimal(str(row['quantity']))
                    trans_price = Decimal(str(row['unit_price']))
                    trans_value = Decimal(str(row['value']))
                    
                    if row['transaction_type'] == 'purchase':
                        qty_balance += trans_qty
                        value_balance += trans_value
                    elif row['transaction_type'] == 'sale':
                        qty_balance -= trans_qty
                        # Use weighted average cost for sales value
                        running_transactions.append({
                            'transaction_type': 'purchase',
                            'quantity': float(trans_qty),
                            'unit_price': float(trans_price)
                        })
                        wac = calculate_weighted_average_cost(running_transactions)
                        sale_value = trans_qty * wac
                        value_balance -= sale_value
                    elif row['transaction_type'] == 'adjustment':
                        qty_diff = trans_qty - qty_balance
                        qty_balance = trans_qty
                        # Recalculate value based on current WAC
                        if running_transactions:
                            wac = calculate_weighted_average_cost(running_transactions)
                            value_balance = qty_balance * wac
                        else:
                            value_balance = qty_balance * initial_cost
                    
                    # Calculate WAC for this point in time
                    current_transactions = running_transactions.copy()
                    if current_transactions:
                        wac = calculate_weighted_average_cost(current_transactions)
                    else:
                        wac = initial_cost
                    
                    # Update the main transactions DataFrame
                    transactions.loc[row.name, 'balance_qty'] = float(qty_balance)
                    transactions.loc[row.name, 'balance_value'] = float(value_balance)
                    transactions.loc[row.name, 'weighted_avg_cost'] = float(wac)
            
            # Format dates
            transactions['created_at'] = transactions['created_at'].dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Reorder columns for better readability
            columns = [
                'created_at', 'item_name', 'transaction_type', 'quantity', 
                'unit_price', 'value', 'weighted_avg_cost', 'balance_qty', 'balance_value',
                'unit_type', 'notes', 'item_id'
            ]
            transactions = transactions[columns]
        
        # Create a buffer to store the CSV data
        buffer = StringIO()
        transactions.to_csv(buffer, index=False)
        return buffer.getvalue()
        
    except Exception as e:
        st.error(f"❌ Error exporting data: {str(e)}")
        print(f"Export error: {str(e)}")  # For debugging
        return None

def render_settings_page():
    """Render the settings page."""
    st.title("⚙️ Data Management")
    
    # Export Transactions
    st.subheader("📥 Export Transactions")
    st.write("Download your transaction history in CSV format.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        csv_data = export_data_to_csv()
        if csv_data:
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button(
                "Download Transactions CSV",
                data=csv_data,
                file_name=f"vivita_transactions_{current_time}.csv",
                mime="text/csv",
                help="Download all transactions as CSV"
            )
    
    # Data Backup
    st.subheader("💾 Data Backup")
    st.info(
        "Your data is automatically backed up in the Supabase database. "
        "Use the export function above to keep local copies of your transactions."
    )

def render_settings_page_original():
    """Render the settings page."""
    st.markdown("### ⚙️ Settings")
    
    # User preferences
    st.markdown("#### 👤 User Preferences")
    default_view = st.selectbox(
        "Default View",
        options=["Dashboard", "Inventory", "Transactions"],
        help="Choose which page to show when you first open the app"
    )
    
    enable_notifications = st.checkbox(
        "Enable Notifications",
        help="Get notified about low stock and other important events"
    )
    
    items_per_page = st.number_input(
        "Items per Page",
        min_value=10,
        max_value=100,
        value=20,
        help="Number of items to show in tables and lists"
    )
    
    # Export/Import
    st.markdown("#### 💾 Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        csv_data = export_data_to_csv()
        if csv_data:
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button(
                "📥 Export Data",
                data=csv_data,
                file_name=f"vivita_inventory_export_{current_time}.csv",
                mime="text/csv",
                help="Download all inventory data as CSV"
            )
    
    with col2:
        uploaded_file = st.file_uploader(
            "Import Data",
            type=["csv"],
            help="Upload a CSV file to import data"
        )
        if uploaded_file is not None:
            st.info("ℹ️ Import functionality coming soon!")

def main():
    """Main entry point for the Streamlit application."""
    # Initialize managers
    initialize_managers()
    
    # Initialize page state if not exists
    if "page" not in st.session_state:
        st.session_state.page = "dashboard"
    
    # Create sidebar and dashboard with proper dependencies
    filters = Sidebar.render(handle_page_change, st.session_state.page)
    dashboard = Dashboard(st.session_state.analytics_manager)
    
    # Custom CSS for better styling
    st.markdown("""
        <style>
            /* Improve spacing and readability */
            .block-container {
                padding-top: 2rem;
                padding-bottom: 2rem;
            }
            
            /* Better heading styles */
            h1 {
                color: #1f77b4;
                font-size: 2.5rem !important;
                font-weight: 700 !important;
                margin-bottom: 1.5rem !important;
            }
            h2 {
                color: #2c3e50;
                font-size: 1.8rem !important;
                font-weight: 600 !important;
                margin-bottom: 1rem !important;
            }
            
            /* Improved metric cards */
            [data-testid="stMetricValue"] {
                font-size: 1.8rem !important;
                font-weight: 700 !important;
                color: #1f77b4 !important;
            }
            [data-testid="stMetricLabel"] {
                font-size: 1rem !important;
                font-weight: 600 !important;
                color: #2c3e50 !important;
            }
            
            /* Better form styling */
            .stTextInput, .stNumberInput, .stSelectbox {
                margin-bottom: 1rem !important;
            }
            
            /* Improved button styling */
            .stButton button {
                width: 100%;
                border-radius: 4px !important;
                padding: 0.5rem 1rem !important;
                font-weight: 600 !important;
            }
            
            /* Better expander styling */
            .streamlit-expanderHeader {
                font-size: 1.1rem !important;
                font-weight: 600 !important;
                color: #2c3e50 !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # Initialize session state
    if "show_new_item_form" not in st.session_state:
        st.session_state.show_new_item_form = False
    if "show_new_transaction_form" not in st.session_state:
        st.session_state.show_new_transaction_form = False
    if "show_new_supplier_form" not in st.session_state:
        st.session_state.show_new_supplier_form = False
    if "selected_item_id" not in st.session_state:
        st.session_state.selected_item_id = None
    if "selected_supplier_id" not in st.session_state:
        st.session_state.selected_supplier_id = None

    # Render main application code
    if st.session_state.page == "dashboard":
        dashboard.render()
    elif st.session_state.page == "inventory":
        render_inventory_page()
    elif st.session_state.page == "transactions":
        render_transactions_page()
    elif st.session_state.page == "suppliers":
        render_suppliers_page()
    elif st.session_state.page == "analytics":
        render_analytics_page()
    elif st.session_state.page == "settings":
        render_settings_page()

if __name__ == "__main__":
    main()
