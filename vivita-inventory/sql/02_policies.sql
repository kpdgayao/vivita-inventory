-- Drop existing policies
DROP POLICY IF EXISTS "Enable read access for all authenticated users" ON items;
DROP POLICY IF EXISTS "Enable insert access for authenticated users" ON items;
DROP POLICY IF EXISTS "Enable update access for authenticated users" ON items;
DROP POLICY IF EXISTS "Enable delete access for authenticated users" ON items;
DROP POLICY IF EXISTS "Enable read access for all authenticated users" ON transactions;
DROP POLICY IF EXISTS "Enable insert access for authenticated users" ON transactions;
DROP POLICY IF EXISTS "Enable update access for authenticated users" ON transactions;
DROP POLICY IF EXISTS "Enable delete access for authenticated users" ON transactions;

-- Enable Row Level Security
ALTER TABLE items ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;

-- Create policies for items table
CREATE POLICY "Enable read access for all authenticated users"
ON items FOR SELECT
TO authenticated
USING (true);

CREATE POLICY "Enable insert access for authenticated users"
ON items FOR INSERT
TO authenticated
WITH CHECK (true);

CREATE POLICY "Enable update access for authenticated users"
ON items FOR UPDATE
TO authenticated
USING (true)
WITH CHECK (true);

CREATE POLICY "Enable delete access for authenticated users"
ON items FOR DELETE
TO authenticated
USING (true);

-- Create policies for transactions table
CREATE POLICY "Enable read access for all authenticated users"
ON transactions FOR SELECT
TO authenticated
USING (true);

CREATE POLICY "Enable insert access for authenticated users"
ON transactions FOR INSERT
TO authenticated
WITH CHECK (true);

CREATE POLICY "Enable update access for authenticated users"
ON transactions FOR UPDATE
TO authenticated
USING (true)
WITH CHECK (true);

CREATE POLICY "Enable delete access for authenticated users"
ON transactions FOR DELETE
TO authenticated
USING (true);
