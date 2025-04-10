# Function to print status messages
function Write-Status {
    param($Message)
    Write-Host ">>> $Message" -ForegroundColor Blue
}

# Check for Python installation
Write-Status "Checking Python installation..."
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python 3 is not installed. Please install Python 3 and try again." -ForegroundColor Red
    exit 1
}

# Check for Node.js installation
Write-Status "Checking Node.js installation..."
if (!(Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "Node.js is not installed. Please install Node.js and try again." -ForegroundColor Red
    exit 1
}

# Create and activate Python virtual environment
Write-Status "Setting up Python virtual environment..."
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install Python dependencies
Write-Status "Installing Python dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# Install frontend dependencies
Write-Status "Installing frontend dependencies..."
Set-Location frontend
npm install

# Build frontend
Write-Status "Building frontend..."
npm run build

Write-Status "Setup completed successfully!"
Write-Status "To start the development servers:"
Write-Host "1. Backend: .\venv\Scripts\Activate.ps1 && python main.py"
Write-Host "2. Frontend: cd frontend && npm run dev"

# Return to root directory
Set-Location .. 