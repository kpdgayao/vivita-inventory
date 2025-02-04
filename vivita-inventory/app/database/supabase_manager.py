"""Database connection and CRUD operations manager for Supabase."""

import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

class SupabaseManager:
    """Manages database connections and operations with Supabase."""
    
    def __init__(self):
        """Initialize Supabase client."""
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase credentials not found in environment variables")
        
        try:
            # Initialize Supabase client with minimal configuration
            self.client: Client = create_client(
                self.supabase_url,
                self.supabase_key
            )
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Supabase: {str(e)}")

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
            # Ensure required fields are present and match database schema
            required_fields = ["name", "category", "unit_type", "quantity", "unit_cost", "min_quantity"]
            missing_fields = [field for field in required_fields if field not in item_data]
            if missing_fields:
                raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
            
            # Add default values if not present
            item_data.setdefault("is_active", True)
            item_data.setdefault("created_at", datetime.now().isoformat())
            item_data.setdefault("updated_at", datetime.now().isoformat())
            
            # Ensure numeric fields are the correct type
            try:
                item_data["quantity"] = int(item_data["quantity"])
                item_data["min_quantity"] = int(item_data["min_quantity"])
                item_data["unit_cost"] = float(item_data["unit_cost"])
                if "max_quantity" in item_data:
                    item_data["max_quantity"] = int(item_data["max_quantity"])
            except (ValueError, TypeError) as e:
                raise ValueError(f"Invalid numeric value: {str(e)}")
            
            # Create the item
            response = self.client.table("items").insert(item_data).execute()
            
            if not response.data:
                return None
            
            return response.data[0]
        except Exception as e:
            print(f"Error creating item: {e}")
            return None

    def update_item(self, item_id: str, item_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing item."""
        try:
            # Add updated_at timestamp
            item_data["updated_at"] = datetime.now().isoformat()
            
            # Update the item
            response = self.client.table("items").update(item_data).eq("id", item_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating item: {e}")
            return None

    def delete_item(self, item_id: str) -> bool:
        """Delete an item."""
        try:
            response = self.client.table("items").delete().eq("id", item_id).execute()
            return bool(response.data)
        except Exception as e:
            print(f"Error deleting item: {e}")
            return False

    def get_low_stock_items(self) -> List[Dict[str, Any]]:
        """Retrieve items with quantity below min_quantity."""
        try:
            # Using a simple query to compare quantity with min_quantity
            response = self.client.table("items").select("*").execute()
            if not response.data:
                return []
            
            # Filter in Python since Supabase doesn't support column comparisons
            return [item for item in response.data if item["quantity"] <= item["min_quantity"]]
        except Exception as e:
            print(f"Error retrieving low stock items: {e}")
            return []

    def is_connected(self) -> bool:
        """Check if database connection is active."""
        try:
            self.client.table("items").select("id").limit(1).execute()
            return True
        except Exception:
            return False

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

    def create_transaction(self, transaction_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new transaction and update item quantity."""
        try:
            # Get the item to validate quantity
            item = self.get_item(transaction_data["item_id"])
            if not item:
                raise ValueError(f"Item with ID {transaction_data['item_id']} not found")
            
            print(f"Creating transaction with data: {transaction_data}")
            
            # Calculate new quantity
            quantity_change = transaction_data["quantity"]
            if transaction_data["transaction_type"] in ["sale", "transfer_out", "loss"]:
                quantity_change = -quantity_change
            
            new_quantity = item["quantity"] + quantity_change
            
            # Validate new quantity
            if new_quantity < 0:
                raise ValueError("Transaction would result in negative quantity")
            
            # Create transaction
            print(f"Sending transaction to Supabase: {transaction_data}")
            response = self.client.table("transactions").insert(transaction_data).execute()
            print(f"Supabase response: {response}")
            if not response.data:
                raise ValueError("No data returned from transaction insert")
            
            # Update item quantity
            self.update_item(item["id"], {"quantity": new_quantity})
            
            return response.data[0]
        except Exception as e:
            print(f"Error creating transaction: {e}")
            return None

    def get_transaction(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single transaction by ID."""
        try:
            response = self.client.table("transactions").select("*").eq("id", transaction_id).single().execute()
            return response.data if response.data else None
        except Exception as e:
            print(f"Error retrieving transaction: {e}")
            return None

    def update_transaction(self, transaction_id: str, transaction_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing transaction."""
        try:
            # Add updated_at timestamp
            transaction_data["updated_at"] = datetime.now().isoformat()
            
            # Update the transaction
            response = self.client.table("transactions").update(transaction_data).eq("id", transaction_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating transaction: {e}")
            return None

    def delete_transaction(self, transaction_id: str) -> bool:
        """Delete a transaction."""
        try:
            response = self.client.table("transactions").delete().eq("id", transaction_id).execute()
            return bool(response.data)
        except Exception as e:
            print(f"Error deleting transaction: {e}")
            return False

    def get_supplier(self, supplier_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single supplier by ID."""
        try:
            response = self.client.table("suppliers").select("*").eq("id", supplier_id).single().execute()
            return response.data if response.data else None
        except Exception as e:
            print(f"Error retrieving supplier: {e}")
            return None

    def get_suppliers(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Retrieve suppliers with optional filters."""
        try:
            query = self.client.table("suppliers").select("*")
            
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            # Only return active suppliers by default
            if not filters or "is_active" not in filters:
                query = query.eq("is_active", True)
            
            response = query.execute()
            return response.data
        except Exception as e:
            print(f"Error retrieving suppliers: {e}")
            return []

    def create_supplier(self, supplier_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new supplier."""
        try:
            # Debug: Print initial data
            print("\n=== Creating New Supplier ===")
            print("Initial supplier data:", supplier_data)
            
            # Ensure required fields are present
            if "name" not in supplier_data:
                raise ValueError("Supplier name is required")
            
            # Add default values if not present
            supplier_data.setdefault("is_active", True)
            supplier_data.setdefault("created_at", datetime.now().isoformat())
            supplier_data.setdefault("updated_at", datetime.now().isoformat())
            
            # Create the supplier
            response = self.client.table("suppliers").insert(supplier_data).execute()
            
            if not response.data:
                print("Error: No data returned from insert operation")
                return None
            
            return response.data[0]
        except Exception as e:
            print(f"Error creating supplier: {e}")
            return None

    def update_supplier(self, supplier_id: str, supplier_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing supplier."""
        try:
            # Remove any None values
            update_data = {k: v for k, v in supplier_data.items() if v is not None}
            
            # Update the updated_at timestamp
            update_data["updated_at"] = datetime.now().isoformat()
            
            response = self.client.table("suppliers").update(update_data).eq("id", supplier_id).execute()
            
            if not response.data:
                print("Error: No data returned from update operation")
                return None
            
            return response.data[0]
        except Exception as e:
            print(f"Error updating supplier: {e}")
            return None

    def delete_supplier(self, supplier_id: str) -> bool:
        """Soft delete a supplier by setting is_active to False."""
        try:
            response = self.client.table("suppliers").update({
                "is_active": False,
                "updated_at": datetime.now().isoformat()
            }).eq("id", supplier_id).execute()
            
            return bool(response.data)
        except Exception as e:
            print(f"Error deleting supplier: {e}")
            return False
