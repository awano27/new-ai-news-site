#!/usr/bin/env python3
"""Setup script for Daily AI News project."""

import os
import sys
import subprocess
from pathlib import Path


def run_command(command: str, description: str) -> bool:
    """Run a command and return success status."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False


def setup_python_environment():
    """Set up Python virtual environment and dependencies."""
    print("🐍 Setting up Python environment...")
    
    # Check Python version
    if sys.version_info < (3, 11):
        print("❌ Python 3.11 or higher is required")
        return False
    
    # Create virtual environment if it doesn't exist
    if not Path("venv").exists():
        if not run_command("python -m venv venv", "Creating virtual environment"):
            return False
    
    # Activate environment and install dependencies
    if os.name == 'nt':  # Windows
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Unix-like
        pip_cmd = "venv/bin/pip"
    
    commands = [
        (f"{pip_cmd} install --upgrade pip", "Upgrading pip"),
        (f"{pip_cmd} install -r requirements.txt", "Installing Python dependencies"),
        (f"{pip_cmd} install -e .", "Installing project in development mode"),
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    
    return True


def setup_spacy_models():
    """Download required spaCy models."""
    print("📚 Setting up spaCy models...")
    
    if os.name == 'nt':  # Windows
        python_cmd = "venv\\Scripts\\python"
    else:  # Unix-like
        python_cmd = "venv/bin/python"
    
    models = [
        ("en_core_web_sm", "English language model"),
        ("ja_core_news_sm", "Japanese language model"),
    ]
    
    for model, description in models:
        command = f"{python_cmd} -m spacy download {model}"
        if not run_command(command, f"Downloading {description}"):
            print(f"⚠️  Failed to download {model}, continuing...")
    
    return True


def create_directories():
    """Create necessary directories."""
    print("📁 Creating project directories...")
    
    directories = [
        "data",
        "cache",
        "logs",
        "dist",
        "templates",
        "static",
        "tests/unit",
        "tests/integration",
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    return True


def setup_git_hooks():
    """Set up Git pre-commit hooks."""
    print("🔧 Setting up Git hooks...")
    
    if not Path(".git").exists():
        print("⚠️  Not a Git repository, skipping hook setup")
        return True
    
    if os.name == 'nt':  # Windows
        python_cmd = "venv\\Scripts\\python"
    else:  # Unix-like
        python_cmd = "venv/bin/python"
    
    commands = [
        (f"{python_cmd} -m pip install pre-commit", "Installing pre-commit"),
        (f"{python_cmd} -m pre_commit install", "Setting up pre-commit hooks"),
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            print(f"⚠️  {description} failed, continuing...")
    
    return True


def create_env_file():
    """Create .env file from template if it doesn't exist."""
    print("🔧 Setting up environment file...")
    
    if not Path(".env").exists():
        if Path(".env.example").exists():
            import shutil
            shutil.copy(".env.example", ".env")
            print("✅ Created .env from template")
            print("⚠️  Please edit .env file with your API keys")
        else:
            print("⚠️  .env.example not found")
    else:
        print("✅ .env file already exists")
    
    return True


def main():
    """Main setup function."""
    print("🚀 Daily AI News - Project Setup")
    print("=" * 50)
    
    setup_tasks = [
        ("Python Environment", setup_python_environment),
        ("spaCy Models", setup_spacy_models),
        ("Project Directories", create_directories),
        ("Environment File", create_env_file),
        ("Git Hooks", setup_git_hooks),
    ]
    
    success_count = 0
    total_tasks = len(setup_tasks)
    
    for task_name, task_func in setup_tasks:
        print(f"\n📋 Setting up {task_name}...")
        if task_func():
            success_count += 1
        else:
            print(f"❌ {task_name} setup failed")
    
    print("\n" + "=" * 50)
    print(f"✅ Setup completed: {success_count}/{total_tasks} tasks successful")
    
    if success_count == total_tasks:
        print("\n🎉 Project setup completed successfully!")
        print("\n📝 Next steps:")
        print("1. Edit .env file with your API keys")
        print("2. Run: python src/main.py --init")
        print("3. Run: python src/main.py --test-mode")
    else:
        print(f"\n⚠️  {total_tasks - success_count} tasks failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()