"""Sidebar component for navigation and filters."""

from typing import Callable, Dict, List, Optional
import streamlit as st

from ..utils.constants import CategoryType, TransactionType

class Sidebar:
    """Sidebar component for the inventory management system."""
    
    @staticmethod
    def render(
        on_page_change: Callable[[str], None],
        current_page: str
    ) -> Dict[str, any]:
        """Render the sidebar with navigation and filters."""
        with st.sidebar:
            st.title("Vivita Inventory")
            
            # Navigation
            st.subheader("Navigation")
            pages = {
                "dashboard": "📊 Dashboard",
                "inventory": "📦 Inventory",
                "transactions": "💰 Transactions",
                "analytics": "📈 Analytics",
                "settings": "⚙️ Settings"
            }
            
            selected_page = st.radio(
                "Go to",
                options=list(pages.keys()),
                format_func=lambda x: pages[x],
                index=list(pages.keys()).index(current_page)
            )
            
            if selected_page != current_page:
                on_page_change(selected_page)
            
            # Filters
            st.subheader("Filters")
            filters = {}
            
            if current_page in ["inventory", "analytics"]:
                # Category filter
                filters["category"] = st.multiselect(
                    "Categories",
                    options=[e.value for e in CategoryType],
                    default=[]
                )
                
                # Stock level filter
                filters["stock_level"] = st.radio(
                    "Stock Level",
                    options=["All", "Low Stock", "Out of Stock"],
                    index=0
                )
                
                # Active/Inactive filter
                filters["status"] = st.radio(
                    "Status",
                    options=["All", "Active", "Inactive"],
                    index=0
                )
            
            elif current_page == "transactions":
                # Transaction type filter
                filters["transaction_type"] = st.multiselect(
                    "Transaction Types",
                    options=[e.value for e in TransactionType],
                    default=[]
                )
                
                # Date range filter
                filters["date_range"] = st.radio(
                    "Date Range",
                    options=[
                        "Today",
                        "Yesterday",
                        "Last 7 Days",
                        "Last 30 Days",
                        "This Month",
                        "Custom"
                    ],
                    index=2
                )
                
                if filters["date_range"] == "Custom":
                    filters["start_date"] = st.date_input("Start Date")
                    filters["end_date"] = st.date_input("End Date")
            
            # Export button
            if current_page in ["inventory", "transactions"]:
                st.subheader("Export")
                export_format = st.selectbox(
                    "Format",
                    options=["CSV", "Excel"],
                    index=0
                )
                
                if st.button("Export Data"):
                    filters["export"] = {
                        "format": export_format.lower(),
                        "timestamp": True
                    }
            
            return filters

    @staticmethod
    def render_quick_actions():
        """Render quick action buttons in the sidebar."""
        with st.sidebar:
            st.subheader("Quick Actions")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("➕ New Item"):
                    st.session_state["show_new_item_form"] = True
            
            with col2:
                if st.button("📝 New Transaction"):
                    st.session_state["show_new_transaction_form"] = True
            
            # Alert summary
            st.subheader("Alerts")
            alert_count = st.session_state.get("alert_count", 0)
            
            if alert_count > 0:
                st.warning(f"🚨 {alert_count} items need attention")
            else:
                st.success("✅ No alerts")
