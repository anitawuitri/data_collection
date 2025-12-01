import os
import shutil
import argparse
from datetime import datetime, timedelta
import re
from pathlib import Path

def parse_arguments():
    parser = argparse.ArgumentParser(description='Archive data for a specific month.')
    parser.add_argument('--month', type=str, help='Target month to archive (YYYY-MM). Defaults to previous month.')
    parser.add_argument('--dry-run', action='store_true', help='Simulate the archive process without moving files.')
    return parser.parse_args()

def get_previous_month():
    today = datetime.today()
    first = today.replace(day=1)
    last_month = first - timedelta(days=1)
    return last_month.strftime('%Y-%m')

def get_month_str(date_str):
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%Y-%m')
    except ValueError:
        return None

def is_target_month(date_str, target_month):
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%Y-%m') == target_month
    except ValueError:
        return False

def archive_node_data(base_dir, archive_base, target_month, dry_run):
    print(f"Scanning node data in {base_dir} for month {target_month}...")
    colab_dirs = [d for d in os.listdir(base_dir) if d.startswith('colab-gpu')]
    
    for colab_dir in colab_dirs:
        colab_path = os.path.join(base_dir, colab_dir)
        if not os.path.isdir(colab_path):
            continue
            
        # Iterate through date directories
        for date_dir in os.listdir(colab_path):
            date_path = os.path.join(colab_path, date_dir)
            if not os.path.isdir(date_path):
                continue
                
            # Check if directory name is a date
            if not re.match(r'\d{4}-\d{2}-\d{2}', date_dir):
                continue
                
            if is_target_month(date_dir, target_month):
                target_dir = os.path.join(archive_base, target_month, colab_dir)
                target_path = os.path.join(target_dir, date_dir)
                
                if dry_run:
                    print(f"[DRY RUN] Would move {date_path} to {target_path}")
                else:
                    os.makedirs(target_dir, exist_ok=True)
                    print(f"Moving {date_path} to {target_path}")
                    shutil.move(date_path, target_path)

def archive_reports(reports_dir, archive_reports_dir, target_month, dry_run):
    print(f"Scanning reports in {reports_dir} for month {target_month}...")
    if not os.path.exists(reports_dir):
        print(f"Reports directory {reports_dir} does not exist.")
        return

    for filename in os.listdir(reports_dir):
        file_path = os.path.join(reports_dir, filename)
        if not os.path.isfile(file_path):
            continue
            
        # Extract dates from filename
        # Pattern: ...YYYY-MM-DD... or ...YYYY-MM-DD_to_YYYY-MM-DD...
        dates = re.findall(r'\d{4}-\d{2}-\d{2}', filename)
        
        should_move = False
        if dates:
            # If range, check the end date. If single date, check that date.
            # We use the last date found in the filename.
            last_date = dates[-1]
            if is_target_month(last_date, target_month):
                should_move = True
        
        if should_move:
            target_path = os.path.join(archive_reports_dir, target_month, filename)
            if dry_run:
                print(f"[DRY RUN] Would move {file_path} to {target_path}")
            else:
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                print(f"Moving {file_path} to {target_path}")
                shutil.move(file_path, target_path)

def main():
    args = parse_arguments()
    
    target_month = args.month if args.month else get_previous_month()
    
    base_dir = '/app/data' # Inside Docker container
    archive_base = '/app/data_archive' # Inside Docker container
    
    # Fallback to local paths if not in Docker (for testing)
    if not os.path.exists(base_dir):
        base_dir = os.path.join(os.getcwd(), 'data')
        archive_base = os.path.join(os.getcwd(), 'data_archive')

    print(f"Starting archive process for {target_month} (Dry Run: {args.dry_run})")
    print(f"Source: {base_dir}")
    print(f"Destination: {archive_base}")
    
    archive_node_data(base_dir, archive_base, target_month, args.dry_run)
    archive_reports(os.path.join(base_dir, 'reports'), os.path.join(archive_base, 'reports'), target_month, args.dry_run)
    
    print("Archive process completed.")

if __name__ == "__main__":
    main()
