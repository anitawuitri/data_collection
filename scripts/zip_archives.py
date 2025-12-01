import os
import shutil
import re

def zip_archives():
    base_dir = '/home/amditri/data_collection/data_archive'
    
    if not os.path.exists(base_dir):
        print(f"Directory {base_dir} does not exist.")
        return

    print(f"Zipping contents of {base_dir}...")

    for item in os.listdir(base_dir):
        item_path = os.path.join(base_dir, item)
        
        if os.path.isdir(item_path):
            # Check if it looks like a monthly archive or reports
            if re.match(r'\d{4}-\d{2}', item) or item == 'reports':
                zip_name = os.path.join(base_dir, item)
                print(f"Zipping {item} -> {item}.zip ...")
                shutil.make_archive(zip_name, 'zip', item_path)
                print(f"Done.")

if __name__ == "__main__":
    zip_archives()
