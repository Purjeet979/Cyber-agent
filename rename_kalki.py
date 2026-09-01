import os
import shutil

def find_replace(directory, old_text, new_text, match_case=True):
    for root, dirs, files in os.walk(directory):
        if '.venv' in root or '.git' in root or '__pycache__' in root:
            continue
        for file in files:
            if file.endswith(('.py', '.html', '.css', '.js', '.toml', '.md', '.log')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if old_text in content:
                        new_content = content.replace(old_text, new_text)
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f"Updated {filepath}")
                except Exception as e:
                    print(f"Failed to read/write {filepath}: {e}")

if __name__ == "__main__":
    base_dir = r"e:\Cyber\kalki"
    
    # 1. Rename folder
    src_folder = os.path.join(base_dir, "src", "kalki")
    dst_folder = os.path.join(base_dir, "src", "kalki")
    
    if os.path.exists(src_folder) and not os.path.exists(dst_folder):
        print(f"Renaming {src_folder} to {dst_folder}")
        os.rename(src_folder, dst_folder)
        
    # 2. String replacements
    find_replace(base_dir, "kalki", "kalki")
    find_replace(base_dir, "Kalki", "Kalki")
    
    print("Renaming complete.")
