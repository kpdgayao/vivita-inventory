"""Inventory management component for displaying and managing inventory items."""

from typing import Dict, Any, Optional, List, Callable
import streamlit as st
import pandas as pd
import datetime

from ..utils.constants import CategoryType, UnitType
from ..utils.helpers import format_currency, format_timestamp
from .ui_components import DataTable, StatusBadge, NotificationManager, FormValidator

class InventoryManager:
    """Inventory management component for the system."""
    
    def __init__(self, db_manager):
        """Initialize inventory manager with database manager.
        
        Args:
            db_manager: Database manager instance for data operations
        """
        self.db_manager = db_manager
        self.notifications = NotificationManager()
        
        # Initialize callbacks
        self.on_edit = None
        self.on_delete = None
        self.on_add = None
        
        # Initialize state
        if "inventory_view" not in st.session_state:
            st.session_state.inventory_view = "grid"
            
        if "inventory_filters" not in st.session_state:
            st.session_state.inventory_filters = {
                "category": None,
                "status": None,
                "search": "",
                "sort_by": "name",
                "sort_order": "asc"
            }
    
    def render(self, 
               on_edit: Callable[[Dict[str, Any]], None],
               on_delete: Callable[[str], None],
               on_add: Callable[[], None]):
        """Render the inventory management interface.
        
        Args:
            on_edit: Callback for editing an item
            on_delete: Callback for deleting an item
            on_add: Callback for adding a new item
        """
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_add = on_add
        
        st.markdown("## 📦 Inventory Management")
        
        # Render action buttons and filters
        self._render_actions_and_filters()
        
        # Get filtered inventory data
        try:
            inventory_data = self._get_filtered_inventory()
            
            # Render inventory based on selected view
            if st.session_state.inventory_view == "grid":
                self._render_grid_view(inventory_data)
            else:
                self._render_table_view(inventory_data)
                
        except Exception as e:
            self.notifications.error(f"Error loading inventory data: {str(e)}")
            st.error(f"Failed to load inventory data: {str(e)}")
    
    def _render_actions_and_filters(self):
        """Render action buttons and filter controls."""
        # Action buttons and view toggle
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("➕ Add New Item", use_container_width=True):
                self.on_add()
                
        with col2:
            # View toggle
            view_options = {
                "grid": "Grid View",
                "table": "Table View"
            }
            
            selected_view = st.selectbox(
                "View",
                options=list(view_options.keys()),
                format_func=lambda x: view_options[x],
                index=0 if st.session_state.inventory_view == "grid" else 1,
                key="inventory_view_toggle"
            )
            
            if selected_view != st.session_state.inventory_view:
                st.session_state.inventory_view = selected_view
                st.rerun()
        
        with col3:
            # Search box
            search_query = st.text_input(
                "Search Items",
                value=st.session_state.inventory_filters.get("search", ""),
                placeholder="Search by name, SKU, or description...",
                key="inventory_search"
            )
            
            if search_query != st.session_state.inventory_filters.get("search", ""):
                st.session_state.inventory_filters["search"] = search_query
        
        # Filter controls
        st.markdown("### Filters")
        filter_cols = st.columns(4)
        
        with filter_cols[0]:
            # Category filter
            categories = [None, *list(CategoryType.__members__.keys())]
            selected_category = st.selectbox(
                "Category",
                options=categories,
                format_func=lambda x: "All Categories" if x is None else x.replace("_", " ").title(),
                index=0,
                key="inventory_category_filter"
            )
            
            if selected_category != st.session_state.inventory_filters.get("category"):
                st.session_state.inventory_filters["category"] = selected_category
        
        with filter_cols[1]:
            # Status filter
            statuses = [None, "low", "normal", "high", "out_of_stock"]
            selected_status = st.selectbox(
                "Stock Status",
                options=statuses,
                format_func=lambda x: "All Statuses" if x is None else x.replace("_", " ").title(),
                index=0,
                key="inventory_status_filter"
            )
            
            if selected_status != st.session_state.inventory_filters.get("status"):
                st.session_state.inventory_filters["status"] = selected_status
        
        with filter_cols[2]:
            # Sort by
            sort_options = {
                "name": "Name",
                "sku": "SKU",
                "category": "Category",
                "quantity": "Quantity",
                "price": "Price",
                "last_updated": "Last Updated"
            }
            
            selected_sort = st.selectbox(
                "Sort By",
                options=list(sort_options.keys()),
                format_func=lambda x: sort_options[x],
                index=0,
                key="inventory_sort_by"
            )
            
            if selected_sort != st.session_state.inventory_filters.get("sort_by"):
                st.session_state.inventory_filters["sort_by"] = selected_sort
        
        with filter_cols[3]:
            # Sort order
            sort_order_options = {
                "asc": "Ascending",
                "desc": "Descending"
            }
            
            selected_order = st.selectbox(
                "Sort Order",
                options=list(sort_order_options.keys()),
                format_func=lambda x: sort_order_options[x],
                index=0,
                key="inventory_sort_order"
            )
            
            if selected_order != st.session_state.inventory_filters.get("sort_order"):
                st.session_state.inventory_filters["sort_order"] = selected_order
    
    def _get_filtered_inventory(self) -> List[Dict[str, Any]]:
        """Get filtered inventory data based on current filters.
        
        Returns:
            List of inventory items after applying filters
        """
        # In a real implementation, this would query the database with filters
        # For now, we'll simulate this with a placeholder
        
        # Get all inventory items from the database
        items = self.db_manager.get_items()
        
        # Apply filters
        filtered_items = items
        filters = st.session_state.inventory_filters
        
        # Apply category filter
        if filters.get("category"):
            filtered_items = [item for item in filtered_items 
                             if item.get("category") == filters["category"]]
        
        # Apply status filter
        if filters.get("status"):
            filtered_items = [item for item in filtered_items 
                             if item.get("status") == filters["status"]]
        
        # Apply search filter
        if filters.get("search"):
            search_query = str(filters["search"]).lower()
            filtered_items = [item for item in filtered_items 
                             if (search_query in str(item.get("name", "")).lower() or
                                search_query in str(item.get("sku", "")).lower() or
                                search_query in str(item.get("description", "")).lower())]
        
        # Apply sorting
        sort_by = filters.get("sort_by", "name")
        sort_order = filters.get("sort_order", "asc")
        
        # Handle None values for sorting
        filtered_items = sorted(
            filtered_items,
            key=lambda x: (x.get(sort_by) is None, x.get(sort_by, "")),
            reverse=(sort_order == "desc")
        )
        
        return filtered_items
    
    def _render_grid_view(self, items: List[Dict[str, Any]]):
        """Render inventory items in a grid view.
        
        Args:
            items: List of inventory items to display
        """
        if not items:
            st.info("No inventory items found matching your filters.")
            return
        
        # Display items in a grid layout with 3 columns
        cols_per_row = 3
        rows = [items[i:i + cols_per_row] for i in range(0, len(items), cols_per_row)]
        
        for row in rows:
            cols = st.columns(cols_per_row)
            
            for i, item in enumerate(row):
                with cols[i]:
                    self._render_item_card(item)
    
    def _render_item_card(self, item: Dict[str, Any]):
        """Render a single item card for grid view.
        
        Args:
            item: Item data to display
        """
        # Card container with styling
        st.markdown(
            f"""
            <div style="
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 16px;
                margin-bottom: 16px;
                background-color: white;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            ">
                <h3 style="margin-top: 0; margin-bottom: 8px;">{item.get('name', 'Unnamed Item')}</h3>
                <p style="color: #666; margin-bottom: 8px; font-size: 0.9em;">SKU: {item.get('sku', 'N/A')}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Item details
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Category:** {item.get('category', 'N/A').replace('_', ' ').title()}")
            st.markdown(f"**Price:** {format_currency(item.get('price', 0))}")
        
        with col2:
            st.markdown(f"**Quantity:** {item.get('quantity', 0)} {item.get('unit_type', 'units')}")
            StatusBadge.render(item.get('status', 'normal'))
        
        # Action buttons
        action_cols = st.columns(2)
        with action_cols[0]:
            if st.button("✏️ Edit", key=f"edit_{item.get('id')}", use_container_width=True):
                self.on_edit(item)
        
        with action_cols[1]:
            if st.button("🗑️ Delete", key=f"delete_{item.get('id')}", use_container_width=True):
                self.on_delete(item.get('id'))
    
    def _render_table_view(self, items: List[Dict[str, Any]]):
        """Render inventory items in a table view.
        
        Args:
            items: List of inventory items to display
        """
        if not items:
            st.info("No inventory items found matching your filters.")
            return
        
        # Define columns for the data table
        columns = [
            {"field": "name", "label": "Name"},
            {"field": "sku", "label": "SKU"},
            {"field": "category", "label": "Category"},
            {"field": "quantity", "label": "Quantity"},
            {"field": "unit_type", "label": "Unit"},
            {"field": "price", "label": "Price", "format": "currency"},
            {"field": "status", "label": "Status"},
            {"field": "last_updated", "label": "Last Updated", "format": "timestamp"}
        ]
        
        # Define actions for the table
        actions = [
            {"label": "Edit", "icon": "✏️", "callback": self.on_edit},
            {"label": "Delete", "icon": "🗑️", "callback": self.on_delete}
        ]
        
        # Format data for display
        for item in items:
            # Format category for display
            if "category" in item:
                item["category"] = item["category"].replace("_", " ").title()
            
            # Format status for display
            if "status" in item:
                status = item["status"]
                item["status"] = StatusBadge.render(status)
        
        # Render the data table
        DataTable.render(
            data=items,
            columns=columns,
            key="inventory_table",
            actions=actions,
            pagination=True,
            items_per_page=10,
            searchable=False,  # We already have a search box above
            empty_message="No inventory items found matching your filters."
        )
