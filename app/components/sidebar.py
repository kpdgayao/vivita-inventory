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
            
            # Add version info at the bottom
            st.sidebar.markdown("---")
            st.sidebar.markdown("v1.0.0")
            
            return {}
