# BharatKart Setup Script for Windows
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "BharatKart Setup Script (Windows)" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

# Function to check Python
function Check-Python {
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "Python version: $pythonVersion" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "Python is not installed. Please install Python 3.8+" -ForegroundColor Red
        return $false
    }
}

# Function to create directory
function Create-Directory {
    param($Path)
    if (!(Test-Path $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
        Write-Host "Created: $Path" -ForegroundColor Green
    }
}

# Check Python
if (!(Check-Python)) {
    exit 1
}

# Create virtual environment
Write-Host "`nCreating virtual environment..." -ForegroundColor Yellow
if (!(Test-Path .venv)) {
    python -m venv .venv
    Write-Host "Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "Virtual environment already exists" -ForegroundColor Yellow
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\.venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install requirements
Write-Host "Installing requirements..." -ForegroundColor Yellow
pip install -r requirements.txt

# Create .env file
if (!(Test-Path .env)) {
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "Please edit .env file with your configuration" -ForegroundColor Red
} else {
    Write-Host ".env file already exists" -ForegroundColor Green
}

# Create directories
Write-Host "`nCreating directories..." -ForegroundColor Yellow
$directories = @(
    'media/products',
    'media/categories',
    'media/brands',
    'media/profiles',
    'media/reviews',
    'media/invoices',
    'logs',
    'chroma_db',
    'faiss_index',
    'staticfiles'
)

foreach ($dir in $directories) {
    Create-Directory -Path $dir
}

# Run migrations
Write-Host "`nRunning migrations..." -ForegroundColor Yellow
python manage.py makemigrations
python manage.py migrate

# Create superuser
Write-Host "`nCreating superuser..." -ForegroundColor Yellow
Write-Host "Please enter your superuser credentials:" -ForegroundColor Cyan
python manage.py createsuperuser

# Collect static files
Write-Host "`nCollecting static files..." -ForegroundColor Yellow
python manage.py collectstatic --noinput

# Download NLTK data
Write-Host "`nDownloading NLTK data..." -ForegroundColor Yellow
python -c "import nltk; nltk.download('punkt')"

# Generate sample data
Write-Host "`nDo you want to generate sample data? (y/n)" -ForegroundColor Yellow
$response = Read-Host
if ($response -eq 'y' -or $response -eq 'Y') {
    Write-Host "Generating sample data..." -ForegroundColor Yellow
    python scripts/generate_sample_data.py
}

# Index knowledge base
Write-Host "`nIndexing knowledge base..." -ForegroundColor Yellow
python manage.py shell -c "from apps.rag.rag_pipeline import HybridRAGPipeline; HybridRAGPipeline().bulk_index_knowledge_base()"

Write-Host "`n==================================" -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green
Write-Host ""
Write-Host "To run the development server:" -ForegroundColor Cyan
Write-Host "  .\.venv\Scripts\Activate.ps1" -ForegroundColor Yellow
Write-Host "  python manage.py runserver" -ForegroundColor Yellow
Write-Host ""
Write-Host "To run with WebSocket support:" -ForegroundColor Cyan
Write-Host "  daphne -b 0.0.0.0 -p 8000 ecommerce.asgi:application" -ForegroundColor Yellow
Write-Host ""
Write-Host "To run Celery worker:" -ForegroundColor Cyan
Write-Host "  celery -A ecommerce worker -l info" -ForegroundColor Yellow
Write-Host ""
Write-Host "Access the application at: http://localhost:8000" -ForegroundColor Green