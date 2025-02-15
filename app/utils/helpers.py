"""Helper functions for the inventory management system."""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
import re
import uuid
from decimal import Decimal
import pytz

def generate_sku(
    category: str,
    name: str,
    existing_skus: List[str] = None
) -> str:
    """Generate a unique SKU for an item."""
    # Convert category and name to uppercase
    category = category.upper()
    name = name.upper()
    
    # Get first 3 letters of category
    category_prefix = re.sub(r'[^A-Z]', '', category)[:3]
    
    # Get first 3 letters of name
    name_part = re.sub(r'[^A-Z]', '', name)[:3]
    
    # Generate base SKU
    base_sku = f"{category_prefix}-{name_part}"
    
    if not existing_skus:
        return f"{base_sku}-001"
    
    # Find highest number for this base SKU
    pattern = re.compile(f"{base_sku}-?(\\d+)")
    max_num = 0
    
    for sku in existing_skus:
        match = pattern.match(sku)
        if match:
            num = int(match.group(1))
            max_num = max(max_num, num)
    
    return f"{base_sku}-{str(max_num + 1).zfill(3)}"

def validate_quantity(
    quantity: Union[int, float],
    min_quantity: Optional[Union[int, float]] = None,
    max_quantity: Optional[Union[int, float]] = None
) -> bool:
    """Validate quantity against min and max constraints."""
    try:
        quantity = float(quantity)
        
        if quantity < 0:
            return False
            
        if min_quantity is not None and quantity < float(min_quantity):
            return False
            
        if max_quantity is not None and quantity > float(max_quantity):
            return False
            
        return True
    except (ValueError, TypeError):
        return False

def format_currency(
    amount: Union[int, float, Decimal],
    currency: str = "₱",
    decimals: int = 2
) -> str:
    """Format a number as currency.
    
    Args:
        amount: The amount to format
        currency: Currency symbol to use (default: ₱)
        decimals: Number of decimal places (default: 2)
    
    Returns:
        Formatted currency string
    """
    return f"{currency}{float(amount):,.{decimals}f}"

def calculate_reorder_quantity(
    current_quantity: int,
    min_quantity: int,
    max_quantity: Optional[int] = None,
    avg_daily_usage: Optional[float] = None
) -> int:
    """Calculate recommended reorder quantity."""
    if max_quantity is None:
        max_quantity = min_quantity * 3
    
    if current_quantity >= min_quantity:
        return 0
    
    base_quantity = max_quantity - current_quantity
    
    if avg_daily_usage:
        # Add buffer based on average daily usage
        buffer_days = 7  # One week buffer
        buffer_quantity = int(avg_daily_usage * buffer_days)
        return base_quantity + buffer_quantity
    
    return base_quantity

def parse_date_range(
    date_str: str
) -> tuple[datetime, datetime]:
    """Parse date range string into start and end dates."""
    today = datetime.now()
    
    if date_str == "today":
        start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = today.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif date_str == "yesterday":
        start_date = (today - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = (today - timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=999999)
    elif date_str == "last7days":
        start_date = (today - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = today.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif date_str == "last30days":
        start_date = (today - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = today.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif date_str == "thismonth":
        start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = today.replace(hour=23, minute=59, second=59, microsecond=999999)
    else:
        raise ValueError("Invalid date range")
    
    return start_date, end_date

def get_ph_time() -> datetime:
    """Get current time in Philippine timezone (GMT+8)."""
    ph_tz = pytz.timezone('Asia/Manila')
    return datetime.now(ph_tz)

def format_timestamp(timestamp_str: str, format: str = "%Y-%m-%d %H:%M") -> str:
    """
    Format a timestamp string to Philippine time.
    
    Args:
        timestamp_str: ISO format timestamp string
        format: Optional strftime format string
    
    Returns:
        Formatted timestamp string in Philippine time
    """
    # Remove 'Z' if present and add UTC timezone if no timezone info
    if timestamp_str.endswith('Z'):
        timestamp_str = timestamp_str[:-1] + '+00:00'
    elif '+' not in timestamp_str and '-' not in timestamp_str:
        timestamp_str += '+00:00'
    
    # Parse the timestamp
    timestamp = datetime.fromisoformat(timestamp_str)
    
    # Convert to Philippine time
    ph_tz = pytz.timezone('Asia/Manila')
    ph_time = timestamp.astimezone(ph_tz)
    
    return ph_time.strftime(format)

def get_ph_timestamp() -> str:
    """Get current timestamp in Philippine time, ISO format."""
    return get_ph_time().isoformat()

def calculate_weighted_average_cost(
    transactions: List[Dict[str, Any]]
) -> Decimal:
    """
    Calculate the weighted average cost of inventory based on purchase transactions.
    
    Args:
        transactions: List of transaction records with quantity and unit_price
        
    Returns:
        Weighted average cost per unit
    """
    total_cost = Decimal('0')
    total_quantity = Decimal('0')
    
    for transaction in transactions:
        if transaction['transaction_type'] == 'purchase':
            quantity = Decimal(str(transaction.get('quantity', 0)))
            unit_price = Decimal(str(transaction.get('unit_price', 0)))
            total_cost += quantity * unit_price
            total_quantity += quantity
    
    return total_cost / total_quantity if total_quantity > 0 else Decimal('0')

def calculate_total_value(
    items: List[Dict[str, Any]],
    transactions: Optional[List[Dict[str, Any]]] = None
) -> Decimal:
    """
    Calculate total value of inventory items using weighted average cost if transactions are provided.
    
    Args:
        items: List of inventory items
        transactions: Optional list of transactions to calculate weighted average cost
        
    Returns:
        Total inventory value
    """
    total = Decimal('0')
    
    for item in items:
        quantity = Decimal(str(item.get('quantity', 0)))
        
        # If we have transactions, use weighted average cost
        if transactions:
            item_transactions = [
                t for t in transactions 
                if t.get('item_id') == item.get('id')
            ]
            if item_transactions:
                unit_cost = calculate_weighted_average_cost(item_transactions)
            else:
                unit_cost = Decimal(str(item.get('unit_cost', 0)))
        else:
            # Fall back to current unit_cost if no transactions
            unit_cost = Decimal(str(item.get('unit_cost', 0)))
            
        total += quantity * unit_cost
    
    return total

def generate_transaction_reference() -> str:
    """Generate a unique transaction reference number."""
    timestamp = datetime.now().strftime('%Y%m%d')
    unique_id = str(uuid.uuid4())[:8]
    return f"TXN-{timestamp}-{unique_id}"
