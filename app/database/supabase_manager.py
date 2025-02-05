"""Database connection and CRUD operations manager for Supabase."""

import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from supabase import create_client, Client
from app.utils.helpers import get_ph_timestamp

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
            print(f"Initializing Supabase client with URL: {self.supabase_url}")
            # Initialize Supabase client with minimal configuration
            self.client: Client = create_client(
                self.supabase_url,
                self.supabase_key
            )
            # Test the connection with a simple query
            print("Testing connection with a simple query...")
            test_response = self.client.from_("items").select("*").limit(1).execute()
            print(f"Test query response: {test_response.data}")
        except Exception as e:
            import traceback
            print(f"Failed to connect to Supabase: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            raise ConnectionError(f"Failed to connect to Supabase: {str(e)}")

    def get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single item by ID."""
        try:
            response = self.client.table("items").select("*").eq("id", item_id).single().execute()
            return response.data if response.data else None
        except Exception as e:
            print(f"Error retrieving item: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return None

    def get_items(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Retrieve items with optional filters."""
        try:
            print(f"Attempting to fetch items from Supabase URL: {self.supabase_url}")
            query = self.client.table("items").select("*")
            
            if filters:
                print(f"Applying filters: {filters}")
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            response = query.execute()
            print(f"Response data type: {type(response.data)}")
            print(f"Response data: {response.data}")
            if response.data:
                print(f"Number of items retrieved: {len(response.data)}")
                if len(response.data) > 0:
                    print(f"Sample item: {response.data[0]}")
            return response.data
        except Exception as e:
            print(f"Error retrieving items: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
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
            item_data.setdefault("created_at", get_ph_timestamp())
            item_data.setdefault("updated_at", get_ph_timestamp())
            
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
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return None

    def update_item(self, item_id: str, item_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing item."""
        try:
            # Add updated_at timestamp
            item_data["updated_at"] = get_ph_timestamp()
            
            # Update the item
            response = self.client.table("items").update(item_data).eq("id", item_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating item: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return None

    def delete_item(self, item_id: str) -> bool:
        """Delete an item."""
        try:
            response = self.client.table("items").delete().eq("id", item_id).execute()
            return bool(response.data)
        except Exception as e:
            print(f"Error deleting item: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
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
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return []

    def is_connected(self) -> bool:
        """Check if database connection is active."""
        try:
            self.client.table("items").select("id").limit(1).execute()
            return True
        except Exception as e:
            print(f"Error checking connection: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
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
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
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
            
            # Generate reference number if not provided
            if not transaction_data.get("reference_number"):
                from ..utils.helpers import generate_transaction_reference
                transaction_data["reference_number"] = generate_transaction_reference()
            
            # Create transaction record with only allowed fields
            # Let the database handle timestamps with DEFAULT CURRENT_TIMESTAMP
            transaction_record = {
                "item_id": transaction_data["item_id"],
                "transaction_type": transaction_data["transaction_type"],
                "quantity": transaction_data["quantity"],
                "unit_price": transaction_data["unit_price"],
                "reference_number": transaction_data.get("reference_number", ""),
                "notes": transaction_data.get("notes", "")
            }
            
            # Create transaction
            print(f"Sending transaction to Supabase: {transaction_record}")
            response = self.client.table("transactions").insert(transaction_record).execute()
            print(f"Supabase response: {response}")
            if not response.data:
                raise ValueError("No data returned from transaction insert")
            
            # Update item quantity
            # Let the database trigger handle updated_at
            self.update_item(item["id"], {
                "quantity": new_quantity
            })
            
            return response.data[0]
        except Exception as e:
            print(f"Error creating transaction: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            raise  # Re-raise the exception to be handled by the caller

    def get_transaction(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single transaction by ID."""
        try:
            response = self.client.table("transactions").select("*").eq("id", transaction_id).single().execute()
            return response.data if response.data else None
        except Exception as e:
            print(f"Error retrieving transaction: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return None

    def update_transaction(self, transaction_id: str, transaction_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing transaction."""
        try:
            # Add updated_at timestamp
            transaction_data["updated_at"] = get_ph_timestamp()
            
            # Update the transaction
            response = self.client.table("transactions").update(transaction_data).eq("id", transaction_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating transaction: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return None

    def delete_transaction(self, transaction_id: str) -> bool:
        """Delete a transaction."""
        try:
            response = self.client.table("transactions").delete().eq("id", transaction_id).execute()
            return bool(response.data)
        except Exception as e:
            print(f"Error deleting transaction: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return False

    def get_supplier(self, supplier_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single supplier by ID."""
        try:
            print(f"\n=== Getting Supplier {supplier_id} ===")
            response = self.client.table("suppliers").select("*").eq("id", supplier_id).single().execute()
            
            if not response.data:
                print("No supplier found with ID:", supplier_id)
                return None
            
            print("Retrieved supplier:", response.data)
            return response.data
        except Exception as e:
            print(f"Error retrieving supplier: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
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
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
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
            supplier_data.setdefault("created_at", get_ph_timestamp())
            supplier_data.setdefault("updated_at", get_ph_timestamp())
            
            # Debug: Print final data before insert
            print("Final supplier data to insert:", supplier_data)
            
            # Create the supplier
            try:
                print("Attempting to insert supplier...")
                response = self.client.table("suppliers").insert(supplier_data).execute()
                print("Insert response:", response)
                
                if not response.data:
                    print("Error: No data returned from insert operation")
                    if hasattr(response, 'error'):
                        print("Error details:", response.error)
                    return None
                
                print("Created supplier:", response.data[0])
                return response.data[0]
            except Exception as insert_error:
                print(f"Error during insert operation: {str(insert_error)}")
                import traceback
                print(f"Insert error traceback: {traceback.format_exc()}")
                raise
        except Exception as e:
            print(f"Error creating supplier: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return None

    def update_supplier(self, supplier_id: str, supplier_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing supplier."""
        try:
            print("\n=== Updating Supplier ===")
            print("Initial update data:", supplier_data)
            
            # Remove any None values and id from update data
            update_data = {k: v for k, v in supplier_data.items() if v is not None and k != 'id'}
            print("Filtered update data:", update_data)
            
            # Update the updated_at timestamp
            update_data["updated_at"] = get_ph_timestamp()
            
            response = self.client.table("suppliers").update(update_data).eq("id", supplier_id).execute()
            print("Update response:", response)
            
            if not response.data:
                print("Error: No data returned from update operation")
                if hasattr(response, 'error'):
                    print("Error details:", response.error)
                return None
            
            print("Updated supplier:", response.data[0])
            return response.data[0]
        except Exception as e:
            print(f"Error updating supplier: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return None

    def delete_supplier(self, supplier_id: str) -> bool:
        """Soft delete a supplier by setting is_active to False."""
        try:
            response = self.client.table("suppliers").update({
                "is_active": False,
                "updated_at": get_ph_timestamp()
            }).eq("id", supplier_id).execute()
            
            return bool(response.data)
        except Exception as e:
            print(f"Error deleting supplier: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return False
