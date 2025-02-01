-- Transaction Types
CREATE TYPE transaction_type AS ENUM (
    'purchase',
    'sale',
    'adjustment',
    'return',
    'transfer_in',
    'transfer_out',
    'loss',
    'write_off'
);

-- Unit Types
CREATE TYPE unit_type AS ENUM (
    'piece',
    'kg',
    'gram',
    'liter',
    'meter',
    'box',
    'pack',
    'set',
    'pair',
    'unit'
);

-- Category Types
CREATE TYPE category_type AS ENUM (
    'raw_materials',
    'finished_goods',
    'packaging',
    'supplies',
    'equipment',
    'spare_parts',
    'consumables',
    'other'
);

COMMENT ON TYPE transaction_type IS 'Valid types of inventory transactions';
COMMENT ON TYPE unit_type IS 'Valid units of measurement for items';
COMMENT ON TYPE category_type IS 'Valid categories for inventory items';
