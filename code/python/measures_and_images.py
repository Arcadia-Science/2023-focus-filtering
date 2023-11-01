"""
Summary:
The script is designed to process a single TIF image stack,
compute its focus measure using various methods,
and then save the computed images and measurements to specific directories.
The focus measure methods available
include variance of Laplacian, standard deviation of intensity
(with and without Gaussian blur), and the Sobel method.
The script also logs each step of the process.
Results are saved both as images and as a CSV file containing focus measurements.
"""

import csv
import logging
import os
import cv2
import numpy as np

from skimage import io

ALL_FOCUS_METHODS = [
    'variance_of_laplacian',
    'std_dev_of_intensity_without_blur',
    'std_dev_of_intensity_with_blur',
    'sobel_method',
]


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='focus-filter.log',
)


def variance_of_laplacian(frame):
    '''
    The variance-of-Laplacian focus measure method
    '''
    img = cv2.GaussianBlur(frame, (3, 3), 0)

    # Compute the Laplacian of the blurred image
    laplacian = cv2.Laplacian(img, cv2.CV_64F)

    # Normalize the Laplacian image
    laplacian_normalized = cv2.normalize(
        laplacian, None, 0, 65535, cv2.NORM_MINMAX, cv2.CV_16U
    )
    return laplacian_normalized, laplacian.var()


def sobel_method(frame):
    '''
    the varianc-of-sobel focus measure method
    '''
    img = cv2.GaussianBlur(frame, (3, 3), 0)

    # Compute the x-gradient and y-gradient using Sobel operator
    sobelx = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=5)
    sobely = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=5)

    # Compute the magnitude of the gradient
    magnitude = np.sqrt(sobelx**2 + sobely**2)

    # Normalize the magnitude image
    magnitude_normalized = cv2.normalize(
        magnitude, None, 0, 65535, cv2.NORM_MINMAX, cv2.CV_16U
    )
    return magnitude_normalized, magnitude.var()


def std_dev_of_intensity(frame, blur=False):
    '''
    the standard deviation of intensity as a focus measure method
    (with or without Gaussian blur)
    '''
    if blur:
        frame = cv2.GaussianBlur(frame, (3, 3), 0)
    return None, np.std(frame)


def compute_focus_measure(frame, method):
    '''
    compute the focus measure for the specified method
    '''
    if method == 'variance_of_laplacian':
        return variance_of_laplacian(frame)
    elif method == 'std_dev_of_intensity_without_blur':
        return std_dev_of_intensity(frame, blur=False)
    elif method == 'std_dev_of_intensity_with_blur':
        return std_dev_of_intensity(frame, blur=True)
    elif method == 'sobel_method':
        return sobel_method(frame)
    else:
        raise ValueError(f"Unknown focus measure method: {method}")


def save_computed_image(image, method, stack_id, frame_num):
    '''
    write the computed image to an output directory
    '''
    output_dir = f"./analysis/processed_images/{method}/{stack_id}"
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, f"{stack_id}_{frame_num}.tif")

    if image is not None:
        io.imsave(output_path, image.astype(np.uint16))


def process_single_tif_stack(stack_path):
    '''
    Calculate all of the focus measures for each frame of the stack
    '''
    logging.info(f"Processing TIF stack: {stack_path}")

    original_stack = io.imread(stack_path)
    logging.info(f"Read TIF stack with {len(original_stack)} frames.")

    # Placeholder names (can be adjusted as needed)
    stack_id = "sampled_sequence"

    focus_measures = []
    for method in ALL_FOCUS_METHODS:
        computed_images_focus_values = [
            compute_focus_measure(frame, method) for frame in original_stack
        ]

        for frame_num, (image, focus_value) in enumerate(computed_images_focus_values):
            logging.info(f"Processing frame {frame_num} for {stack_id} using {method}")
            save_computed_image(image, method, stack_id, frame_num)
            focus_measures.append(
                {
                    'stack_id': stack_id,
                    'method': method,
                    'frame': frame_num,
                    'focus_measure': focus_value,
                }
            )

    return focus_measures


if __name__ == "__main__":
    focus_measures = process_single_tif_stack("experiment_images/sampled_sequence.tif")

    output_csv_dir = './analysis/measurements/'
    os.makedirs(output_csv_dir, exist_ok=True)

    with open('./analysis/measurements/focus_measures.csv', 'w', newline='') as csvfile:
        fieldnames = ['stack_id', 'method', 'frame', 'focus_measure']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(focus_measures)

    logging.info("Processing complete.")
