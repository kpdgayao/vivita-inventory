"""Analytics manager for processing and analyzing inventory data."""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from app.database.supabase_manager import SupabaseManager

class AnalyticsManager:
    """Manages analytics and data processing for inventory system."""

    def __init__(self, db_manager: SupabaseManager):
        """Initialize with database manager."""
        self.db = db_manager

    def get_inventory_summary(self) -> Dict[str, Any]:
        """Get summary statistics of current inventory."""
        items = self.db.get_items()
        df = pd.DataFrame(items)
        
        if df.empty:
            return {
                "total_items": 0,
                "total_value": 0,
                "avg_unit_cost": 0,
                "low_stock_count": 0
            }

        return {
            "total_items": len(df),
            "total_value": (df["quantity"] * df["unit_cost"]).sum(),
            "avg_unit_cost": df["unit_cost"].mean(),
            "low_stock_count": len(df[df["quantity"] <= df["min_quantity"]])
        }

    def get_transaction_trends(
        self,
        days: int = 30
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get transaction trends for specified period."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        transactions = self.db.get_transactions(
            start_date=start_date,
            end_date=end_date
        )
        
        df = pd.DataFrame(transactions)
        if df.empty:
            return {"daily_transactions": [], "transaction_types": []}

        # Daily transaction counts
        daily_counts = df.groupby(
            pd.to_datetime(df["created_at"]).dt.date
        ).size().reset_index()
        daily_counts.columns = ["date", "count"]
        
        # Transaction types distribution
        type_counts = df["transaction_type"].value_counts().reset_index()
        type_counts.columns = ["type", "count"]

        return {
            "daily_transactions": daily_counts.to_dict("records"),
            "transaction_types": type_counts.to_dict("records")
        }

    def get_category_distribution(self) -> List[Dict[str, Any]]:
        """Get distribution of items across categories."""
        items = self.db.get_items()
        df = pd.DataFrame(items)
        
        if df.empty:
            return []

        category_counts = df.groupby("category").agg({
            "id": "count",
            "quantity": "sum",
            "unit_cost": lambda x: (x * df["quantity"]).sum()
        }).reset_index()
        
        category_counts.columns = [
            "category", "item_count", "total_quantity", "total_value"
        ]
        
        return category_counts.to_dict("records")

    def create_inventory_value_chart(self) -> go.Figure:
        """Create a bar chart of inventory value by category."""
        category_data = self.get_category_distribution()
        df = pd.DataFrame(category_data)
        
        if df.empty:
            return go.Figure()

        fig = px.bar(
            df,
            x="category",
            y="total_value",
            title="Inventory Value by Category",
            labels={"total_value": "Total Value ($)", "category": "Category"}
        )
        
        return fig

    def create_transaction_trend_chart(self, days: int = 30) -> go.Figure:
        """Create a line chart of transaction trends."""
        trends = self.get_transaction_trends(days)
        df = pd.DataFrame(trends["daily_transactions"])
        
        if df.empty:
            return go.Figure()

        fig = px.line(
            df,
            x="date",
            y="count",
            title=f"Transaction Trends (Last {days} Days)",
            labels={"count": "Number of Transactions", "date": "Date"}
        )
        
        return fig

    def get_stock_alerts(self) -> List[Dict[str, Any]]:
        """Get list of items requiring attention."""
        low_stock_items = self.db.get_low_stock_items()
        df = pd.DataFrame(low_stock_items)
        
        if df.empty:
            return []

        alerts = []
        for _, item in df.iterrows():
            alerts.append({
                "id": item["id"],
                "name": item["name"],
                "current_quantity": item["quantity"],
                "min_quantity": item["min_quantity"],
                "shortage": item["min_quantity"] - item["quantity"],
                "last_ordered": item["last_ordered_at"]
            })
        
        return alerts
