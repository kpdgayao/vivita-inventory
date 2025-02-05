"""Main application file for the Vivita Inventory Management System."""

import os
from typing import Dict, Any
import streamlit as st
import pandas as pd
from app.components.forms import ItemForm, TransactionForm, SupplierForm
from app.components.sidebar import Sidebar
from app.components.dashboard import Dashboard
from app.utils.helpers import format_currency, generate_sku
from app.utils.constants import CategoryType, TransactionType, UnitType
from dotenv import load_dotenv
from datetime import datetime

from app.database.supabase_manager import SupabaseManager
from app.analytics.analytics_manager import AnalyticsManager

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Vivita Inventory",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
if "page" not in st.session_state:
    st.session_state.page = "dashboard"
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

def initialize_managers():
    """Initialize database and analytics managers."""
    if "db_manager" not in st.session_state:
        st.session_state.db_manager = SupabaseManager()
    
    if "analytics_manager" not in st.session_state:
        st.session_state.analytics_manager = AnalyticsManager(st.session_state.db_manager)

def handle_page_change(new_page: str):
    """Handle page navigation."""
    st.session_state.page = new_page
    st.experimental_rerun()

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
            st.success("✅ Item updated successfully!")
            st.session_state.show_new_item_form = False  # Close the form
            st.experimental_rerun()  # Refresh the page
        else:
            st.error("❌ Failed to update item")
    else:
        # Create new item
        try:
            result = db.create_item(item_data)
            if result:
                st.success("✅ Item created successfully!")
                st.session_state.show_new_item_form = False  # Close the form
                st.experimental_rerun()  # Refresh the page
            else:
                st.error("❌ Failed to create item. Please check all required fields are filled correctly.")
        except ValueError as e:
            st.error(f"❌ {str(e)}")
        except Exception as e:
            st.error(f"❌ An unexpected error occurred: {str(e)}")

def handle_transaction_submit(transaction_data: Dict[str, Any]):
    """Handle transaction form submission."""
    db = st.session_state.db_manager
    
    # Attempt to create the transaction
    result = db.create_transaction(transaction_data)
    
    if result:
        st.success("✅ Transaction recorded successfully!")
        # Reset the form state
        st.session_state.show_new_transaction_form = False
        st.session_state.selected_item_id = None
        # Force a rerun to refresh the data
        st.experimental_rerun()
    else:
        st.error("❌ Failed to record transaction")

def handle_supplier_submit(supplier_data: Dict[str, Any]):
    """Handle supplier form submission."""
    db = st.session_state.db_manager
    
    if "id" in supplier_data:
        # Update existing supplier
        result = db.update_supplier(supplier_data["id"], supplier_data)
        if result:
            st.success("Supplier updated successfully!")
        else:
            st.error("Failed to update supplier")
    else:
        # Create new supplier
        result = db.create_supplier(supplier_data)
        if result:
            st.success("Supplier created successfully!")
            st.session_state.show_new_supplier_form = False
        else:
            st.error("Failed to create supplier")

