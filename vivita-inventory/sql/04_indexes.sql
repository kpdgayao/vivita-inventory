-- Items table indexes
-- Index for SKU searches
CREATE INDEX idx_items_sku ON items (sku);

-- Index for category filtering
CREATE INDEX idx_items_category ON items (category);

-- Index for low stock queries
CREATE INDEX idx_items_quantity_status ON items (quantity) 
WHERE quantity <= min_quantity AND is_active = true;

-- Combined index for name searches and category filtering
CREATE INDEX idx_items_name_category ON items (name, category);

-- Index for last ordered items
CREATE INDEX idx_items_last_ordered ON items (last_ordered_at DESC NULLS LAST)
WHERE is_active = true;

-- Transactions table indexes
-- Index for item_id foreign key
CREATE INDEX idx_transactions_item_id ON transactions (item_id);

-- Index for transaction type filtering
CREATE INDEX idx_transactions_type ON transactions (transaction_type);

-- Index for transaction date range queries
CREATE INDEX idx_transactions_created_at ON transactions (created_at DESC);

-- Combined index for item transactions
CREATE INDEX idx_transactions_item_date ON transactions (item_id, created_at DESC);

-- Index for reference number searches
CREATE INDEX idx_transactions_reference ON transactions (reference_number);

COMMENT ON INDEX idx_items_sku IS 'Optimize SKU lookups';
COMMENT ON INDEX idx_items_category IS 'Optimize category filtering';
COMMENT ON INDEX idx_items_quantity_status IS 'Optimize low stock queries';
COMMENT ON INDEX idx_transactions_item_id IS 'Optimize item transaction lookups';
COMMENT ON INDEX idx_transactions_type IS 'Optimize transaction type filtering';
