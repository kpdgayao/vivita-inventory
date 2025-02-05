-- Enable Row Level Security for suppliers
ALTER TABLE suppliers ENABLE ROW LEVEL SECURITY;

-- Create policy to enable read access for all users
CREATE POLICY "Enable read access for suppliers"
ON suppliers
FOR SELECT
USING (true);

-- Create policy to enable insert access for all users
CREATE POLICY "Enable insert access for suppliers"
ON suppliers
FOR INSERT
WITH CHECK (true);

-- Create policy to enable update access for all users
CREATE POLICY "Enable update access for suppliers"
ON suppliers
FOR UPDATE
USING (true)
WITH CHECK (true);

-- Create policy to enable delete access for all users (soft delete)
CREATE POLICY "Enable delete access for suppliers"
ON suppliers
FOR DELETE
USING (true);
