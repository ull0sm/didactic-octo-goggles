#!/bin/bash
# Start script for EntryDesk application

echo "Starting EntryDesk Application..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please edit .env file with your credentials before running again."
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Initialize database
echo "Initializing database..."
python -c "from database import init_db; init_db()"

# Start Streamlit app
echo "Starting Streamlit application on http://localhost:8501"
streamlit run app.py
