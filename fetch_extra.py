import os
import subprocess
import re
import shutil
from pathlib import Path
from fetch import get_proxy_config, merge_switch, check_switch, cleanup_tmp

def clone_mynxcheats():
    """Clone MyNXCheats repository to tmp folder with proxy configuration"""
    repo_url = "https://github.com/tomvita/MyNXCheats.git"
    tmp_dir = Path("tmp")
    clone_dir = tmp_dir / "MyNXCheats"

    # Create tmp folder if it doesn't exist
    tmp_dir.mkdir(parents=True, exist_ok=True)

    # Get proxy configuration
    proxies = get_proxy_config()

    try:
        print(f"Starting clone: {repo_url}")

        # Prepare git command
        clone_cmd = ["git", "clone", repo_url, str(clone_dir)]

        # Configure proxy for git if available
        env = os.environ.copy()
        if proxies:
            if 'https' in proxies:
                env['https_proxy'] = proxies['https']
                env['HTTPS_PROXY'] = proxies['https']
            if 'http' in proxies:
                env['http_proxy'] = proxies['http']
                env['HTTP_PROXY'] = proxies['http']

        # Execute git clone
        result = subprocess.run(
            clone_cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode == 0:
            print(f"✓ Clone completed: {clone_dir}")
            return True
        else:
            print(f"✗ Clone failed:")
            print(f"  stdout: {result.stdout}")
            print(f"  stderr: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("✗ Clone timeout (exceeded 300 seconds)")
        return False
    except Exception as e:
        print(f"✗ Clone error: {e}")
        return False

def process_mynxcheats_cheats():
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
                titleid_dir = switch_dir / titleid
                titleid_dir.mkdir(parents=True, exist_ok=True)

                # Copy txt file to titleid folder
                dest_file = titleid_dir / txt_file.name.lower()
                shutil.copy2(txt_file, dest_file)
                print(f"  Copied: {txt_file.name.lower()} -> {titleid}/{txt_file.name.lower()}")

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
    print("Step 1: Clone MyNXCheats repository")
    print("="*50)
    clone_mynxcheats()

    print("\n" + "="*50)
    print("Step 2: Process MyNXCheats cheats files")
    print("="*50)
    warnings = process_mynxcheats_cheats()

    print("\n" + "="*50)
    print("Step 3: Merge tmp/switch to project switch")
    print("="*50)
    merge_switch()

    print("\n" + "="*50)
    print("Step 4: Check switch folder")
    print("="*50)
    check_warnings = check_switch()

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
    print("Step 5: Cleanup tmp folder")
    print("="*50)
    cleanup_tmp()

if __name__ == "__main__":
    main()
