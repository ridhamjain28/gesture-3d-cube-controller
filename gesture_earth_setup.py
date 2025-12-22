"""
Project Setup Script
Creates the complete directory structure for gesture-earth-control project
"""
import os

# Create main project directory
base_dir = r"D:\Img projecy\gesture-earth-control"
os.makedirs(base_dir, exist_ok=True)

# Create subdirectories
directories = [
    "src",
    "tests",
    "docs",
    "web"
]

for directory in directories:
    path = os.path.join(base_dir, directory)
    os.makedirs(path, exist_ok=True)
    print(f"✓ Created: {path}")

print(f"\n✓ Project structure created at: {base_dir}")
print("\nNext step: Run this script to create directories, then files will be generated.")
