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
        """Render summary metrics in cards."""
        summary = self.analytics.get_inventory_summary()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Items",
                f"{summary['total_items']:,}",
                help="Total number of unique items in inventory"
            )
        
        with col2:
            st.metric(
                "Total Value",
                format_currency(summary['total_value']),
                help="Total value of current inventory"
            )
        
        with col3:
            st.metric(
                "Avg Unit Cost",
                format_currency(summary['avg_unit_cost']),
                help="Average cost per unit across all items"
            )
        
        with col4:
            st.metric(
                "Low Stock Items",
                f"{summary['low_stock_count']:,}",
                help="Number of items below minimum quantity"
            )

    def render_stock_alerts(self):
        """Render stock alerts section."""
        alerts = self.analytics.get_stock_alerts()
        
        st.subheader("Stock Alerts")
        
        if not alerts:
            st.success("No items require attention")
            return
        
        for alert in alerts:
            with st.expander(f"🚨 {alert['name']} - Current: {alert['current_quantity']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Minimum Quantity:**", alert['min_quantity'])
                    st.write("**Shortage:**", alert['shortage'])
                
                with col2:
                    st.write("**Last Ordered:**", alert['last_ordered'])
                    if st.button("Order More", key=f"order_{alert['id']}"):
                        st.session_state["show_new_transaction_form"] = True
                        st.session_state["selected_item_id"] = alert['id']

    def render_transaction_chart(self):
        """Render transaction trend chart."""
        st.subheader("Transaction Trends")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            chart = self.analytics.create_transaction_trend_chart()
            st.plotly_chart(chart, use_container_width=True)
        
        with col2:
            trends = self.analytics.get_transaction_trends()
            
            # Transaction type distribution
            st.write("**Transaction Types**")
            for t_type in trends["transaction_types"]:
                st.write(
                    f"{t_type['type']}: {t_type['count']:,}"
                )

    def render_category_analysis(self):
        """Render category analysis section."""
        st.subheader("Category Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Category distribution chart
            chart = self.analytics.create_inventory_value_chart()
            st.plotly_chart(chart, use_container_width=True)
        
        with col2:
            # Category metrics
            categories = self.analytics.get_category_distribution()
            
            for category in categories:
                with st.expander(f"📊 {category['category']}"):
                    st.write("**Items:**", f"{category['item_count']:,}")
                    st.write(
                        "**Total Quantity:**",
                        f"{category['total_quantity']:,}"
                    )
                    st.write(
                        "**Total Value:**",
                        format_currency(category['total_value'])
                    )

    def render_inventory_table(self, inventory_data):
        """Render the inventory table with data."""
        # Create a DataFrame for display
        data = []
        for item in inventory_data:
            # Add select button
            if st.button("Select", key=f"select_{item['id']}"):
                st.session_state.selected_item = item
                st.session_state.current_page = "transactions"
                st.experimental_rerun()

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
        st.title("Dashboard")
        
        # Summary metrics
        self.render_summary_metrics()
        
        # Stock alerts
        self.render_stock_alerts()
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            self.render_transaction_chart()
        
        with col2:
            self.render_category_analysis()
