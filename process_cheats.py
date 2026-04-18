import os
import shutil
import requests
import zipfile
from pathlib import Path
from fetch import download_file_to_tmp, merge_switch, check_switch, cleanup_tmp, CHEAT_BUILDID_BLACKLIST

def extract_contents_zip():
    """Extract contents_complete.zip to tmp folder"""
    zip_file = Path("tmp/contents_complete.zip")
    output_dir = Path("tmp")

    if not zip_file.exists():
        print(f"Error: {zip_file} does not exist")
        return False

    try:
        print(f"Starting extraction: {zip_file}")

        # Extract zip file
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(output_dir)

        print(f"✓ Extraction completed")
        return True

    except zipfile.BadZipFile as e:
        print(f"✗ Invalid zip file: {e}")
        return False
    except Exception as e:
        print(f"✗ Extraction failed: {e}")
        return False

def main():
    # Download contents_complete.zip
    print("="*50)
    print("Step 1: Download contents_complete.zip")
    print("="*50)
    download_file_to_tmp("https://github.com/HamletDuFromage/switch-cheats-db/releases/latest/download/contents_complete.zip", "contents_complete.zip")

    # Extract contents_complete.zip
    print("="*50)
    print("Step 2: Extract contents_complete.zip")
    print("="*50)
    extract_contents_zip()

    print("\n" + "="*50)
    print("Step 3: Process titles")
    print("="*50)

    # Define target directory
    titles_dir = Path("tmp/contents")

    # Collect warning messages and excluded folder names
    warnings = []
    excluded_folders = []

    if not titles_dir.exists():
        print(f"Error: {titles_dir} does not exist")
        return

    # Traverse all folders in titles folder
    for item in titles_dir.iterdir():
        if not item.is_dir():
            continue

        folder_name = item.name

        # Check if starts with 0100
        if not folder_name.startswith("0100"):
            msg = f"Warning: Folder '{folder_name}' does not start with 0100, skipped"
            warnings.append(msg)
            excluded_folders.append(folder_name)
            continue

        # Check if folder name length is 16 characters
        if len(folder_name) != 16:
            msg = f"Warning: Folder '{folder_name}' length is not 16 characters, skipped"
            warnings.append(msg)
            excluded_folders.append(folder_name)
            continue

        # Check if cheats folder exists
        cheats_dir = item / "cheats"
        if not cheats_dir.exists():
            msg = f"Warning: Folder '{folder_name}' does not have cheats subfolder, skipped"
            warnings.append(msg)
            excluded_folders.append(folder_name)
            continue

        print(f"Processing folder: {folder_name}")

        # Delete all txt files at the same level as cheats folder
        txt_files = list(item.glob("*.txt"))
        for txt_file in txt_files:
            print(f"  Delete txt file: {txt_file.name}")
            txt_file.unlink()

        # Move all files from cheats folder to parent folder
        for file_or_dir in cheats_dir.iterdir():
            # Get filename without extension
            name_without_ext = file_or_dir.stem

            # Check if filename (without extension) is in blacklist
            if name_without_ext.lower() in CHEAT_BUILDID_BLACKLIST:
                msg = f"  Warning: File '{file_or_dir.name}' (without extension) is in blacklist, not moved"
                warnings.append(msg)
                continue

            # Check if filename (without extension) length is 16 characters
            if len(name_without_ext) != 16:
                msg = f"  Warning: File '{file_or_dir.name}' (without extension) length is not 16 characters, not moved"
                warnings.append(msg)
                continue

            dest = item / file_or_dir.name.lower()
            # If target already exists, delete it first
            if dest.exists():
                if dest.is_dir():
                    shutil.rmtree(dest)
                else:
                    dest.unlink()
            # Move file
            shutil.move(str(file_or_dir), str(dest))
            print(f"  Moved: {file_or_dir.name.lower()}")

        # Delete cheats folder
        shutil.rmtree(cheats_dir)
        print(f"  Delete cheats folder")

    # Delete excluded folders
    if excluded_folders:
        print("\n" + "="*50)
        print("Step 4: Delete excluded folders")
        print("="*50)
        for folder_name in excluded_folders:
            folder_path = titles_dir / folder_name
            if folder_path.exists():
                shutil.rmtree(folder_path)
                print(f"Deleted: {folder_name}")

    # Rename contents folder to switch
    print("\n" + "="*50)
    print("Step 5: Rename contents to switch")
    print("="*50)
    contents_dir = Path("tmp/contents")
    switch_dir = Path("tmp/switch")

    if contents_dir.exists():
        if switch_dir.exists():
            shutil.rmtree(switch_dir)
        contents_dir.rename(switch_dir)
        print(f"✓ Renamed: tmp/contents -> tmp/switch")

    print("\n" + "="*50)
    print("Step 6: Merge tmp/switch to project switch")
    print("="*50)
    merge_switch()

    print("\n" + "="*50)
    print("Step 7: Check switch folder")
    print("="*50)
    check_warnings = check_switch()

    # Collect all warnings
    all_warnings = []
    if isinstance(warnings, list):
        all_warnings.extend(warnings)
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
    print("Step 8: Cleanup tmp folder")
    print("="*50)
    cleanup_tmp()

if __name__ == "__main__":
    main()
