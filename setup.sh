#!/bin/bash

# Print colored output
print_status() {
    echo -e "\e[1;34m>>> $1\e[0m"
}

# Check for Python installation
print_status "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Check for Node.js installation
print_status "Checking Node.js installation..."
if ! command -v node &> /dev/null; then
    echo "Node.js is not installed. Please install Node.js and try again."
    exit 1
fi

# Create and activate Python virtual environment
print_status "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install frontend dependencies
print_status "Installing frontend dependencies..."
cd frontend
npm install

# Build frontend
print_status "Building frontend..."
npm run build

print_status "Setup completed successfully!"
print_status "To start the development servers:"
echo "1. Backend: source venv/bin/activate && python main.py"
echo "2. Frontend: cd frontend && npm run dev" 