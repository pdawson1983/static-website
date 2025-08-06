import shutil, sys
from pathlib import Path
from mdhandler import generate_page

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

def generate_pages_recursive(content_dir, template_path, dest_dir, basepath):
    content_path = Path(content_dir)
    dest_path = Path(dest_dir)
    
    if not content_path.exists():
        raise FileNotFoundError(f"Content directory '{content_path}' does not exist")
    
    # Create destination directory if it doesn't exist
    dest_path.mkdir(parents=True, exist_ok=True)
    
    for item in content_path.iterdir():
        if item.is_dir():
            # Recursive case: process subdirectory
            sub_dest = dest_path / item.name
            generate_pages_recursive(item, template_path, sub_dest, basepath)
            
        elif item.suffix == '.md':
            # Base case: convert .md file to .html
            if item.name == 'index.md':
                # index.md becomes index.html
                html_file = dest_path / 'index.html'
            else:
                # other.md becomes other.html
                html_file = dest_path / f"{item.stem}.html"
            
            print(f"Generating: {item} -> {html_file}")
            generate_page(str(item), template_path, str(html_file), basepath)

def main():
    setup_public_directory('static','public', True)
    generate_pages_recursive('content', 'template.html', 'public', basepath)

if __name__ == '__main__':
    args = sys.argv
    if not args[1:]:
        basepath = '/'
    else:
        basepath = args[1]
    main()