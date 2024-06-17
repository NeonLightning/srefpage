from PIL import Image
import os
import concurrent.futures
import threading

# Global variables for tracking progress and truncated images
global processed_count, total_count, truncated_images
processed_count = 0
total_count = 0
truncated_images = []
lock = threading.Lock()

def convert_to_interlaced(file_path):
    global processed_count, truncated_images
    try:
        with Image.open(file_path) as img:
            img = img.convert("RGBA")
            output_path = file_path
            img.save(output_path, optimize=True, interlace=True)
            print(f"Processed {processed_count}/{total_count} images.")
            with lock:
                processed_count += 1
    except Exception as e:
        print(f"Error converting {os.path.basename(file_path)}: {e}")
        with lock:
            truncated_images.append(os.path.basename(file_path))

def process_images_in_folder(folder_path, max_workers=None):
    global total_count
    files_to_process = [os.path.join(folder_path, filename) for filename in os.listdir(folder_path)
                        if filename.lower().endswith((".png", ".jpg", ".jpeg"))]
    total_count = len(files_to_process)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(convert_to_interlaced, files_to_process)

    print("Processing complete.")

    if truncated_images:
        print("Truncated images:")
        for filename in truncated_images:
            print(filename)

folder_path = "/home/neonbot/midjourney/images"  # Replace with the path to your folder
max_workers = 4  # Set to the desired number of threads, or None to use the default
process_images_in_folder(folder_path, max_workers=max_workers)
