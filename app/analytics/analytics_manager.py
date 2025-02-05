"""Analytics manager for processing and analyzing inventory data."""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from decimal import Decimal

from app.database.supabase_manager import SupabaseManager

def calculate_total_value(items, transactions):
    """Calculate the total value of items using weighted average cost."""
    total_value = Decimal(0)
    
    # Group transactions by item
    item_transactions = {}
    for transaction in transactions:
        item_id = transaction['item_id']
        if item_id not in item_transactions:
            item_transactions[item_id] = []
        item_transactions[item_id].append(transaction)
    
    # Calculate value for each item
    for item in items:
        item_id = item['id']
        current_quantity = Decimal(str(item.get('quantity', 0)))
        
        # If no transactions, use current unit cost
        if item_id not in item_transactions or not item_transactions[item_id]:
            total_value += current_quantity * Decimal(str(item.get('unit_cost', 0)))
            continue
        
        # Calculate weighted average cost from purchase transactions
        total_cost = Decimal(0)
        total_quantity = Decimal(0)
        
        for transaction in item_transactions[item_id]:
            if transaction['transaction_type'] == 'purchase':
                quantity = Decimal(str(transaction.get('quantity', 0)))
                unit_price = Decimal(str(transaction.get('unit_price', 0)))
                total_cost += quantity * unit_price
                total_quantity += quantity
        
        # Calculate average cost and total value
        if total_quantity > 0:
            avg_cost = total_cost / total_quantity
            total_value += current_quantity * avg_cost
        else:
            # If no purchase transactions, use current unit cost
            total_value += current_quantity * Decimal(str(item.get('unit_cost', 0)))
    
    return total_value

