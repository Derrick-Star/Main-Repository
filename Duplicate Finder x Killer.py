import os
import hashlib

def get_file_hash(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def scan_counts(root_folder):
    total_files = 0
    total_folders = 0
    total_subfolders = 0

    for current_path, dirs, files in os.walk(root_folder):
        # Count folders
        total_folders += 1
        total_subfolders += len(dirs)

        # Count files
        total_files += len(files)

    return total_files, total_folders, total_subfolders


def find_duplicates(root_folder, total_files):
    seen = {}
    duplicates = []
    checked = 0

    for current_path, dirs, files in os.walk(root_folder):
        for file in files:
            file_path = os.path.join(current_path, file)

            if not os.path.isfile(file_path):
                continue

            checked += 1
            print(f"Checked {checked} out of {total_files} files", end="\r")

            try:
                file_hash = get_file_hash(file_path)
            except Exception:
                continue

            # Store only the filename (not full path)
            name_only = os.path.basename(file_path)

            if file_hash in seen:
                print(f"\nDuplicate found: {name_only}")
                duplicates.append(file_path)
            else:
                seen[file_hash] = name_only

    print()  # newline after progress bar
    return duplicates


folder = input("Folder path: ").strip()

if not os.path.isdir(folder):
    print("Directory not found.")
    exit()

# Scan once to count files + folders
total_files, total_folders, total_subfolders = scan_counts(folder)

print(f"\nFolder contains:")
print(f" - {total_files} files")
print(f" - {total_folders} folders")
print(f" - {total_subfolders} subfolders\n")

duplicates = find_duplicates(folder, total_files)

if not duplicates:
    print("\nNo duplicates found.")
    exit()

print("\nDuplicates detected:")
for d in duplicates:
    print(" -", os.path.basename(d))

confirm = input("\nDelete ALL duplicates? (y/n): ").lower().strip()

if confirm == "y":
    for d in duplicates:
        try:
            os.remove(d)
            print(f"Deleted: {os.path.basename(d)}")
        except Exception as e:
            print(f"Error deleting {os.path.basename(d)}: {e}")

    print("\nCleanup complete.")
else:
    print("\nOperation cancelled. No files were deleted.")