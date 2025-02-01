"""Constants used throughout the application."""

from enum import Enum
from typing import List, Dict

class TransactionType(str, Enum):
    """Valid transaction types."""
    PURCHASE = "purchase"
    SALE = "sale"
    ADJUSTMENT = "adjustment"
    RETURN = "return"
    TRANSFER_IN = "transfer_in"
    TRANSFER_OUT = "transfer_out"
    LOSS = "loss"
    WRITE_OFF = "write_off"
    CREDIT_NOTE = "credit_note"
    DEBIT_NOTE = "debit_note"

class UnitType(str, Enum):
    """Valid unit types."""
    PIECE = "piece"
    KG = "kg"
    GRAM = "gram"
    LITER = "liter"
    METER = "meter"
    BOX = "box"
    PACK = "pack"
    SET = "set"
    PAIR = "pair"
    UNIT = "unit"

class CategoryType(str, Enum):
    """Valid category types."""
    RAW_MATERIALS = "raw_materials"
    FINISHED_GOODS = "finished_goods"
    PACKAGING = "packaging"
    SUPPLIES = "supplies"
    EQUIPMENT = "equipment"
    SPARE_PARTS = "spare_parts"
    CONSUMABLES = "consumables"
    OTHER = "other"

# Form field configurations
ITEM_FORM_FIELDS: Dict[str, Dict] = {
    "name": {
        "label": "Item Name",
        "required": True,
        "type": "text",
        "help": "Enter the name of the item"
    },
    "description": {
        "label": "Description",
        "required": False,
        "type": "text_area",
        "help": "Enter a detailed description of the item"
    },
    "sku": {
        "label": "SKU",
        "required": True,
        "type": "text",
        "help": "Enter a unique SKU for the item"
    },
    "category": {
        "label": "Category",
        "required": True,
        "type": "select",
        "options": [e.value for e in CategoryType],
        "help": "Select the item category"
    },
    "unit_type": {
        "label": "Unit Type",
        "required": True,
        "type": "select",
        "options": [e.value for e in UnitType],
        "help": "Select the unit of measurement"
    },
    "min_quantity": {
        "label": "Minimum Quantity",
        "required": True,
        "type": "number",
        "help": "Enter the minimum stock level"
    },
    "max_quantity": {
        "label": "Maximum Quantity",
        "required": False,
        "type": "number",
        "help": "Enter the maximum stock level (optional)"
    },
    "unit_cost": {
        "label": "Unit Cost",
        "required": True,
        "type": "number",
        "help": "Enter the cost per unit"
    }
}

TRANSACTION_FORM_FIELDS: Dict[str, Dict] = {
    "transaction_type": {
        "label": "Transaction Type",
        "required": True,
        "type": "select",
        "options": [e.value for e in TransactionType],
        "help": "Select the type of transaction"
    },
    "quantity": {
        "label": "Quantity",
        "required": True,
        "type": "number",
        "help": "Enter the quantity"
    },
    "unit_price": {
        "label": "Unit Price",
        "required": True,
        "type": "number",
        "help": "Enter the price per unit"
    },
    "reference_number": {
        "label": "Reference Number",
        "required": False,
        "type": "text",
        "help": "Enter a reference number (e.g., PO number)"
    },
    "notes": {
        "label": "Notes",
        "required": False,
        "type": "text_area",
        "help": "Enter any additional notes"
    }
}

# Cache settings
CACHE_TTL = 3600  # 1 hour in seconds
CACHE_PREFIX = "vivita_inventory_"

# Pagination settings
ITEMS_PER_PAGE = 20
MAX_ITEMS_PER_PAGE = 100

# Chart settings
DEFAULT_CHART_HEIGHT = 400
DEFAULT_CHART_WIDTH = 800
CHART_COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
