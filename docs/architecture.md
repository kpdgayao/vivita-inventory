# Vivita Inventory Management System - Architecture

## System Overview
The Vivita Inventory Management System is a Streamlit-based application designed for Vivita's inventory management needs. It provides real-time inventory tracking, transaction management, and analytics focused on educational and creative materials.

## Technology Stack
- **Frontend**: Streamlit
- **Backend**: Supabase (PostgreSQL)
- **Data Processing**: Pandas
- **Development**: Python 3.9+
- **Environment**: Python Virtual Environment

## Core Components

### Database Structure

#### Items Table
- Tracks inventory items with:
  - Unique identifier (UUID)
  - Name and description
  - SKU (auto-generated)
  - Category (specialized for Vivita's needs)
  - Quantity and unit type
  - Cost information
  - Min/Max quantity thresholds
  - Audit fields (created_at, updated_at)

#### Transactions Table
- Records all inventory movements:
  - Transaction ID and reference number
  - Item reference
  - Transaction type (purchase, sale, adjustment)
  - Quantity and unit price
  - Timestamp and notes
  - Calculated values (total value, running balances)

#### Suppliers Table
- Manages supplier information:
  - Contact details
  - Associated items
  - Active status
  - Notes and metadata

### Application Modules

#### Database Management (`app/database/`)
- `supabase_manager.py`: Handles all database operations
  - CRUD operations for items, transactions, and suppliers
  - Connection management and error handling
  - Data validation and integrity checks

#### Analytics (`app/analytics/`)
- `analytics_manager.py`: Business intelligence features
  - Category distribution analysis
  - Transaction trend analysis
  - Stock level monitoring
  - Value calculations using weighted average cost

#### User Interface Components (`app/components/`)
- `forms.py`: Input handling
  - Dynamic form validation
  - Search-enabled item selection
  - Smart defaults and suggestions
- `sidebar.py`: Navigation
  - Page routing
  - Application state management
- `dashboard.py`: Data visualization
  - Key metrics display
  - Status summaries
  - Alert notifications

#### Utilities (`app/utils/`)
- `constants.py`: System configuration
  - Category definitions:
    - Robotics and Electronics
    - Arts and Crafts
    - Design and Prototyping
    - Kitchen/Baking Activities
    - General Office/Administrative Items
  - Transaction types
  - Unit types
- `helpers.py`: Support functions
  - SKU generation
  - Date/time handling
  - Currency formatting
  - Weighted average cost calculations

## Key Features

### Inventory Management
1. **Item Management**
   - Category-based organization
   - Automatic SKU generation
   - Stock level tracking
   - Min/Max quantity monitoring

2. **Transaction Processing**
   - Purchase recording
   - Sales tracking
   - Stock adjustments
   - Running balance calculation
   - Weighted average cost tracking

3. **Analytics & Reporting**
   - Category distribution analysis
   - Transaction trends
   - Stock alerts
   - Value calculations
   - CSV export functionality

### User Interface

#### Dashboard Page
- Overview of key metrics
- Recent transactions
- Stock alerts
- Category distribution

#### Inventory Page
- Searchable item list
- Category filtering
- Quick actions for common tasks
- Stock level indicators

#### Transactions Page
- Search-enabled item selection
- Smart transaction form
- Transaction history
- Balance tracking

#### Analytics Page
- Category analysis
- Transaction analysis
- Stock monitoring
- Value calculations

#### Settings Page
- Data management
- CSV export functionality
- System information

## Data Flow
1. User interactions via Streamlit UI
2. Form validation and data processing
3. Database operations via Supabase
4. Real-time updates and calculations
5. Analytics processing and display

## Security & Data Integrity
- Environment-based configuration
- Input validation
- Transaction logging
- Audit trail maintenance
- Data backup via Supabase

## Future Considerations
1. Multi-user support
2. Advanced reporting
3. Batch operations
4. Mobile interface
5. Integration with other systems
