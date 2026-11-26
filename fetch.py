"""Fetch and merge cheat files."""

from pathlib import Path
import shutil


def merge_cheats(src_dir, dest_dir):
    """Merge cheats from src_dir into dest_dir in new-file mode."""
    src_switch_dir = Path(src_dir)
    dest_switch_dir = Path(dest_dir)

    # Collect warning messages and excluded folder names
    warnings = []
    excluded_folders = []

    if not src_switch_dir.exists():
        print(f"Error: {src_switch_dir} does not exist")
        return False

    try:
        print(f"Starting merge: {src_switch_dir} -> {dest_switch_dir}")
        dest_switch_dir.mkdir(parents=True, exist_ok=True)

        for title_dir in src_switch_dir.iterdir():
            if not title_dir.is_dir():
                continue

            folder_name = title_dir.name
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

            src_cheats_dir = title_dir / "cheats"
            if not src_cheats_dir.is_dir():
                msg = f"Warning: Folder '{folder_name}' does not have cheats subfolder, skipped"
                warnings.append(msg)
                excluded_folders.append(folder_name)
                continue

            dest_title_dir = dest_switch_dir / title_dir.name
            if not dest_title_dir.exists():
                dest_title_dir.mkdir(parents=True, exist_ok=True)

            dest_cheats_dir = dest_title_dir / "cheats"
            if not dest_cheats_dir.exists():
                dest_cheats_dir.mkdir(parents=True, exist_ok=True)
                print(f"Created folder: {title_dir.name}/cheats")

            for file_path in src_cheats_dir.iterdir():
                if not file_path.is_file():
                    continue

                dest_file = dest_cheats_dir / file_path.name
                if dest_file.exists():
                    continue

                # Get filename without extension
                name_without_ext = file_path.stem

                # Check if filename (without extension) length is 16 characters
                if len(name_without_ext) != 16:
                    msg = f"  Warning: File '{file_path.name}' (without extension) length is not 16 characters, skipped"
                    warnings.append(msg)
                    continue

                # Skip title cheat files whose build ID matches the title ID
                if name_without_ext.casefold() == folder_name.casefold():
                    msg = f"  Warning: {name_without_ext} is equal to title id, skipped"
                    warnings.append(msg)
                    continue

                if " " in name_without_ext:
                    msg = f"  Warning: {name_without_ext} -> This build id is invalid due to containing spaces"
                    warnings.append(msg)
                    continue

                shutil.copy2(file_path, dest_file)
                print(f"  Copied: {file_path.name}")

        print("✓ Merge completed")

        all_warnings = []
        # Print all warnings at the end
        if warnings:
            all_warnings.extend(warnings)
        if all_warnings:
            print("\n" + "="*50)
            print("Warning Summary:")
            print("="*50)
            for warning in all_warnings:
                print(f"  ⚠ {warning}")
            print("="*50)

        return True
    except OSError as exc:
        print(f"✗ Merge failed: {exc}")
        return False


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python fetch.py <src_dir> <dest_dir>")
        sys.exit(1)

    src_dir = sys.argv[1]
    dest_dir = sys.argv[2]
    success = merge_cheats(src_dir, dest_dir)
    if not success:
        sys.exit(1)
    else:
        sys.exit(0)
