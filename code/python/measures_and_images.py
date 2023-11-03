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
import numpy as np
import skimage

ALL_FOCUS_METHODS = [
    'variance_of_laplacian',
    'std_dev_of_intensity_without_blur',
    'std_dev_of_intensity_with_blur',
    'sobel_magnitude',
]


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='focus-filter.log',
)


def _normalize_image(image):
    '''
    Normalize an image to (0, 1)
    '''
    image = skimage.img_as_float(image)
    image -= image.min()
    image[image < 0] = 0
    image /= image.max()
    return image


def variance_of_laplacian(image):
    '''
    The variance-of-Laplacian focus measure method
    '''
    image = skimage.img_as_float(image)

    image_blurred = skimage.filters.gaussian(image, sigma=1)
    image_laplacian = skimage.filters.laplace(image_blurred, ksize=3)
    image_laplacian = _normalize_image(image_laplacian)

    return image_laplacian, image_laplacian.var()


def sobel_magnitude(image):
    '''
    The variance-of-sobel focus measure method
    '''
    image = skimage.img_as_float(image)

    image_blurred = skimage.filters.gaussian(image, sigma=1)

    # Compute the x-gradient and y-gradient using Sobel operator
    image_sobel_h = skimage.filters.sobel_h(image_blurred)
    image_sobel_v = skimage.filters.sobel_v(image_blurred)

    # Compute the normalized magnitude of the gradient
    image_sobel_magnitude = np.sqrt(image_sobel_h**2 + image_sobel_v**2)
    image_sobel_magnitude = _normalize_image(image_sobel_magnitude)

    return image_sobel_magnitude, image_sobel_magnitude.var()


def std_dev_of_intensity(image, blur=False):
    '''
    the standard deviation of intensity as a focus measure method
    (with or without Gaussian blur)
    '''
    if blur:
        image = skimage.filters.gaussian(image, sigma=1)
    return image, image.var()


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
    elif method == 'sobel_magnitude':
        return sobel_magnitude(frame)
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
        skimage.io.imsave(output_path, image.astype(np.uint16))


def process_single_tif_stack(stack_path):
    '''
    Calculate all of the focus measures for each frame of the stack
    '''
    logging.info(f"Processing TIF stack: {stack_path}")

    original_stack = skimage.io.imread(stack_path)
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