def render_inventory_page():
    """Render the inventory management page."""
    st.title("📦 Inventory Management")
    
    # Tabs for different inventory views
    tab1, tab2, tab3 = st.tabs([
        "🗂️ Item List",
        "➕ Add Items",
        "📥 Bulk Operations"
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
                    expanded=False
                ):
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.caption("Details")
                        st.write(f"**Category:** {item['category'].replace('_', ' ').title()}")
                        st.write(f"**SKU:** {item.get('sku', 'N/A')}")
                        if item.get('description'):
                            st.write(f"**Description:** {item['description']}")
                    
                    with col2:
                        st.caption("Stock Info")
                        st.write(f"**Unit Cost:** {format_currency(item['unit_cost'])}")
                        st.write(f"**Min Quantity:** {item['min_quantity']}")
                        if item.get('max_quantity'):
                            st.write(f"**Max Quantity:** {item['max_quantity']}")
                    
                    with col3:
                        st.caption("Actions")
                        if st.button("📝 Edit", key=f"edit_{item['id']}"):
                            st.session_state.show_edit_item_form = True
                            st.session_state.selected_item = item
                            st.rerun()
                        
                        if st.button("🔄 Quick Update", key=f"quick_{item['id']}"):
                            with st.form(key=f"quick_update_{item['id']}"):
                                new_qty = st.number_input(
                                    "New Quantity",
                                    value=item["quantity"],
                                    min_value=0,
                                    step=1
                                )
                                if st.form_submit_button("Update"):
                                    st.session_state.db_manager.update_item(
                                        item["id"],
                                        {"quantity": new_qty}
                                    )
                                    st.rerun()
    
    with tab2:
        # Single item form
        form = ItemForm(handle_item_submit)
        form.render()
    
    with tab3:
        st.subheader("Bulk Operations")
        
        # Bulk update from CSV
        st.markdown("### 📤 Import Items")
        uploaded_file = st.file_uploader(
            "Upload CSV file",
            type="csv",
            help="CSV should have columns: name,category,unit_type,quantity,unit_cost,min_quantity"
        )
        
        if uploaded_file:
            import pandas as pd
            try:
                df = pd.read_csv(uploaded_file)
                required_columns = ["name", "category", "unit_type", "quantity", "unit_cost", "min_quantity"]
                missing_columns = [col for col in required_columns if col not in df.columns]
                
                if missing_columns:
                    st.error(f"Missing required columns: {', '.join(missing_columns)}")
                else:
                    st.write("Preview of items to import:")
                    st.dataframe(df.head())
                    
                    if st.button("Import Items"):
                        with st.spinner("Importing items..."):
                            for _, row in df.iterrows():
                                item_data = row.to_dict()
                                handle_item_submit(item_data)
                            st.success("✅ Items imported successfully!")
                            st.rerun()
            
            except Exception as e:
                st.error(f"Error reading CSV: {str(e)}")
        
        # Export template
        if st.button("📥 Download Template"):
            template_data = {
                "name": ["Example Item 1", "Example Item 2"],
                "category": ["raw_materials", "finished_goods"],
                "unit_type": ["piece", "kg"],
                "quantity": [10, 20],
                "unit_cost": [100.00, 200.00],
                "min_quantity": [5, 10],
                "max_quantity": [50, 100],
                "description": ["Sample description 1", "Sample description 2"]
            }
            df = pd.DataFrame(template_data)
            st.download_button(
                "📥 Download CSV Template",
                df.to_csv(index=False),
                "inventory_template.csv",
                "text/csv"
            )
        
        # Bulk quick update
        st.markdown("### 🔄 Quick Stock Update")
        st.markdown("""
        Update multiple items quickly:
        1. Select items from the list
        2. Enter the new quantity
        3. Click Update to save changes
        """)
        
        items = st.session_state.db_manager.get_items()
        selected_items = st.multiselect(
            "Select items to update",
            options=[item["id"] for item in items],
            format_func=lambda x: next((item["name"] for item in items if item["id"] == x), x)
        )
        
        if selected_items:
            with st.form("bulk_update_form"):
                update_type = st.radio(
                    "Update type",
                    ["Set to", "Add", "Subtract"],
                    horizontal=True
                )
                
                quantity = st.number_input(
                    "Quantity",
                    min_value=0,
                    value=0
                )
                
                if st.form_submit_button("Update Selected Items"):
                    with st.spinner("Updating items..."):
                        for item_id in selected_items:
                            item = next((item for item in items if item["id"] == item_id), None)
                            if item:
                                new_qty = quantity
                                if update_type == "Add":
                                    new_qty = item["quantity"] + quantity
                                elif update_type == "Subtract":
                                    new_qty = max(0, item["quantity"] - quantity)
                                
                                st.session_state.db_manager.update_item(
                                    item_id,
                                    {"quantity": new_qty}
                                )
                        
                        st.success("✅ Items updated successfully!")
                        st.rerun()

def render_transactions_page():
    """Render the transactions page."""
    st.markdown("### 🔄 Transactions")
    
    # Get all transactions and items
    db = st.session_state.db_manager
    transactions = db.get_transactions()
    
    if not transactions:
        st.info("📝 No transactions found")
        return
    
    # Get all items to map IDs to names
    items = {item["id"]: item for item in db.get_items()}
    
    # Add filters
    col1, col2, col3 = st.columns(3)
    with col1:
        transaction_types = list(set(t["transaction_type"] for t in transactions))
        selected_type = st.selectbox(
            "Filter by Type",
            ["All"] + transaction_types,
            key="transaction_filter_type"
        )
    
    with col2:
        item_names = list(set(items[t["item_id"]]["name"] for t in transactions if t["item_id"] in items))
        selected_item = st.selectbox(
            "Filter by Item",
            ["All"] + item_names,
            key="transaction_filter_item"
        )
    
    with col3:
        date_range = st.selectbox(
            "Date Range",
            ["All Time", "Today", "Last 7 Days", "Last 30 Days", "This Month", "This Year"],
            key="transaction_filter_date"
        )
    
    # Filter transactions based on selections
    filtered_transactions = transactions
    if selected_type != "All":
        filtered_transactions = [t for t in filtered_transactions if t["transaction_type"] == selected_type]
    if selected_item != "All":
        filtered_transactions = [t for t in filtered_transactions if items[t["item_id"]]["name"] == selected_item]
    
    # Create a summary section
    st.markdown("#### 📊 Summary")
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    
    with summary_col1:
        st.metric(
            "Total Transactions",
            len(filtered_transactions),
            help="Total number of transactions in selected filters"
        )
    
    with summary_col2:
        total_value = sum(t.get("unit_price", 0) * t.get("quantity", 0) for t in filtered_transactions)
        st.metric(
            "Total Value",
            f"₱{total_value:,.2f}",
            help="Total value of all transactions"
        )
    
    with summary_col3:
        purchases = sum(t.get("quantity", 0) for t in filtered_transactions if t["transaction_type"] == "purchase")
        st.metric(
            "Items Purchased",
            purchases,
            help="Total number of items purchased"
        )
    
    with summary_col4:
        sales = sum(t.get("quantity", 0) for t in filtered_transactions if t["transaction_type"] == "sale")
        st.metric(
            "Items Sold",
            sales,
            help="Total number of items sold"
        )
    
    # Display transactions in a more organized way
    st.markdown("#### 📜 Transaction History")
    
    for transaction in filtered_transactions:
        # Get item details
        item = items.get(transaction["item_id"], {})
        item_name = item.get("name", "Unknown Item")
        
        # Format the transaction date
        created_at = datetime.fromisoformat(transaction["created_at"].replace("Z", "+00:00"))
        formatted_date = created_at.strftime("%Y-%m-%d %H:%M")
        
        # Determine transaction icon and color
        icon_map = {
            "purchase": "📥",
            "sale": "📤",
            "adjustment": "🔄"
        }
        icon = icon_map.get(transaction["transaction_type"], "📋")
        
        # Calculate total amount
        total = transaction.get("unit_price", 0) * transaction.get("quantity", 0)
        
        with st.expander(
            f"{icon} {item_name} - {transaction['transaction_type'].title()} ({formatted_date})"
        ):
            tcol1, tcol2, tcol3 = st.columns([2, 1, 1])
            
            with tcol1:
                st.write("**Type:**", transaction["transaction_type"].title())
                st.write("**Reference:**", transaction.get("reference_number", "N/A"))
            
            with tcol2:
                st.write("**Quantity:**", transaction["quantity"])
                st.write("**Unit Price:**", f"₱{transaction.get('unit_price', 0):.2f}")
            
            with tcol3:
                st.write("**Total:**", f"₱{total:.2f}")
                st.write("**Notes:**", transaction.get("notes", "N/A"))

def render_suppliers_page():
    """Render the supplier management page."""
    st.title("Supplier Management")
    
    # Add new supplier button
    if st.button("➕ Add New Supplier"):
        st.session_state.show_new_supplier_form = True
    
    # New supplier form
    if st.session_state.show_new_supplier_form:
        st.subheader("New Supplier")
        SupplierForm(handle_supplier_submit).render()
    
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
            
            with col3:
                st.write("**Actions**")
                if st.button("✏️ Edit", key=f"edit_{supplier['id']}"):
                    st.session_state.selected_supplier_id = supplier["id"]
                    SupplierForm(
                        handle_supplier_submit,
                        existing_supplier=supplier
                    ).render()
                
                if st.button("❌ Delete", key=f"delete_{supplier['id']}"):
                    if st.session_state.db_manager.delete_supplier(supplier["id"]):
                        st.success("Supplier deleted successfully!")
                        st.experimental_rerun()
                    else:
                        st.error("Failed to delete supplier")

def render_analytics_page():
    """Render the analytics page."""
    st.title("Analytics")
    analytics = st.session_state.analytics_manager
    
    # Render all analytics components
    analytics.create_inventory_value_chart()
    analytics.create_transaction_trend_chart()
    
    # Category distribution
    st.subheader("Category Distribution")
    categories = analytics.get_category_distribution()
    
    for category in categories:
        st.write(
            f"{category['category']}: {category['item_count']} items, "
            f"Total Value: ₱{category['total_value']:,.2f}"
        )

def export_data_to_csv():
    """Export inventory data to CSV format."""
    try:
        import pandas as pd
        from io import StringIO
        
        db = st.session_state.db_manager
        
        # Get all data
        items = pd.DataFrame(db.get_items())
        transactions = pd.DataFrame(db.get_transactions())
        suppliers = pd.DataFrame(db.get_suppliers())
        
        # Create a buffer to store the CSV data
        buffer = StringIO()
        
        # Write each table to the buffer with headers
        buffer.write("# Items\n")
        if not items.empty:
            items.to_csv(buffer, index=False)
        buffer.write("\n\n# Transactions\n")
        if not transactions.empty:
            transactions.to_csv(buffer, index=False)
        buffer.write("\n\n# Suppliers\n")
        if not suppliers.empty:
            suppliers.to_csv(buffer, index=False)
        
        return buffer.getvalue()
    except Exception as e:
        st.error(f"❌ Error exporting data: {str(e)}")
        return None

def render_settings_page():
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
    """Main application entry point."""
    # Initialize managers
    initialize_managers()
    
    # Render sidebar
    filters = Sidebar.render(handle_page_change, st.session_state.page)
    
    # Render main content
    if st.session_state.page == "dashboard":
        Dashboard(st.session_state.analytics_manager).render()
    elif st.session_state.page == "inventory":
        render_inventory_page()
    elif st.session_state.page == "suppliers":
        render_suppliers_page()
    elif st.session_state.page == "transactions":
        render_transactions_page()
    elif st.session_state.page == "analytics":
        render_analytics_page()
    elif st.session_state.page == "settings":
        render_settings_page()
    
    # Handle transaction form
    if st.session_state.show_new_transaction_form and st.session_state.selected_item_id:
        st.subheader("New Transaction")
        item = st.session_state.db_manager.get_item(
            st.session_state.selected_item_id
        )
        if item:
            # Get all items for the transaction form
            items = st.session_state.db_manager.get_items()
            
            # Create and render the transaction form
            form = TransactionForm()
            result = form.render(items)
            
            # Handle form submission
            if result:
                handle_transaction_submit(result)

if __name__ == "__main__":
    main()
