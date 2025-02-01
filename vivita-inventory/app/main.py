"""Main application file for the Vivita Inventory Management System."""

import os
from typing import Dict, Any
import streamlit as st
from dotenv import load_dotenv

from database.supabase_manager import SupabaseManager
from analytics.analytics_manager import AnalyticsManager
from components.dashboard import Dashboard
from components.sidebar import Sidebar
from components.forms import ItemForm, TransactionForm

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Vivita Inventory",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "dashboard"
if "show_new_item_form" not in st.session_state:
    st.session_state.show_new_item_form = False
if "show_new_transaction_form" not in st.session_state:
    st.session_state.show_new_transaction_form = False
if "selected_item_id" not in st.session_state:
    st.session_state.selected_item_id = None

def initialize_managers():
    """Initialize database and analytics managers."""
    db_manager = SupabaseManager()
    analytics_manager = AnalyticsManager(db_manager)
    return db_manager, analytics_manager

def handle_page_change(new_page: str):
    """Handle page navigation."""
    st.session_state.page = new_page
    st.experimental_rerun()

def handle_item_submit(item_data: Dict[str, Any]):
    """Handle item form submission."""
    db = st.session_state.db_manager
    
    if "id" in item_data:
        # Update existing item
        result = db.update_item(item_data["id"], item_data)
        if result:
            st.success("Item updated successfully!")
        else:
            st.error("Failed to update item")
    else:
        # Create new item
        result = db.create_item(item_data)
        if result:
            st.success("Item created successfully!")
            st.session_state.show_new_item_form = False
        else:
            st.error("Failed to create item")

def handle_transaction_submit(transaction_data: Dict[str, Any]):
    """Handle transaction form submission."""
    db = st.session_state.db_manager
    result = db.create_transaction(transaction_data)
    
    if result:
        st.success("Transaction created successfully!")
        st.session_state.show_new_transaction_form = False
    else:
        st.error("Failed to create transaction")

def render_inventory_page():
    """Render the inventory management page."""
    st.title("Inventory Management")
    
    # Add new item button
    if st.button("➕ Add New Item"):
        st.session_state.show_new_item_form = True
    
    # New item form
    if st.session_state.show_new_item_form:
        st.subheader("New Item")
        ItemForm(handle_item_submit).render()
    
    # Item list
    items = st.session_state.db_manager.get_items()
    
    if not items:
        st.info("No items found. Add your first item!")
        return
    
    for item in items:
        with st.expander(f"{item['name']} ({item['sku']})"):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write("**Description:**", item["description"])
                st.write("**Category:**", item["category"])
            
            with col2:
                st.write("**Quantity:**", item["quantity"])
                st.write("**Unit Cost:**", f"${item['unit_cost']:.2f}")
            
            with col3:
                if st.button("📝 Edit", key=f"edit_{item['id']}"):
                    st.session_state.selected_item_id = item["id"]
                    ItemForm(
                        handle_item_submit,
                        existing_item=item
                    ).render()
                
                if st.button("🔄 New Transaction", key=f"trans_{item['id']}"):
                    st.session_state.show_new_transaction_form = True
                    st.session_state.selected_item_id = item["id"]

def render_transactions_page():
    """Render the transactions page."""
    st.title("Transactions")
    
    # Transaction list
    transactions = st.session_state.db_manager.get_transactions()
    
    if not transactions:
        st.info("No transactions found")
        return
    
    for transaction in transactions:
        with st.expander(
            f"{transaction['transaction_type']} - {transaction['created_at']}"
        ):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Item ID:**", transaction["item_id"])
                st.write("**Quantity:**", transaction["quantity"])
            
            with col2:
                st.write(
                    "**Unit Price:**",
                    f"${transaction['unit_price']:.2f}"
                )
                st.write(
                    "**Total Amount:**",
                    f"${transaction['total_amount']:.2f}"
                )
            
            if transaction["notes"]:
                st.write("**Notes:**", transaction["notes"])

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
            f"Total Value: ${category['total_value']:,.2f}"
        )

def render_settings_page():
    """Render the settings page."""
    st.title("Settings")
    
    # User preferences
    st.subheader("User Preferences")
    st.selectbox(
        "Default View",
        options=["Dashboard", "Inventory", "Transactions"]
    )
    st.checkbox("Enable Notifications")
    st.number_input("Items per Page", min_value=10, max_value=100, value=20)
    
    # Export/Import
    st.subheader("Data Management")
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            "Export Data",
            data="",  # TODO: Implement data export
            file_name="inventory_export.csv"
        )
    
    with col2:
        st.file_uploader("Import Data", type=["csv"])

def main():
    """Main application entry point."""
    # Initialize managers
    if "db_manager" not in st.session_state:
        db_manager, analytics_manager = initialize_managers()
        st.session_state.db_manager = db_manager
        st.session_state.analytics_manager = analytics_manager
    
    # Render sidebar
    filters = Sidebar.render(handle_page_change, st.session_state.page)
    Sidebar.render_quick_actions()
    
    # Render main content
    if st.session_state.page == "dashboard":
        Dashboard(st.session_state.analytics_manager).render()
    elif st.session_state.page == "inventory":
        render_inventory_page()
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
            TransactionForm(
                handle_transaction_submit,
                item["id"],
                item["quantity"]
            ).render()

if __name__ == "__main__":
    main()
