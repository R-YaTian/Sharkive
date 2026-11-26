from pathlib import Path
import subprocess
import shutil
import stat
import os


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


def clone_repo_to_tmp(repo_url, repo_name):
    """Clone git repository to tmp folder with proxy configuration"""
    tmp_dir = Path("tmp")
    clone_dir = tmp_dir / repo_name

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


def download_file_to_tmp(url, dest_name):
    import requests
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


def merge_cheats(src_dir, dest_dir):
    """Merge cheats from src_dir into dest_dir in new-file mode."""
    src_switch_dir = Path(src_dir)
    dest_switch_dir = Path(dest_dir)

    # Collect warning messages
    warnings = []

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
                continue

            # Check if folder name length is 16 characters
            if len(folder_name) != 16:
                msg = f"Warning: Folder '{folder_name}' length is not 16 characters, skipped"
                warnings.append(msg)
                continue

            src_cheats_dir = title_dir / "cheats"
            if not src_cheats_dir.is_dir():
                msg = f"Warning: Folder '{folder_name}' does not have cheats subfolder, skipped"
                warnings.append(msg)
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

        return warnings
    except OSError as exc:
        print(f"✗ Merge failed: {exc}")
        return []


def cleanup_tmp():
    """Clean up the tmp folder and all its contents"""
    tmp_dir = Path("tmp")

    def handle_remove_readonly(func, path, exc):
        os.chmod(path, stat.S_IWRITE)
        func(path)

    try:
        if tmp_dir.exists():
            print(f"Cleaning up: {tmp_dir}")
            shutil.rmtree(tmp_dir, onerror=handle_remove_readonly)
            print(f"✓ Cleanup completed")
            return True
        else:
            print(f"Warning: {tmp_dir} does not exist, skipped cleanup")
            return True

    except Exception as e:
        print(f"✗ Cleanup failed: {e}")
        return False
