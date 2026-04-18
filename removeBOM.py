import os
from pathlib import Path

def remove_bom(file_path):
    """Remove UTF-8 BOM from file"""
    with open(file_path, 'rb') as f:
        data = f.read()

    # Check for UTF-8 BOM (0xEF 0xBB 0xBF)
    if data[:3] == b'\xef\xbb\xbf':
        data = data[3:]
        with open(file_path, 'wb') as f:
            f.write(data)
        print(f"Removed BOM from: {file_path}")

def walk(directory):
    """Recursively walk through directory and remove BOM from txt files"""
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.txt'):
                file_path = os.path.join(root, file)
                remove_bom(file_path)

if __name__ == "__main__":
    folder = Path("./switch")
    if folder.exists():
        walk(folder)
        print("✓ BOM removal completed")
    else:
        print(f"Error: {folder} does not exist")
