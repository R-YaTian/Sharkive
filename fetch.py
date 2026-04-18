import os
import json
import requests
import shutil
from pathlib import Path

# Cheat buildid blacklist
CHEAT_BUILDID_BLACKLIST = [
    "448e0f0e1c1cbade",
    "9e47489ddafa3530"
]

def get_proxy_config():
    """Get proxy configuration from environment variables"""
    proxies = {}

    # Check http_proxy environment variable
    http_proxy = os.getenv('http_proxy') or os.getenv('HTTP_PROXY')
    if http_proxy:
        proxies['http'] = http_proxy
        print(f"Using http_proxy: {http_proxy}")

    # Check https_proxy environment variable
    https_proxy = os.getenv('https_proxy') or os.getenv('HTTPS_PROXY')
    if https_proxy:
        proxies['https'] = https_proxy
        print(f"Using https_proxy: {https_proxy}")

    return proxies if proxies else None

def download_file_to_tmp(url, dest_name):
    output_dir = Path("tmp")
    output_file = output_dir / dest_name

    # Create tmp folder if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        print(f"Starting download: {url}")

        # Get proxy configuration
        proxies = get_proxy_config()

        # Download file
        response = requests.get(url, proxies=proxies, timeout=30)
        response.raise_for_status()

        # Save file
        with open(output_file, 'wb') as f:
            f.write(response.content)

        print(f"✓ Download completed: {output_file}")
        print(f"  File size: {output_file.stat().st_size / (1024*1024):.2f} MB")
        return True

    except requests.exceptions.RequestException as e:
        print(f"✗ Download failed: {e}")
        return False

