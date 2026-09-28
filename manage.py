#!/usr/bin/env python
"""
Django's command-line utility for administrative tasks.

BharatKart - Advanced Indian E-Commerce Platform
Manage script for Django administrative commands.

Usage:
    python manage.py runserver          - Start development server
    python manage.py migrate            - Apply database migrations
    python manage.py makemigrations     - Create new migrations
    python manage.py createsuperuser    - Create admin user
    python manage.py collectstatic      - Collect static files
    python manage.py shell              - Open Django shell
    python manage.py test               - Run tests
"""

import os
import sys
from pathlib import Path


def main():
    """Run administrative tasks."""
    
    # Set default settings module
    # Change to 'ecommerce.settings.production' for production
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
    
    # Add project root to Python path
    project_root = Path(__file__).resolve().parent
    sys.path.insert(0, str(project_root))
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?\n\n"
            "To activate virtual environment:\n"
            "  Windows (PowerShell): .\\.venv\\Scripts\\Activate.ps1\n"
            "  Windows (CMD):        .venv\\Scripts\\activate.bat\n"
            "  Linux/Mac:            source .venv/bin/activate\n\n"
            "To install Django:\n"
            "  pip install -r requirements.txt"
        ) from exc
    
    # Execute the command
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()