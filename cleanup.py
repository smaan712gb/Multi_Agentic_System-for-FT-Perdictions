import os
import shutil
import sys

def cleanup():
    """
    Clean up the data directory
    """
    data_dir = "data"
    
    if not os.path.exists(data_dir):
        print(f"Data directory '{data_dir}' does not exist. Nothing to clean up.")
        return
    
    print(f"This will delete all data in the '{data_dir}' directory.")
    print("Are you sure you want to continue? (y/n)")
    
    choice = input().lower()
    if choice != 'y':
        print("Cleanup cancelled.")
        return
    
    try:
        # Remove the data directory and all its contents
        shutil.rmtree(data_dir)
        print(f"Data directory '{data_dir}' has been deleted.")
    except Exception as e:
        print(f"Error deleting data directory: {e}")
        return
    
    # Recreate the data directory
    os.makedirs(data_dir, exist_ok=True)
    print(f"Empty data directory '{data_dir}' has been created.")

if __name__ == "__main__":
    cleanup()
