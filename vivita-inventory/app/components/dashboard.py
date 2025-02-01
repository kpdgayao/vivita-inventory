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
