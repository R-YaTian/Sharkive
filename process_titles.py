import os
import shutil
import zipfile
from pathlib import Path
from fetch import cleanup_tmp

def main():
    # Get the project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))

    # Define paths
    tmp_dir = os.path.join(project_root, "tmp")
    titles_dir = os.path.join(tmp_dir, "titles")
    switch_dir = os.path.join(project_root, "switch")
    build_dir = os.path.join(project_root, "build")
    zip_path = os.path.join(build_dir, "titles.zip")

    print("Starting processing...")

    # 1. Create tmp directory (if it does not exist)
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
        print(f"✓ Created tmp directory: {tmp_dir}")

    # 2. Delete titles directory if it already exists
    if os.path.exists(titles_dir):
        shutil.rmtree(titles_dir)
        print(f"✓ Deleted existing titles directory")

    # 3. Copy switch folder to titles
    shutil.copytree(switch_dir, titles_dir)
    print(f"✓ Copied switch directory to {titles_dir}")

    # 4. Traverse all subfolders in titles folder
    for item in os.listdir(titles_dir):
        item_path = os.path.join(titles_dir, item)

        # Only process directories
        if os.path.isdir(item_path):
            # Create cheats subfolder
            cheats_dir = os.path.join(item_path, "cheats")
            if not os.path.exists(cheats_dir):
                os.makedirs(cheats_dir)
                print(f"  ✓ Created cheats folder for {item}")

            # Move all .txt files to cheats folder
            txt_files = [f for f in os.listdir(item_path) if f.endswith('.txt')]
            for txt_file in txt_files:
                src_path = os.path.join(item_path, txt_file)
                dst_path = os.path.join(cheats_dir, txt_file)
                shutil.move(src_path, dst_path)

            if txt_files:
                print(f"  ✓ Moved {len(txt_files)} .txt files to {item}/cheats")

    # 5. Perform highest compression ratio zip on titles folder
    print("\nStarting compression...")

    # Delete existing zip file
    if os.path.exists(zip_path):
        os.remove(zip_path)
        print(f"✓ Deleted existing zip file")

    # Create zip file with highest compression ratio
    def zipdir(folder_path, zip_file):
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(folder_path))
                zip_file.write(file_path, arcname)

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
        zipdir(titles_dir, zipf)

    print(f"✓ Created zip file: {zip_path}")

    # Display compressed file size
    zip_size = os.path.getsize(zip_path)
    print(f"✓ Compressed file size: {zip_size / (1024*1024):.2f} MB")

    # Delete tmp folder
    cleanup_tmp()

    print("\nProcessing completed!")

if __name__ == "__main__":
    main()
