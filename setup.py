# Run this in VS Code Python Interactive Window
from pathlib import Path
import os

# Test path creation
test_dir = Path("poc") / "results"
print(f"Path: {test_dir}")
print(f"Exists before: {test_dir.exists()}")

test_dir.mkdir(parents=True, exist_ok=True)
print(f"Exists after: {test_dir.exists()}")

# Check current directory
print(f"CWD: {os.getcwd()}")