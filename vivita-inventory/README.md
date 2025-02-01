# Vivita Inventory Management System

A modern, efficient inventory management system built with Streamlit and Supabase.

## Features

- Real-time inventory tracking
- Transaction history
- Analytics dashboard
- Stock alerts
- Multi-user support
- Role-based access control

## Technology Stack

- Frontend: Streamlit
- Backend: Supabase
- Database: PostgreSQL
- Analytics: Pandas, Plotly
- Authentication: Supabase Auth

## Setup Instructions

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and configure your environment variables
4. Run the application:
   ```bash
   streamlit run app/main.py
   ```

## Environment Variables

Required environment variables in `.env`:
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase project API key
- `STREAMLIT_SERVER_PORT`: Port for Streamlit server (default: 8501)

## Development Guidelines

1. Follow PEP 8 style guide
2. Add type hints to all functions
3. Include docstrings for all modules and functions
4. Write unit tests for new features
5. Update documentation when making changes

## Testing

Run tests using pytest:
```bash
pytest tests/
```

## Deployment

1. Set up your Supabase project
2. Configure environment variables
3. Deploy using Docker:
   ```bash
   docker-compose up -d
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License
