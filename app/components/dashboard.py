"""Dashboard component for displaying inventory overview and metrics."""

from typing import Dict, Any
import streamlit as st
import plotly.graph_objects as go

from ..analytics.analytics_manager import AnalyticsManager
from ..utils.helpers import format_currency

class Dashboard:
    """Dashboard component for the inventory management system."""
    
    def __init__(self, analytics_manager: AnalyticsManager):
        """Initialize dashboard with analytics manager."""
        self.analytics = analytics_manager

    def render_summary_metrics(self):
        """Render key summary metrics."""
        summary = self.analytics.get_inventory_summary()
        
        # Create two main columns for the overview
        left_col, right_col = st.columns([2, 1])
        
        with left_col:
            st.markdown("### 📊 Key Metrics")
            
            # Only show the most important metrics
            metric_cols = st.columns(3)
            with metric_cols[0]:
                st.metric(
                    "Total Items",
                    f"{summary['total_items']:,}",
                    help="Total unique items"
                )
            
            with metric_cols[1]:
                st.metric(
                    "Total Value",
                    format_currency(summary['total_value']),
                    help="Current inventory value"
                )
            
            with metric_cols[2]:
                st.metric(
                    "Low Stock Items",
                    f"{summary['low_stock_count']:,}",
                    help="Items needing attention",
                    delta=summary['low_stock_count'] if summary['low_stock_count'] > 0 else None,
                    delta_color="inverse"
                )
        
        with right_col:
            st.markdown("### ⚡ Quick Actions")
            col1, col2 = st.columns(2)
            with col1:
                st.button(
                    "➕ New Item",
                    key="quick_new_item",
                    use_container_width=True,
                    on_click=self._handle_new_item_click
                )
            with col2:
                st.button(
                    "🔄 New Transaction",
                    key="quick_new_transaction",
                    use_container_width=True,
                    on_click=self._handle_new_transaction_click
                )

    def render_stock_alerts(self):
        """Render critical stock alerts."""
        alerts = self.analytics.get_stock_alerts()
        
        if not alerts:
            return
        
        st.markdown("### 🚨 Critical Items")
        
        critical_items = sorted(
            alerts,
            key=lambda x: (x['quantity'] / x['min_quantity']) if x['min_quantity'] > 0 else float('inf')
        )[:5]
        
        for alert in critical_items:
            shortage_percent = ((alert['min_quantity'] - alert['quantity']) / alert['min_quantity'] * 100) if alert['min_quantity'] > 0 else 0
            with st.expander(
                f"⚠️ {alert['name']} ({alert['quantity']} {alert['unit_type']} of {alert['min_quantity']} min)",
                expanded=True
            ):
                cols = st.columns([3, 1])
                with cols[0]:
                    progress = min(1.0, alert['quantity'] / alert['min_quantity']) if alert['min_quantity'] > 0 else 0
                    st.progress(
                        progress,
                        text=f"Stock Level: {shortage_percent:.1f}% below minimum"
                    )
                
                with cols[1]:
                    st.button(
                        "📦 Order",
                        key=f"order_{alert['id']}",
                        use_container_width=True,
                        on_click=self._handle_order_click,
                        args=(alert['id'],)
                    )

    def _handle_new_item_click(self):
        """Handle new item button click."""
        # Initialize all required session state variables
        st.session_state.show_new_item_form = True
        st.session_state.editing_item = None
        st.session_state.quick_update_item = None
        st.session_state.selected_item_id = None
        st.session_state.nav_page = "inventory"

    def _handle_new_transaction_click(self):
        """Handle new transaction button click."""
        # Initialize all required session state variables
        st.session_state.show_new_transaction_form = True
        st.session_state.selected_item_id = None
        st.session_state.editing_item = None
        st.session_state.nav_page = "transactions"

    def _handle_order_click(self, item_id: str):
        """Handle order button click."""
        # Initialize all required session state variables
        st.session_state["show_new_transaction_form"] = True
        st.session_state["selected_item_id"] = item_id
        st.session_state["default_transaction_type"] = "purchase"
        st.session_state.editing_item = None
        st.session_state.nav_page = "transactions"

    def render_transaction_chart(self):
        """Render simplified transaction trends."""
        st.markdown("### 📈 Recent Activity")
        
        # Create tabs for different views
        tab1, tab2 = st.tabs(["📊 Overview", "📋 Recent Transactions"])
        
        with tab1:
            # Show only the chart with last 7 days of data
            chart = self.analytics.create_transaction_trend_chart(days=7)
            st.plotly_chart(chart, use_container_width=True)
        
        with tab2:
            # Show only the 5 most recent transactions
            transactions = self.analytics.get_recent_transactions(limit=5)
            if transactions:
                for t in transactions:
                    with st.container():
                        cols = st.columns([1, 2, 1])
                        with cols[0]:
                            icon = "📥" if t['transaction_type'] == "purchase" else "📤"
                            st.markdown(f"{icon} **{t['transaction_type'].title()}**")
                        with cols[1]:
                            st.markdown(f"**{t['item_name']}**: {t['quantity']} units @ {format_currency(t['unit_price'])}")
                        with cols[2]:
                            st.markdown(f"{t['created_at']}")  # Date is already formatted
            else:
                st.info("No recent transactions")

    def render_category_analysis(self):
        """Render simplified category analysis."""
        # Only show this if there's more than one category
        categories = self.analytics.get_category_distribution()
        if len(categories) <= 1:
            return
        
        st.markdown("### 📊 Category Overview")
        chart = self.analytics.create_inventory_value_chart()
        st.plotly_chart(chart, use_container_width=True)

    def render_inventory_table(self, inventory_data):
        """Render the inventory table with data."""
        # Create a DataFrame for display
        data = []
        for item in inventory_data:
            # Add select button
            if st.button("Select", key=f"select_{item['id']}"):
                pass  # Removed state handling

            data.append({
                "Name": item["name"],
                "Category": item["category"],
                "SKU": item["sku"] or "",
                "Quantity": item["quantity"],
                "Min Qty": item["min_quantity"],
                "Unit Cost": format_currency(item["unit_cost"]),
                "Total Value": format_currency(item["quantity"] * item["unit_cost"]),
                "Status": "⚠️ Low Stock" if item["quantity"] <= item["min_quantity"] else "✅ In Stock",
                "Actions": f"select_{item['id']}"  # Reference to the select button
            })
        
        # Display the table
        st.dataframe(
            data,
            column_config={
                "Name": st.column_config.TextColumn("Name", width="medium"),
                "Category": st.column_config.TextColumn("Category", width="small"),
                "SKU": st.column_config.TextColumn("SKU", width="small"),
                "Quantity": st.column_config.NumberColumn("Quantity", width="small"),
                "Min Qty": st.column_config.NumberColumn("Min Qty", width="small"),
                "Unit Cost": st.column_config.TextColumn("Unit Cost", width="small"),
                "Total Value": st.column_config.TextColumn("Total Value", width="small"),
                "Status": st.column_config.TextColumn("Status", width="small"),
                "Actions": st.column_config.Column("Actions", width="small")
            },
            hide_index=True,
            use_container_width=True
        )

    def render_transactions_table(self, transactions):
        """Render the transactions table."""
        # Create a DataFrame for display
        data = []
        for transaction in transactions:
            data.append({
                "Date": transaction["created_at"].split("T")[0],
                "Type": transaction["transaction_type"].title(),
                "Quantity": transaction["quantity"],
                "Unit Price": format_currency(transaction["unit_price"]),
                "Total": format_currency(transaction["quantity"] * transaction["unit_price"]),
                "Reference": transaction["reference_number"] or "-",
                "Notes": transaction["notes"] or "-"
            })
        
        # Display the table
        st.dataframe(
            data,
            column_config={
                "Date": st.column_config.TextColumn("Date", width="small"),
                "Type": st.column_config.TextColumn("Type", width="small"),
                "Quantity": st.column_config.NumberColumn("Quantity", width="small"),
                "Unit Price": st.column_config.TextColumn("Unit Price", width="small"),
                "Total": st.column_config.TextColumn("Total", width="small"),
                "Reference": st.column_config.TextColumn("Reference", width="medium"),
                "Notes": st.column_config.TextColumn("Notes", width="medium")
            },
            hide_index=True,
            use_container_width=True
        )

    def render(self):
        """Render the complete dashboard."""
        st.markdown("# 🏠 Dashboard")
        
        # 1. Key Metrics and Quick Actions
        self.render_summary_metrics()
        
        # 2. Critical Items (if any)
        self.render_stock_alerts()
        
        # 3. Recent Activity
        self.render_transaction_chart()
        
        # 4. Category Analysis (if enough data)
        self.render_category_analysis()

        # Handle navigation if needed
        if hasattr(st.session_state, 'nav_page') and st.session_state.nav_page != "dashboard":
            st.session_state.page = st.session_state.nav_page
