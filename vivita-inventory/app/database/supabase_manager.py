"""Database connection and CRUD operations manager for Supabase."""

import os
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class SupabaseManager:
    """Manages database connections and operations with Supabase."""
    
    def __init__(self):
        """Initialize Supabase client."""
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase credentials not found in environment variables")
        
        self.client: Client = create_client(self.supabase_url, self.supabase_key)

    def get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single item by ID."""
        try:
            response = self.client.table("items").select("*").eq("id", item_id).single().execute()
            return response.data if response.data else None
        except Exception as e:
            print(f"Error retrieving item: {e}")
            return None

    def get_items(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Retrieve items with optional filters."""
        try:
            query = self.client.table("items").select("*")
            
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            response = query.execute()
            return response.data
        except Exception as e:
            print(f"Error retrieving items: {e}")
            return []

    def create_item(self, item_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new item."""
        try:
            response = self.client.table("items").insert(item_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating item: {e}")
            return None

    def update_item(self, item_id: str, item_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing item."""
        try:
            response = self.client.table("items").update(item_data).eq("id", item_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating item: {e}")
            return None

    def delete_item(self, item_id: str) -> bool:
        """Delete an item."""
        try:
            self.client.table("items").delete().eq("id", item_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting item: {e}")
            return False

    def create_transaction(self, transaction_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new transaction and update item quantity."""
        try:
            # Start a transaction
            response = self.client.table("transactions").insert(transaction_data).execute()
            
            if response.data:
                # Update item quantity
                item_id = transaction_data["item_id"]
                quantity_change = transaction_data["quantity"]
                
                if transaction_data["transaction_type"] in ["sale", "transfer_out", "loss"]:
                    quantity_change = -quantity_change
                
                self.client.rpc(
                    "update_item_quantity",
                    {
                        "p_item_id": item_id,
                        "p_quantity_change": quantity_change
                    }
                ).execute()
                
                return response.data[0]
        except Exception as e:
            print(f"Error creating transaction: {e}")
            return None

    def get_transactions(
        self,
        item_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve transactions with optional filters."""
        try:
            query = self.client.table("transactions").select("*")
            
            if item_id:
                query = query.eq("item_id", item_id)
            if start_date:
                query = query.gte("created_at", start_date.isoformat())
            if end_date:
                query = query.lte("created_at", end_date.isoformat())
            
            response = query.order("created_at", desc=True).execute()
            return response.data
        except Exception as e:
            print(f"Error retrieving transactions: {e}")
            return []

    def get_low_stock_items(self) -> List[Dict[str, Any]]:
        """Retrieve items with quantity below min_quantity."""
        try:
            response = self.client.table("items")\
                .select("*")\
                .lt("quantity", self.client.raw("min_quantity"))\
                .eq("is_active", True)\
                .execute()
            return response.data
        except Exception as e:
            print(f"Error retrieving low stock items: {e}")
            return []
