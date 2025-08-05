import os, shutil
from pathlib import Path

def setup_public_directory(source_dir, dest_dir='public', clean=False):
    src = Path(source_dir)
    dest = Path(dest_dir)

    if not src.exists():
        raise FileNotFoundError(f"Source directory '{src}' does not exist")
    
    if not src.is_dir():
        raise NotADirectoryError(f"Source '{src}' is not a directory")
    
    if dest.exists() and clean:
        print(f"Cleaning destination directory: {dest}")
        if dest.is_dir():
            for item in dest.iterdir():
                if item.is_dir():
                    shutil.rmtree(item)
                    print(f"Removed directory: {item}")
                else:
                    item.unlink()
                    print(f"Removed file: {item}")
        else:
            dest.unlink()
            print(f"Removed file: {dest}")
    
    print(f'Create destination directory: {dest}')
    dest.mkdir(parents=True, exist_ok=True)

    files_copied = 0
    directories_created = 0
    
    for item in src.iterdir():
        dest_item = dest / item.name
        
        if item.is_dir():
            # Recursive case: create subdirectory and copy its contents
            dest_item.mkdir(exist_ok=True)
            print(f"Created directory: {dest_item}")
            directories_created += 1
            
            # Recursively copy subdirectory contents
            sub_files, sub_dirs = setup_public_directory(item, dest_item)
            files_copied += sub_files
            directories_created += sub_dirs
            
        else:
            # Base case: copy file
            shutil.copy2(item, dest_item)  # Preserves metadata
            print(f"Copied file: {item} -> {dest_item}")
            files_copied += 1
    
    return files_copied, directories_created

def main():
    setup_public_directory('static','public', True)

if __name__ == '__main__':
    main()