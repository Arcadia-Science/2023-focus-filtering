import os
import calculate_metrics
import numpy as np
import pandas as pd
import skimage
import utils

from matplotlib import pyplot as plt

IMAGING_MODALITY_NAMES = ('Brightfield', 'DIC')


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


def filter_annotations_by_modality(annotations, modality_name):
    '''
    filter an annotations dataframe to include only the rows from a given imaging modality

    WARNING: this is specific to the stack and annotations included in this repo
    (`experiment_images/sampled_sequence.tif` and `analysis/user_assessments/` respectively)
    '''
    # this is the frame index in the stack 'experiment_images/sampled_sequence.tif'
    # at which the frames switch from brightfield ('bf') to DIC
    bf_dic_ind = 90

    if modality_name.lower() == 'brightfield':
        annotations = annotations.iloc[:bf_dic_ind].copy().reset_index()
    elif modality_name.lower() == 'dic':
        annotations = annotations.iloc[bf_dic_ind:].copy().reset_index()
    else:
        raise ValueError(f"Unknown modality: {modality_name}")

    return annotations


def plot_all_roc_curves():
    '''
    Plot a grid of ROC curves for all focus metrics and all annotations

    The grid has two rows, one for each imaging modality (brightfield and DIC),
    and one column for each focus metric
    '''

    repo_dirpath = utils.find_repo_root(__file__)
    annotation_filepaths = list((repo_dirpath / 'analysis' / 'user_assessments').glob('*.csv'))

    num_rows = len(IMAGING_MODALITY_NAMES)
    num_cols = len(calculate_metrics.ALL_FOCUS_METRICS)
    _, axs = plt.subplots(num_rows, num_cols, figsize=(12, 8))

    for filepath in annotation_filepaths:
        annotations_all = load_annotations_and_calc_metrics(filepath)

        for col_ind, metric_name in enumerate(calculate_metrics.ALL_FOCUS_METRICS):
            for row_ind, modality_name in enumerate(IMAGING_MODALITY_NAMES):
                ax = axs[row_ind][col_ind]

                annotations = filter_annotations_by_modality(annotations_all, modality_name)
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


def calc_median_tpr(fpr_thresh):
    '''
    Calculate the median true positive rate across all imaging modalities
    for a given false positive rate threshold
    '''

    repo_dirpath = utils.find_repo_root(__file__)
    annotation_filepaths = list((repo_dirpath / 'analysis' / 'user_assessments').glob('*.csv'))

    summary_rows = []
    for filepath in annotation_filepaths:
        annotations_all = load_annotations_and_calc_metrics(filepath)

        for metric_name in calculate_metrics.ALL_FOCUS_METRICS:
            for modality_name in IMAGING_MODALITY_NAMES:
                annotations = filter_annotations_by_modality(annotations_all, modality_name)
                sorted_labels = annotations.sort_values(by=metric_name, ascending=True).InFocus
                roc_curve = calc_roc(sorted_labels)

                # calculate the true positive rate at the FPR closest
                # to a given false positive rate
                ind = np.argmin((roc_curve[0, :] - fpr_thresh) ** 2)
                summary_rows.append(
                    {
                        'modality': modality_name,
                        'metric': metric_name,
                        'fpr': roc_curve[0, ind],
                        'tpr': roc_curve[1, ind],
                    }
                )

    summary = pd.DataFrame(summary_rows)
    summary = summary.groupby(['modality', 'metric']).median().reset_index()
    return summary


if __name__ == '__main__':
    output_dirpath = utils.find_repo_root(__file__) / 'analysis' / 'figures'
    os.makedirs(output_dirpath, exist_ok=True)

    plot_all_roc_curves()
    plt.savefig(output_dirpath / 'focus_metric_roc_curves.svg', format='svg')

    summary = calc_median_tpr(fpr_thresh=0.05)
    summary.to_csv(output_dirpath / 'roc_curve_summary.csv', index=False, float_format='%.3f')
