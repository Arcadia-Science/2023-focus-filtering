"""
Summary:
The script processes a single TIFF image stack, computes various focus metrics,
and then saves the computed images and metrics to specific directories.

The focus metrics it computes are:
- variance of the raw intensities
- variance of the Laplacian-filtered image
- variance of the Sobel-filtered image

The script also logs each step of the process.
Results are saved both as images and as a CSV file containing the focus metrics.
"""

import csv
import logging
import os
import pathlib
import numpy as np
import skimage
import utils

ALL_FOCUS_METRICS = [
    'variance_of_intensity_without_blur',
    'variance_of_sobel_magnitude',
    'variance_of_laplacian',
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
    The variance-of-Laplacian focus metric
    '''
    image = skimage.img_as_float(image)

    image_blurred = skimage.filters.gaussian(image, sigma=1)
    image_laplacian = skimage.filters.laplace(image_blurred, ksize=3)
    image_laplacian = _normalize_image(image_laplacian)

    return image_laplacian, image_laplacian.var()


def variance_of_sobel_magnitude(image):
    '''
    The variance-of-sobel focus metric
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


def variance_of_intensity(image, blur=False):
    '''
    the variance of intensity as a focus metric
    (with or without Gaussian blur)
    '''
    if blur:
        image = skimage.filters.gaussian(image, sigma=1)
    return image, image.var()


def compute_focus_metric(frame, metric_name):
    '''
    compute the specified focus metric
    '''
    if metric_name == 'variance_of_laplacian':
        return variance_of_laplacian(frame)
    elif metric_name == 'variance_of_intensity_without_blur':
        return variance_of_intensity(frame, blur=False)
    elif metric_name == 'variance_of_sobel_magnitude':
        return variance_of_sobel_magnitude(frame)
    else:
        raise ValueError(f"Unknown focus metric: {metric_name}")


def save_computed_image(image, metric_name, stack_id, frame_num):
    '''
    write the computed image to an output directory
    '''
    repo_dirpath = utils.find_repo_root(__file__)
    output_dir = pathlib.Path(
        repo_dirpath / 'analysis' / 'processed_images' / metric_name / stack_id
    )
    os.makedirs(output_dir, exist_ok=True)

    output_path = output_dir / f"{stack_id}_{frame_num}.tif"
    if image is not None:
        skimage.io.imsave(output_path, image.astype(np.uint16))


def process_single_tif_stack(stack_path):
    '''
    Calculate all of the focus metric for each frame of the stack
    '''
    logging.info(f"Processing TIF stack: {stack_path}")

    original_stack = skimage.io.imread(stack_path)
    logging.info(f"Read TIF stack with {len(original_stack)} frames.")

    # Placeholder names (can be adjusted as needed)
    stack_id = "sampled_sequence"

    focus_metrics = []
    for metric_name in ALL_FOCUS_METRICS:
        computed_images_focus_values = [
            compute_focus_metric(frame, metric_name) for frame in original_stack
        ]

        for frame_num, (image, focus_value) in enumerate(computed_images_focus_values):
            logging.info(f"Processing frame {frame_num} for {stack_id} using {metric_name}")
            save_computed_image(image, metric_name, stack_id, frame_num)
            focus_metrics.append(
                {
                    'stack_id': stack_id,
                    'frame_num': frame_num,
                    'metric_name': metric_name,
                    'metric_value': focus_value,
                }
            )

    return focus_metrics


if __name__ == "__main__":
    repo_dirpath = utils.find_repo_root(__file__)
    focus_metrics = process_single_tif_stack(
        pathlib.Path(repo_dirpath / "experiment_images" / "sampled_sequence.tif")
    )

    output_csv_dir = repo_dirpath / 'analysis' / 'measurements'
    os.makedirs(output_csv_dir, exist_ok=True)

    with open(output_csv_dir / 'focus_measures.csv', 'w', newline='') as csvfile:
        fieldnames = ['stack_id', 'frame_num', 'metric_name', 'metric_value']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(focus_metrics)

    logging.info("Processing complete.")
