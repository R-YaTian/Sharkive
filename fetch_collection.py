import zipfile
from pathlib import Path
from fetch import download_file_to_tmp, merge_cheats, cleanup_tmp


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
    downloaded = download_file_to_tmp("https://github.com/sthetix/nx-cheats-db/releases/latest/download/contents_complete.zip", "contents_complete.zip")
    if not downloaded:
        print("Error: Download failed")
        return

    # Extract contents_complete.zip
    print("="*50)
    print("Step 2: Extract contents_complete.zip")
    print("="*50)
    if not extract_contents_zip():
        print("Error: Extraction failed")
        return

    if not Path("tmp/contents").exists():
        print(f"Error: tmp/contents does not exist")
        return

    # Collect warning messages
    warnings = []

    print("\n" + "="*50)
    print("Step 3: Merge tmp/contents to titles folder")
    print("="*50)
    warnings = merge_cheats("tmp/contents", "titles")

    # Print all warnings at the end
    if warnings:
        print("\n" + "="*50)
        print("Warning Summary:")
        print("="*50)
        for warning in warnings:
            print(f"  ⚠ {warning}")
        print("="*50)

    print("\n" + "="*50)
    print("Step 4: Cleanup tmp folder")
    print("="*50)
    cleanup_tmp()


if __name__ == "__main__":
    main()