class AnalyticsManager:
    """Manages analytics and data processing for inventory system."""

    def __init__(self, db_manager: SupabaseManager):
        """Initialize with database manager."""
        self.db = db_manager

    def get_inventory_summary(self) -> Dict[str, Any]:
        """Get summary statistics of current inventory."""
        items = self.db.get_items()
        transactions = self.db.get_transactions()
        
        if not items:
            return {
                "total_items": 0,
                "total_value": 0,
                "avg_unit_cost": 0,
                "low_stock_count": 0
            }

        # Calculate total value using weighted average cost
        total_value = calculate_total_value(items, transactions)
        
        # Calculate other metrics
        total_items = len(items)
        low_stock_count = sum(1 for item in items 
                            if item.get('quantity', 0) <= item.get('min_quantity', 0))
        
        # Calculate average unit cost
        total_unit_costs = sum(float(item.get('unit_cost', 0)) for item in items)
        avg_unit_cost = total_unit_costs / total_items if total_items > 0 else 0
        
        return {
            "total_items": total_items,
            "total_value": float(total_value),
            "avg_unit_cost": avg_unit_cost,
            "low_stock_count": low_stock_count
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
        transactions = self.db.get_transactions()
        df = pd.DataFrame(items)
        
        if df.empty:
            return []

        category_values = []
        for category in df['category'].unique():
            category_items = df[df['category'] == category].to_dict('records')
            value = calculate_total_value(category_items, transactions)
            category_values.append({
                "category": category,
                "value": float(value)
            })
        
        return category_values

    def get_top_selling_items(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get the top selling items for the specified period.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            List of items with their sales data
        """
        # Get sales transactions for the period
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        transactions = self.db.get_transactions(
            start_date=start_date,
            end_date=end_date
        )
        
        if not transactions:
            return []
            
        # Filter sales transactions and group by item
        sales_data = {}
        for trans in transactions:
            if trans['transaction_type'] != 'sale':
                continue
                
            item_id = trans['item_id']
            quantity = Decimal(str(trans.get('quantity', 0)))
            unit_price = Decimal(str(trans.get('unit_price', 0)))
            
            if item_id not in sales_data:
                sales_data[item_id] = {
                    'units_sold': 0,
                    'revenue': Decimal(0)
                }
            
            sales_data[item_id]['units_sold'] += quantity
            sales_data[item_id]['revenue'] += quantity * unit_price
        
        # Get item details and combine with sales data
        items = self.db.get_items()
        result = []
        
        for item in items:
            item_id = item['id']
            if item_id in sales_data:
                result.append({
                    'name': item['name'],
                    'units_sold': int(sales_data[item_id]['units_sold']),
                    'revenue': float(sales_data[item_id]['revenue'])
                })
        
        # Sort by revenue and get top 5
        result.sort(key=lambda x: x['revenue'], reverse=True)
        return result[:5]

    def get_item_turnover(self) -> List[Dict[str, Any]]:
        """Calculate inventory turnover rates for items.
        
        Returns:
            List of items with their turnover metrics
        """
        items = self.db.get_items()
        transactions = self.db.get_transactions()
        
        if not items or not transactions:
            return []
        
        # Convert transactions to DataFrame
        df = pd.DataFrame(transactions)
        df['created_at'] = pd.to_datetime(df['created_at'])
        
        result = []
        for item in items:
            item_id = item['id']
            item_trans = df[df['item_id'] == item_id]
            
            if item_trans.empty:
                continue
            
            # Calculate days in stock
            first_transaction = item_trans['created_at'].min()
            days_in_stock = (datetime.now() - first_transaction).days
            
            if days_in_stock < 1:
                continue
            
            # Calculate turnover rate (annual)
            sales = item_trans[item_trans['transaction_type'] == 'sale']
            total_sold = sales['quantity'].sum()
            avg_inventory = item['quantity'] / 2  # Simple average
            
            if avg_inventory == 0:
                continue
            
            # Annualized turnover rate
            turnover_rate = (total_sold / avg_inventory) * (365 / days_in_stock)
            
            result.append({
                'name': item['name'],
                'turnover_rate': turnover_rate,
                'days_in_stock': days_in_stock
            })
        
        # Sort by turnover rate
        result.sort(key=lambda x: x['turnover_rate'], reverse=True)
        return result

    def create_transaction_trend_chart(self, days: int = 30) -> go.Figure:
        """Create a line chart showing transaction trends over time.
        
        Args:
            days: Number of days to show in the chart
            
        Returns:
            Plotly figure object
        """
        transactions = self.db.get_transactions()
        
        if not transactions:
            # Create empty chart with message
            fig = go.Figure()
            fig.add_annotation(
                text="No transactions found",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False
            )
            return fig
            
        # Convert transactions to DataFrame
        df = pd.DataFrame(transactions)
        
        # Convert timestamps to datetime
        df['created_at'] = pd.to_datetime(df['created_at'])
        
        # Filter to last N days
        start_date = pd.Timestamp.now(tz='Asia/Manila') - pd.Timedelta(days=days)
        df = df[df['created_at'] >= start_date]
        
        # Group by date and transaction type
        daily_counts = df.groupby([
            pd.Grouper(key='created_at', freq='D'),
            'transaction_type'
        ]).size().unstack(fill_value=0)
        
        # Create the line chart
        fig = go.Figure()
        
        # Add a line for each transaction type
        colors = {
            'purchase': '#2E7D32',  # Green
            'sale': '#1976D2',      # Blue
            'adjustment': '#FFA000'  # Orange
        }
        
        for col in daily_counts.columns:
            fig.add_trace(go.Scatter(
                x=daily_counts.index,
                y=daily_counts[col],
                name=col.title(),
                line=dict(color=colors.get(col, '#757575')),
                mode='lines+markers'
            ))
        
        # Update layout
        fig.update_layout(
            title=f"Transaction Trends (Last {days} Days)",
            xaxis_title="Date",
            yaxis_title="Number of Transactions",
            hovermode='x unified',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # Format axes
        fig.update_xaxes(
            tickformat="%Y-%m-%d",
            tickangle=45,
            tickmode="auto",
            nticks=10
        )
        
        fig.update_yaxes(
            tickmode="auto",
            nticks=5,
            rangemode="nonnegative"
        )
        
        return fig

    def create_inventory_value_chart(self) -> go.Figure:
        """Create a bar chart of inventory value by category."""
        items = self.db.get_items()
        transactions = self.db.get_transactions()
        
        # Group items by category
        categories = {}
        for item in items:
            category = item.get('category', 'Uncategorized')
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
        
        # Calculate value for each category
        category_values = []
        for category, category_items in categories.items():
            value = calculate_total_value(category_items, transactions)
            category_values.append({
                'category': category,
                'value': float(value)
            })
        
        # Sort by value descending
        category_values.sort(key=lambda x: x['value'], reverse=True)
        
        # Create the bar chart
        fig = go.Figure(data=[
            go.Bar(
                x=[cv['category'] for cv in category_values],
                y=[cv['value'] for cv in category_values],
                text=[f"{cv['value']:,.2f}" for cv in category_values],
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title="Inventory Value by Category",
            xaxis_title="Category",
            yaxis_title="Value",
            showlegend=False
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

    def get_recent_transactions(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get the most recent transactions.
        
        Args:
            limit: Maximum number of transactions to return
            
        Returns:
            List of recent transactions ordered by date (newest first)
        """
        transactions = self.db.get_transactions()
        
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(transactions)
        if df.empty:
            return []
        
        # Sort by created_at in descending order and take the top N
        df['created_at'] = pd.to_datetime(df['created_at'])
        df = df.sort_values('created_at', ascending=False).head(limit)
        
        # Get item details for each transaction
        items = {item['id']: item for item in self.db.get_items()}
        
        # Enrich transactions with item details and format dates
        result = []
        for _, row in df.iterrows():
            item = items.get(row['item_id'], {})
            # Convert row to dict and handle the Timestamp
            transaction = {}
            for col in df.columns:
                val = row[col]
                # Convert Timestamp to string
                if isinstance(val, pd.Timestamp):
                    transaction[col] = val.strftime('%Y-%m-%d')
                else:
                    transaction[col] = val
            
            transaction['item_name'] = item.get('name', 'Unknown Item')
            result.append(transaction)
        
        return result
