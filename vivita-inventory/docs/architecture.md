# Vivita Inventory Management System - Architecture

## System Overview
The Vivita Inventory Management System is a modern web application built using Streamlit for the frontend and Supabase for the backend. It provides real-time inventory tracking, analytics, and multi-user support.

## Technology Stack
- **Frontend**: Streamlit
- **Backend**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth
- **Analytics**: Pandas, Plotly
- **Development**: Python 3.9+
- **Deployment**: Docker

## Database Schema

### Items Table
- Primary inventory items table
- Tracks quantity, costs, and thresholds
- Includes audit fields (created_at, updated_at)

### Transactions Table
- Immutable transaction log
- Records all inventory movements
- Links to items and users

## Core Modules

### Database Module
- `supabase_manager.py`: Database connection and CRUD operations
- Connection pooling and error handling
- Transaction management

### Analytics Module
- `analytics_manager.py`: Data analysis and metrics
- `visualizations.py`: Charts and dashboards
- Caching for performance

### Components Module
- `forms.py`: Input forms and validation
- `sidebar.py`: Navigation and filters
- `dashboard.py`: Main dashboard components

### Utils Module
- `constants.py`: System constants
- `helpers.py`: Utility functions

## Features & Workflows

### Inventory Management
1. Item creation and updates
2. Stock level tracking
3. Low stock alerts

### Transaction Processing
1. Purchase recording
2. Sales tracking
3. Stock adjustments
4. Returns handling

### Analytics & Reporting
1. Stock level reports
2. Transaction history
3. Trend analysis
4. Cost tracking

## User Interface Components

### Main Dashboard
- Current stock levels
- Recent transactions
- Alert notifications

### Inventory Management
- Item list view
- Add/Edit forms
- Stock adjustment interface

### Analytics Dashboard
- Stock trends
- Transaction summary
- Cost analysis

## Data Flow
1. User interacts with Streamlit UI
2. Requests processed by component handlers
3. Database operations via Supabase
4. Real-time updates reflected in UI

## Security & Access Control

### Authentication
- Supabase Auth integration
- JWT token management
- Session handling

### Authorization
- Role-based access control
- Row-level security policies
- Audit logging

## Deployment Guide

### Prerequisites
1. Docker and Docker Compose
2. Supabase account
3. Environment variables configured

### Deployment Steps
1. Build Docker image
2. Configure environment
3. Run database migrations
4. Start application

### Monitoring
- Application logs
- Database metrics
- Error tracking

## Performance Considerations
- Database indexing
- Query optimization
- Caching strategies
- Connection pooling
