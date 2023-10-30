"""
Summary:
The script is designed to process a single TIF image stack, compute its focus measure using various methods,
and then save the computed images and measurements to specific directories. The focus measure methods available
include variance of Laplacian, standard deviation of intensity (with and without Gaussian blur), and the Sobel method.
The script also logs each step of the process. Results are saved both as images and as a CSV file containing focus measurements.
"""

# Import necessary libraries
import os  # Provides functions for interacting with the operating system.
import numpy as np  # Provides functions for numerical operations.
import cv2  # OpenCV, a library for computer vision tasks.
from skimage import io  # Provides functions for image reading and writing.
import csv  # Provides functions for reading from and writing to CSV files.
import logging  # Provides functions for logging.
import time  # Provides various time-related functions.

# Set up logging with specifications
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='focus_measure.log')

# Define the variance of Laplacian focus measure method
def variance_of_laplacian(frame):
    # Apply Gaussian blur to the frame
    img = cv2.GaussianBlur(frame,(3,3),0)
    # Compute the Laplacian of the blurred image
    laplacian = cv2.Laplacian(img, cv2.CV_64F)
    # Normalize the Laplacian image
    laplacian_normalized = cv2.normalize(laplacian, None, 0, 65535, cv2.NORM_MINMAX, cv2.CV_16U)
    return laplacian_normalized, laplacian.var()

# Define the Sobel focus measure method
def sobel_method(frame):
    # Apply Gaussian blur to the frame
    img = cv2.GaussianBlur(frame, (3,3), 0)
    # Compute the x-gradient and y-gradient using Sobel operator
    sobelx = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=5)
    sobely = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=5)
    # Compute the magnitude of the gradient
    magnitude = np.sqrt(sobelx**2 + sobely**2)
    # Normalize the magnitude image
    magnitude_normalized = cv2.normalize(magnitude, None, 0, 65535, cv2.NORM_MINMAX, cv2.CV_16U)
    return magnitude_normalized, magnitude.var()

# The Tenengrad method is another focus measure method, but it seems redundant with the Sobel method.

# Define the standard deviation of intensity focus measure method (without Gaussian blur)
def std_dev_of_intensity(frame):
    return None, np.std(frame)  # This method does not generate an image, only a focus value

# Define the standard deviation of intensity focus measure method (with Gaussian blur)
def std_dev_of_intensity_with_gauss(frame):
    # Apply Gaussian blur to the frame
    img = cv2.GaussianBlur(frame, (3,3), 0)
    return None, np.std(img)  # This method does not generate an image, only a focus value

# Function to compute focus measure based on the selected method
def compute_focus_measure(frame, method):
    # Determine the focus measure method and apply the corresponding function
    if method == 'variance_of_laplacian':
        return variance_of_laplacian(frame)
    elif method == 'std_dev_of_intensity':
        return std_dev_of_intensity(frame)
    elif method == 'std_dev_of_intensity_with_gauss':
        return std_dev_of_intensity_with_gauss(frame)
    elif method == 'sobel_method':
        return sobel_method(frame)
    else:
        raise ValueError(f"Unknown focus measure method: {method}")

# Save the computed image to a specified directory
def save_computed_image(image, method, stack_id, frame_num):
    # Define the output directory based on method and stack_id
    output_dir = f"./analysis/processed_images/{method}/{stack_id}"
    # Create the directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # Define the output path for the image
    output_path = os.path.join(output_dir, f"{stack_id}_{frame_num}.tif")
    # Save the image to the specified path
    if image is not None:
        io.imsave(output_path, image.astype(np.uint16))

# Function to process a single TIF stack and compute its focus measure using different methods
def process_single_tif_stack(stack_path, all_data):
    # Log the start of processing for the TIF stack
    logging.info(f"Processing TIF stack: {stack_path}")

    # Load the TIF stack into memory
    original_stack = io.imread(stack_path)
    logging.info(f"Read TIF stack with {len(original_stack)} frames.")

    # Placeholder names (can be adjusted as needed)
    stack_id = "sampled_sequence"

    # For each focus measure method, compute the focus measure for each frame in the TIF stack
    for method in focus_methods:
        computed_images_focus_values = [compute_focus_measure(frame, method) for frame in original_stack]

        for frame_num, (image, focus_value) in enumerate(computed_images_focus_values):
            logging.info(f"Processing frame {frame_num} for {stack_id} using {method}")
            save_computed_image(image, method, stack_id, frame_num)
            all_data.append({
                'stack_id': stack_id,
                'method': method,
                'frame': frame_num,
                'focus_measure': focus_value
            })

# Entry point of the script
if __name__ == "__main__":
    # List of focus measure methods to be used
    focus_methods = ['variance_of_laplacian', 'std_dev_of_intensity', 'std_dev_of_intensity_with_gauss', 'sobel_method']
    all_data = []

    # Process the TIF stack and compute its focus measure
    process_single_tif_stack("experiment_images/sampled_sequence.tif", all_data)

    # Define the directory for the output CSV file and create it if it doesn't exist
    output_csv_dir = './analysis/measurements/'
    if not os.path.exists(output_csv_dir):
        os.makedirs(output_csv_dir)

    # Save the computed focus measurements to a CSV file
    with open('./analysis/measurements/focus_measures.csv', 'w', newline='') as csvfile:
        fieldnames = ['stack_id', 'method', 'frame', 'focus_measure']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in all_data:
            writer.writerow(row)

    # Log completion of processing
    logging.info("Processing complete.")
