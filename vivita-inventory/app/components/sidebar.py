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
                "suppliers": "🏢 Suppliers",
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
            
            # Filters section
            if current_page in ["inventory", "analytics"]:
                st.markdown("---")
                st.subheader("Filters")
                filters = {}
                
                # Category filter
                filters["category"] = st.multiselect(
                    "Categories",
                    options=[e.value for e in CategoryType],
                    default=[]
                )
                
                # Status filter
                filters["status"] = st.multiselect(
                    "Status",
                    ["In Stock", "Low Stock", "Out of Stock"],
                    default=[]
                )
                
                return filters
            
            elif current_page == "transactions":
                st.markdown("---")
                st.subheader("Filters")
                filters = {}
                
                # Transaction type filter
                filters["transaction_type"] = st.multiselect(
                    "Transaction Types",
                    [e.value for e in TransactionType],
                    default=[]
                )
                
                return filters
            
            return {}
