import calculate_metrics
import numpy as np
import pandas as pd
import skimage
import utils

from matplotlib import pyplot as plt


def calc_roc(sorted_labels):
    '''
    calculate the ROC curve for an ordered set of binary labels
    sorted_labels : list of the binary ground-truth labels, sorted by the value of the metric
    '''
    num_positive = sorted_labels.sum()
    num_negative = (~sorted_labels).sum()

    true_positive_rates, false_positive_rates = [], []
    for thresh in range(len(sorted_labels)):
        num_predicted_positive = sorted_labels[:thresh].sum()
        num_false_positive = (~sorted_labels[:thresh]).sum()

        true_positive_rates.append(num_predicted_positive / num_positive)
        false_positive_rates.append(num_false_positive / num_negative)

    # append the final top right point, which is at (1, 1) by definition
    true_positive_rates.append(1.0)
    false_positive_rates.append(1.0)

    roc_curve = np.vstack((false_positive_rates, true_positive_rates))
    return roc_curve


def load_annotations_and_calc_metrics(filepath):
    '''
    load a set of manual annotations and calculate the focus metrics for each image
    '''
    repo_dirpath = utils.find_repo_root(__file__)

    # load the images
    stack = skimage.io.imread(repo_dirpath / 'experiment_images' / 'sampled_sequence.tif')

    # load the annotations
    annotations = pd.read_csv(filepath)
    annotations['InFocus'] = annotations.InFocus.astype(bool)

    # calculate the metrics and append them to the dataframe
    for metric_name in calculate_metrics.ALL_FOCUS_METRICS:
        values = []
        for im in stack:
            im, value = calculate_metrics.compute_focus_metric(im, metric_name=metric_name)
            values.append(value)

        annotations[metric_name] = values

    return annotations


def split_annotations_by_modality(annotations):
    '''
    split an annotations dataframe into two dataframes,
    one for the brightfield images and one for the DIC images in the original stack

    WARNING: this is specific to the stack and annotations included in this repo
    (`experiment_images/sampled_sequence.tif` and `analysis/user_assessments/` respectively)
    '''
    # the frame index at which frames switch from brightfield ('bf') to DIC
    # in the stack 'experiment_images/sampled_sequence.tif'
    bf_dic_ind = 90

    annotations_bf = annotations.iloc[:bf_dic_ind].copy().reset_index()
    annotations_dic = annotations.iloc[bf_dic_ind:].copy().reset_index()

    return annotations_bf, annotations_dic


def plot_roc_curves(annotations, metric_name, ax=None, show_axis_labels=True):
    '''
    Plot ROC curves for a given focus metric and set of annotations
    for both the brightfield and DIC images (separately)
    '''
    if ax is None:
        plt.figure()
        ax = plt.gca()

    annotations_bf, annotations_dic = split_annotations_by_modality(annotations)

    for _label, _annotations in zip(('Brightfield', 'DIC'), (annotations_bf, annotations_dic)):
        roc_curve = calc_roc(
            sorted_labels=_annotations.sort_values(by=metric_name, ascending=True).InFocus
        )
        ax.plot(roc_curve[0, :], roc_curve[1, :], label=_label)

        if show_axis_labels:
            ax.set_xlabel('False positive rate')
            ax.set_ylabel('True positive rate')
        ax.set_aspect(1)

    plt.legend()


def plot_all_roc_curves():
    '''
    Plot a grid of ROC curves for all focus metrics and all annotations
    '''

    repo_dirpath = utils.find_repo_root(__file__)
    annotation_filepaths = list((repo_dirpath / 'analysis' / 'user_assessments').glob('*.csv'))

    # instantiate the subplots
    num_rows = len(calculate_metrics.ALL_FOCUS_METRICS)
    num_cols = len(annotation_filepaths)
    fig, axs = plt.subplots(num_rows, num_cols, figsize=(12, 12))

    for col_ind, filepath in enumerate(annotation_filepaths):
        annotations = load_annotations_and_calc_metrics(filepath)
        for row_ind, metric_name in enumerate(calculate_metrics.ALL_FOCUS_METRICS):
            ax = axs[row_ind][col_ind]
            plot_roc_curves(
                annotations, metric_name=metric_name, ax=ax, show_axis_labels=False
            )
            ax.set_title(
                '%s - %s'
                % (
                    filepath.stem.replace('focus_results_', ''),
                    metric_name.replace('_of_intensity', ''),
                ),
                fontsize=10,
            )

            if row_ind < num_rows - 1:
                ax.set_xticks([])

            if col_ind > 0:
                ax.set_yticks([])


if __name__ == '__main__':
    plot_all_roc_curves()
    plt.show()
