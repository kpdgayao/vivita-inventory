-- Enable Row Level Security
ALTER TABLE items ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;

-- Items Policies
-- Read access for authenticated users
CREATE POLICY items_read_policy ON items
    FOR SELECT
    TO authenticated
    USING (true);

-- Write access for authorized users
CREATE POLICY items_insert_policy ON items
    FOR INSERT
    TO authenticated
    WITH CHECK (auth.uid() = created_by);

-- Update access for item owners and admins
CREATE POLICY items_update_policy ON items
    FOR UPDATE
    TO authenticated
    USING (auth.uid() = created_by OR 
          EXISTS (
              SELECT 1 FROM auth.users 
              WHERE auth.uid() = id 
              AND raw_user_meta_data->>'role' = 'admin'
          ));

-- Delete access for admins only
CREATE POLICY items_delete_policy ON items
    FOR DELETE
    TO authenticated
    USING (EXISTS (
        SELECT 1 FROM auth.users 
        WHERE auth.uid() = id 
        AND raw_user_meta_data->>'role' = 'admin'
    ));

-- Transactions Policies
-- Read access for authenticated users
CREATE POLICY transactions_read_policy ON transactions
    FOR SELECT
    TO authenticated
    USING (true);

-- Write access for authorized users
CREATE POLICY transactions_insert_policy ON transactions
    FOR INSERT
    TO authenticated
    WITH CHECK (auth.uid() = created_by);

-- Update access disabled for transactions (immutable)
CREATE POLICY transactions_update_policy ON transactions
    FOR UPDATE
    TO authenticated
    USING (false);

-- Delete access for admins only
CREATE POLICY transactions_delete_policy ON transactions
    FOR DELETE
    TO authenticated
    USING (EXISTS (
        SELECT 1 FROM auth.users 
        WHERE auth.uid() = id 
        AND raw_user_meta_data->>'role' = 'admin'
    ));
