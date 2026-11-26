import re
from shutil import copy2
from pathlib import Path
from fetch import clone_repo_to_tmp, merge_cheats, cleanup_tmp


def process_tomvita_cheats():
    """Process txt files in tmp/MyNXCheats/cheats folder"""
    cheats_dir = Path("tmp/MyNXCheats/cheats")
    switch_dir = Path("tmp/switch")
    warnings = []

    if not cheats_dir.exists():
        print(f"Warning: {cheats_dir} does not exist")
        return warnings

    # Create tmp/switch if it doesn't exist
    switch_dir.mkdir(parents=True, exist_ok=True)

    try:
        print(f"Starting to process: {cheats_dir}")

        # Traverse all files in cheats folder
        for txt_file in cheats_dir.rglob("*.txt"):
            # Get filename without extension
            name_without_ext = txt_file.stem

            # Check if filename length is 16 characters
            if len(name_without_ext) != 16:
                continue

            # Skip filenames containing spaces
            if " " in name_without_ext:
                continue

            try:
                # Read first line of the file
                with open(txt_file, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()

                # Search for TID pattern (case-insensitive)
                tid_match = re.search(r'tid:\s*(.{16})', first_line, re.IGNORECASE)

                if not tid_match:
                    msg = f"Warning: File '{txt_file.name}' - TID pattern not found in first line"
                    warnings.append(msg)
                    continue

                # Extract TID (16 characters after TID:)
                titleid = tid_match.group(1).strip()

                # Verify TID length is 16
                if len(titleid) != 16:
                    msg = f"Warning: File '{txt_file.name}' - TID '{titleid}' length is not 16"
                    warnings.append(msg)
                    continue

                # Check if TID starts with 0100
                if not titleid.startswith("0100"):
                    msg = f"Warning: File '{txt_file.name}' - TID '{titleid}' does not start with 0100"
                    warnings.append(msg)
                    continue

                # Create titleid folder in tmp/switch
                titleid_dir = switch_dir / titleid / "cheats"
                titleid_dir.mkdir(parents=True, exist_ok=True)

                # Copy txt file to titleid folder
                dest_file = titleid_dir / txt_file.name.lower()
                copy2(txt_file, dest_file)
                print(f"  Copied: {txt_file.name.lower()} -> {titleid}/cheats/{txt_file.name.lower()}")

            except Exception as e:
                msg = f"Warning: File '{txt_file.name}' - Error processing: {e}"
                warnings.append(msg)
                continue

        print(f"✓ Processing completed")
        return warnings

    except Exception as e:
        print(f"✗ Processing failed: {e}")
        return []


def main():
    print("="*50)
    print("Step 1: Clone tomvita's MyNXCheats repository")
    print("="*50)
    clone_repo_to_tmp("https://github.com/tomvita/MyNXCheats.git", "MyNXCheats")

    print("\n" + "="*50)
    print("Step 2: Process cheats files")
    print("="*50)
    warnings = process_tomvita_cheats()

    print("\n" + "="*50)
    print("Step 3: Merge tmp/switch to titles folder")
    print("="*50)
    check_warnings = merge_cheats("tmp/switch", "titles")

    if isinstance(check_warnings, list):
        warnings.extend(check_warnings)

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
