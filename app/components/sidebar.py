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
            st.markdown(
                """
                <style>
                div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"] button {
                    width: 100%;
                    text-align: left !important;
                }
                div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"] button p {
                    text-align: left !important;
                }
                </style>
                """,
                unsafe_allow_html=True
            )
            
            st.subheader("Navigation")
            pages = {
                "dashboard": "📊 Dashboard",
                "inventory": "📦 Inventory",
                "suppliers": "🏢 Suppliers",
                "transactions": "💰 Transactions",
                "analytics": "📈 Analytics",
                "settings": "⚙️ Settings"
            }
            
            # Initialize navigation state
            if "nav_page" not in st.session_state:
                st.session_state.nav_page = current_page
            
            # Create navigation buttons
            for page_key, page_label in pages.items():
                col1, col2 = st.columns([0.1, 0.9])
                with col2:
                    if page_key == st.session_state.nav_page:
                        st.markdown(f"**→ {page_label}**")
                    else:
                        if st.button(
                            page_label,
                            key=f"nav_{page_key}",
                            use_container_width=True,
                            on_click=lambda p=page_key: Sidebar._handle_nav_click(p)
                        ):
                            pass  # Button click is handled by on_click
            
            # If navigation state changed, trigger page change
            if st.session_state.nav_page != current_page:
                on_page_change(st.session_state.nav_page)
            
            # Add version info at the bottom
            st.sidebar.markdown("---")
            st.sidebar.markdown("v1.0.0")
            
            return {}
    
    @staticmethod
    def _handle_nav_click(page: str):
        """Handle navigation button click."""
        st.session_state.nav_page = page