def parse_cheats_json():
    """Parse cheats.json and create directory structure and txt files"""
    cheats_file = Path("tmp/cheats.json")
    switch_dir = Path("tmp/switch")
    warnings = []

    if not cheats_file.exists():
        print(f"Error: {cheats_file} does not exist")
        return False

    try:
        print(f"Starting to parse: {cheats_file}")

        # Create switch directory if it doesn't exist
        switch_dir.mkdir(parents=True, exist_ok=True)

        # Load JSON file
        with open(cheats_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Traverse all objects in the root node
        for title_key, title_object in data.items():
            # Check if key starts with 0100
            if not title_key.startswith("0100"):
                warnings.append(f"Title key '{title_key}' does not start with 0100, skipped")
                continue

            # Check if key length is 16 characters
            if len(title_key) != 16:
                warnings.append(f"Title key '{title_key}' length is not 16 characters, skipped")
                continue

            # Create folder with title key name
            title_dir = switch_dir / title_key
            title_dir.mkdir(parents=True, exist_ok=True)
            print(f"Processing title: {title_key}")

            # If title_object is not a dict, skip
            if not isinstance(title_object, dict):
                continue

            # Traverse all sub-objects
            for cheat_key, cheat_object in title_object.items():
                # Check if cheat key is in blacklist
                if cheat_key.lower() in CHEAT_BUILDID_BLACKLIST:
                    warnings.append(f"Cheat key '{cheat_key}' under title '{title_key}' is in blacklist, skipped")
                    continue

                # Check if cheat key length is 16 characters
                if len(cheat_key) != 16:
                    warnings.append(f"Cheat key '{cheat_key}' under title '{title_key}' length is not 16 characters, skipped")
                    continue

                # Create txt file with lowercase key
                txt_file = title_dir / f"{cheat_key.lower()}.txt"
                with open(txt_file, 'w', encoding='utf-8') as f:
                    # Parse cheat content
                    if isinstance(cheat_object, dict):
                        content_lines = []
                        for item_key, item_object in cheat_object.items():
                            if isinstance(item_object, dict) and 'title' in item_object and 'source' in item_object:
                                title_content = item_object['title']
                                source_content = item_object['source']
                                content_lines.append(f"{title_content}\n{source_content}\n")
                        f.write('\n'.join(content_lines))
                    else:
                        f.write(str(cheat_object))

                print(f"  Created: {cheat_key.lower()}.txt")

        print(f"✓ Parsing completed")
        return warnings

    except json.JSONDecodeError as e:
        print(f"✗ JSON parsing failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def merge_switch():
    """Merge tmp/switch to project switch folder in new file mode"""
    tmp_switch_dir = Path("tmp/switch")
    project_switch_dir = Path("switch")

    if not tmp_switch_dir.exists():
        print(f"Error: {tmp_switch_dir} does not exist")
        return False

    try:
        print(f"Starting merge: {tmp_switch_dir} -> {project_switch_dir}")

        # Create project switch directory if it doesn't exist
        project_switch_dir.mkdir(parents=True, exist_ok=True)

        # Traverse all folders and files in tmp/switch
        for title_dir in tmp_switch_dir.iterdir():
            if not title_dir.is_dir():
                continue

            title_name = title_dir.name
            project_title_dir = project_switch_dir / title_name

            # Create title folder in project if it doesn't exist
            if not project_title_dir.exists():
                project_title_dir.mkdir(parents=True, exist_ok=True)
                print(f"Created folder: {title_name}")

            # Copy files from tmp to project (only new files)
            for file_path in title_dir.iterdir():
                if file_path.is_file():
                    dest_file = project_title_dir / file_path.name

                    # Only copy if file doesn't exist
                    if not dest_file.exists():
                        shutil.copy2(file_path, dest_file)
                        print(f"  Copied: {file_path.name}")

        print(f"✓ Merge completed")
        return True

    except Exception as e:
        print(f"✗ Merge failed: {e}")
        return False

def check_switch():
    """Check project switch folder for naming validity"""
    project_switch_dir = Path("switch")
    warnings = []

    if not project_switch_dir.exists():
        print(f"Warning: {project_switch_dir} does not exist")
        return warnings

    try:
        print(f"Starting check: {project_switch_dir}")

        # Traverse all folders and files
        for item in project_switch_dir.rglob("*"):
            # Check folder names
            if item.is_dir():
                if len(item.name) != 16:
                    warnings.append(f"Folder '{item.name}' length is not 16 characters")

            # Check file names (without extension)
            elif item.is_file():
                name_without_ext = item.stem
                if len(name_without_ext) != 16:
                    warnings.append(f"File '{item.name}' (without extension) length is not 16 characters")

        print(f"✓ Check completed")
        return warnings

    except Exception as e:
        print(f"✗ Check failed: {e}")
        return []

def cleanup_tmp():
    """Clean up the tmp folder and all its contents"""
    tmp_dir = Path("tmp")

    try:
        if tmp_dir.exists():
            print(f"Cleaning up: {tmp_dir}")
            shutil.rmtree(tmp_dir)
            print(f"✓ Cleanup completed")
            return True
        else:
            print(f"Warning: {tmp_dir} does not exist, skipped cleanup")
            return True

    except Exception as e:
        print(f"✗ Cleanup failed: {e}")
        return False

def main():
    print("="*50)
    print("Step 1: Download cheats.json")
    print("="*50)
    download_file_to_tmp("https://github.com/blawar/titledb/raw/refs/heads/master/cheats.json", "cheats.json")

    print("\n" + "="*50)
    print("Step 2: Parse cheats.json and create structure")
    print("="*50)
    parse_warnings = parse_cheats_json()

    print("\n" + "="*50)
    print("Step 3: Merge tmp/switch to project switch")
    print("="*50)
    merge_switch()

    print("\n" + "="*50)
    print("Step 4: Check switch folder")
    print("="*50)
    check_warnings = check_switch()

    # Collect all warnings
    all_warnings = []
    if isinstance(parse_warnings, list):
        all_warnings.extend(parse_warnings)
    if isinstance(check_warnings, list):
        all_warnings.extend(check_warnings)

    # Print all warnings at the end
    if all_warnings:
        print("\n" + "="*50)
        print("Warning Summary:")
        print("="*50)
        for warning in all_warnings:
            print(f"  ⚠ {warning}")
        print("="*50)

    print("\n" + "="*50)
    print("Step 5: Cleanup tmp folder")
    print("="*50)
    cleanup_tmp()

if __name__ == "__main__":
    main()
