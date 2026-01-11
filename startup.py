"""
startup.py - Easy startup script for both frontend and backend
==============================================================
Provides a simple way to start the application.
"""

import subprocess
import sys
import time
import os
from pathlib import Path


def check_dependencies():
    """Check if required packages are installed."""
    required_packages = [
        'fastapi',
        'uvicorn',
        'streamlit',
        'sqlmodel',
        'pandas',
        'constraint',
        'requests'
    ]
    
    print("Checking dependencies...")
    missing = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package}")
            missing.append(package)
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print(f"\nInstall with: pip install {' '.join(missing)}")
        return False
    
    print("✓ All dependencies installed!\n")
    return True


def start_backend():
    """Start FastAPI backend."""
    print("\n" + "="*60)
    print("Starting FastAPI Backend...")
    print("="*60)
    print("API will be available at: http://localhost:8000")
    print("Swagger UI: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop backend")
    print("="*60 + "\n")
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "timetable_generator.backend:app",
            "--reload",
            "--host", "0.0.0.0",
            "--port", "8000"
        ])
    except KeyboardInterrupt:
        print("\n✓ Backend stopped")


def start_frontend():
    """Start Streamlit frontend."""
    time.sleep(2)  # Give backend time to start
    
    print("\n" + "="*60)
    print("Starting Streamlit Frontend...")
    print("="*60)
    print("UI will be available at: http://localhost:8501")
    print("\nPress Ctrl+C to stop frontend")
    print("="*60 + "\n")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            "timetable_generator/app.py",
            "--logger.level=info"
        ])
    except KeyboardInterrupt:
        print("\n✓ Frontend stopped")


def main():
    """Main startup function."""
    print("\n" + "="*60)
    print("🎓 MKCE Timetable Generator - Startup Script")
    print("="*60 + "\n")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Initialize database if needed
    print("Checking database...")
    try:
        from timetable_generator.database import create_db_and_tables
        create_db_and_tables()
        print("✓ Database initialized\n")
    except Exception as e:
        print(f"⚠️  Database check warning: {e}\n")
    
    # Ask user what to start
    print("What would you like to start?")
    print("1. Both Backend & Frontend")
    print("2. Backend only")
    print("3. Frontend only")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        print("\nStarting both services...")
        print("Backend on http://localhost:8000")
        print("Frontend on http://localhost:8501")
        
        # Start backend in main process
        # Frontend can be started in another terminal
        start_backend()
    elif choice == "2":
        start_backend()
    elif choice == "3":
        start_frontend()
    else:
        print("Invalid choice")
        sys.exit(1)


if __name__ == "__main__":
    main()
