import os
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
    one for the brightfield ('bf') images and one for the DIC images in the original stack

    WARNING: this is specific to the stack and annotations included in this repo
    (`experiment_images/sampled_sequence.tif` and `analysis/user_assessments/` respectively)
    '''
    # this is the frame index in the stack 'experiment_images/sampled_sequence.tif'
    # at which the frames switch from brightfield ('bf') to DIC
    bf_dic_ind = 90

    annotations_bf = annotations.iloc[:bf_dic_ind].copy().reset_index()
    annotations_dic = annotations.iloc[bf_dic_ind:].copy().reset_index()

    return annotations_bf, annotations_dic


def plot_all_roc_curves():
    '''
    Plot a grid of ROC curves for all focus metrics and all annotations

    The grid has two rows, one for each imaging modality (brightfield and DIC),
    and one column for each focus metric
    '''

    imaging_modality_names = ('Brightfield', 'DIC')

    repo_dirpath = utils.find_repo_root(__file__)
    annotation_filepaths = list((repo_dirpath / 'analysis' / 'user_assessments').glob('*.csv'))

    num_rows = len(imaging_modality_names)
    num_cols = len(calculate_metrics.ALL_FOCUS_METRICS)
    _, axs = plt.subplots(num_rows, num_cols, figsize=(12, 8))

    for filepath in annotation_filepaths:
        annotations_all = load_annotations_and_calc_metrics(filepath)
        annotations_bf, annotations_dic = split_annotations_by_modality(annotations_all)

        for col_ind, metric_name in enumerate(calculate_metrics.ALL_FOCUS_METRICS):
            for row_ind, (modality_name, annotations) in enumerate(
                zip(imaging_modality_names, (annotations_bf, annotations_dic))
            ):
                ax = axs[row_ind][col_ind]

                sorted_labels = annotations.sort_values(by=metric_name, ascending=True).InFocus

                roc_curve = calc_roc(sorted_labels)
                ax.plot(roc_curve[0, :], roc_curve[1, :], color='#28b', alpha=0.5)

                ax.set_title(
                    '%s\n%s' % (metric_name.replace('_', ' ').capitalize(), modality_name),
                    fontsize=10,
                )

                if row_ind == num_rows - 1:
                    ax.set_xlabel('False positive rate')

                if col_ind == 0:
                    ax.set_ylabel('True positive rate')

                if col_ind > 0:
                    ax.set_yticks([])

                ax.set_aspect(1)


if __name__ == '__main__':
    plot_all_roc_curves()
    plot_dirpath = utils.find_repo_root(__file__) / 'output'
    os.makedirs(plot_dirpath, exist_ok=True)
    plt.savefig(plot_dirpath / 'focus_metric_roc_curves.svg', format='svg')
