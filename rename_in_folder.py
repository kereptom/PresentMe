import os
import re
import argparse


def rename_files_in_folder(folder_path, from_prefix, to_prefix):
    # List all files in the given folder
    files = os.listdir(folder_path)

    # Filter files that start with the 'from_prefix'
    target_files = [f for f in files if f.lower().startswith(from_prefix.lower())]

    # Sort the files to maintain order
    target_files.sort()

    # Create a regular expression pattern to extract numbers from the file names
    pattern = re.compile(r'(\d+)')

    # Rename the files
    for file_name in target_files:
        # Extract file extension
        _, file_extension = os.path.splitext(file_name)

        # Extract the number from the file name
        match = pattern.search(file_name)
        if match:
            number = match.group(1)
        else:
            print(f"Could not extract number from {file_name}. Skipping.")
            continue

        # Generate new name
        new_name = f"{to_prefix}{number}{file_extension}"

        # Compute old and new file paths
        old_path = os.path.join(folder_path, file_name)
        new_path = os.path.join(folder_path, new_name)

        # Rename the file
        os.rename(old_path, new_path)
        print(f"Renamed {file_name} to {new_name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rename all files in a folder based on specified prefixes.")
    parser.add_argument("-folder", required=True, help="Path to the folder containing files to rename.")
    parser.add_argument("-from", dest="from_prefix", required=True, help="Existing file prefix to replace.")
    parser.add_argument("-to", dest="to_prefix", required=True, help="New file prefix.")

    args = parser.parse_args()
    folder_path = args.folder
    from_prefix = args.from_prefix
    to_prefix = args.to_prefix

    if not os.path.isdir(folder_path):
        print(f"The path {folder_path} is not a valid directory.")
    else:
        rename_files_in_folder(folder_path, from_prefix, to_prefix)
