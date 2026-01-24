#!/usr/bin/env python3
"""Test runner script for the inventory management system."""

import sys
import subprocess
from pathlib import Path


def run_command(command, description):
    """Run a command and return success status."""
    print(f"\n🔄 {description}")
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True)
    if result.returncode == 0:
        print(f"✅ {description} completed successfully")
        return True
    else:
        print(f"❌ {description} failed")
        return False


def main():
    """Main test runner function."""
    # Change to project root directory
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    print("🚀 Inventory Management API - Test Runner")
    print("=" * 50)
    
    # Check if we're in a virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    # Use virtual environment pytest if available
    venv_pytest = project_root / "venv" / "bin" / "pytest"
    if venv_pytest.exists():
        pytest_cmd = str(venv_pytest)
        print(f"✅ Using virtual environment pytest: {pytest_cmd}")
    elif in_venv:
        pytest_cmd = "pytest"
        print("✅ Using pytest from active virtual environment")
    else:
        pytest_cmd = "pytest"
        print("⚠️  Warning: Using system pytest (virtual environment not detected)")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Exiting...")
            return
    
    # Install dependencies if needed
    if len(sys.argv) > 1 and sys.argv[1] == "--install":
        pip_cmd = str(project_root / "venv" / "bin" / "pip") if venv_pytest.exists() else "pip"
        if not run_command(f"{pip_cmd} install -r requirements-dev.txt", "Installing dependencies"):
            return
    
    # Run tests
    test_commands = {
        "unit": (f"{pytest_cmd} -m 'not integration' -v", "Running unit tests"),
        "integration": (f"{pytest_cmd} -m integration -v", "Running integration tests"),
        "all": (f"{pytest_cmd} -v", "Running all tests"),
        "coverage": (f"{pytest_cmd} --cov=app --cov-report=term-missing", "Running tests with coverage"),
    }
    
    # Determine which tests to run
    test_type = "all"
    if len(sys.argv) > 1 and sys.argv[-1] in test_commands:
        test_type = sys.argv[-1]
    
    command, description = test_commands[test_type]
    
    success = run_command(command, description)
    
    if success:
        print("\n🎉 All tests passed!")
        
        # Optionally run code quality checks
        if "--quality" in sys.argv:
            print("\n🔍 Running code quality checks...")
            run_command("black --check app/ tests/", "Checking code formatting")
            run_command("isort --check-only app/ tests/", "Checking import formatting")
            run_command("flake8 app/ tests/", "Running flake8 linter")
            
    else:
        print("\n💥 Tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()