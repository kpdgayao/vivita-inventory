-- Function to get items with quantity at or below min_quantity
CREATE OR REPLACE FUNCTION get_low_stock_items()
RETURNS TABLE (
    id uuid,
    name text,
    description text,
    sku text,
    category text,
    unit_type text,
    quantity integer,
    min_quantity integer,
    max_quantity integer,
    unit_cost decimal,
    last_ordered_at timestamp with time zone,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    created_by uuid,
    is_active boolean
) AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM items
    WHERE quantity <= min_quantity
    AND is_active = true;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
