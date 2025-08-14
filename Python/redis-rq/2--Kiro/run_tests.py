#!/usr/bin/env python3
"""
Test runner script for the accounting automation backend.
"""

import sys
import subprocess
from pathlib import Path


def run_tests():
    """Run the test suite."""
    # Change to project root directory
    project_root = Path(__file__).parent
    
    # Run pytest with coverage
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/unit/",
        "-v",
        "--tb=short",
        "--color=yes"
    ]
    
    print("Running unit tests...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, cwd=project_root, check=False)
        return result.returncode
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)