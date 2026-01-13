import os

# Path to the target folder (change this to your actual pictures folder path)
target_folder = r'C:\Users\user\Pictures\BACKGROUND\RIBBONS & FRAMES'

# Change working directory to the target folder
os.chdir(target_folder)

# Rename the files inside that folder
for i, filename in enumerate(os.listdir()):
    ext = os.path.splitext(filename)[1]  # keep the file extension
    new_name = f"Ribbon & Frames_{i+1}{ext}"
    os.rename(filename, new_name)