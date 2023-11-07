# Assessment of feature- and edge-detection algorithms for identifying frames of cells in focus
This repository contains code for image processing and analysis to identify frames from video micrographs with *Chlamydomonas* cells in the focal plane. See [Comparison of feature- and edge-detection algorithms for identifying cells in focus](TODO: add link) for more details.


## Release snapshots
__Github__<br>
[![DOI](TODO: add badge link)](TODO: add zenodo link)

__Data__<br>
[![DOI](TODO: add badge link)](TODO: add zenodo link)


## Computational Protocols
For each step run the commands indicated in code blocks from the "focus-filtering" directory. This repository uses conda to manage software environments and installations.

You can find operating system-specific instructions for installing miniconda [here](https://docs.conda.io/en/latest/miniconda.html). We installed Miniconda3 version `23.7.3':
```sh
# download the miniconda installation script
curl -JLO https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

# run the miniconda installation script. Accept the license and follow the defaults.
bash Miniconda3-latest-Linux-x86_64.sh

# source the .bashrc for miniconda to be available in the environment
source ~/.bashrc

# configure miniconda channel order
conda config --add channels defaults
conda config --add channels bioconda
conda config --add channels conda-forge
conda config --set channel_priority strict
```

## Getting started with this repository
After installing conda run the following command to create the pipeline run environment:
```sh
conda env create -n focus-filtering --file envs/focus-filtering.yml
conda activate focus-filtering
```

## Protocol to identify frames of cells in focus using different feature- and edge-detection algorithms
This protocol is a step by step computational guide to assess different feature- and edge-detection algorithms for identifying images in which objects (usually cells) of interest are in focus. The input is video data of algal cells collected by brightfield or differential interference contrast (DIC) microscopy. The output includes computed images and focus metrics. For related experimental results [see here](TODO: add link to pub).

1. Open the [sample image data](./experiment_images/sampled_sequence.tif) in Fiji. __Note that this sequence includes several timelapses concatenated together, including timelapses from brightfield and DIC imaging.__

2. Run the [Fiji macro](./code/fiji_macro/user_assessment.ijm) to enable users to select frames of a 180-frame video that are in or out of focus. This outputs a CSV file with a random six-digit ID in the name with focus assessment for each frame. The assessments used for the published analysis are [here](./analysis/user_assessments/).

3. Calculate the focus-detection metrics using [this script](./code/python/measures_and_images.py). The input to the script is a TIFF stack of raw brightfield or DIC images. The output is 1) a CSV file with the values of the focus metrics for each frame and 2) the individual frames after filtering with each edge-detection filter.


## Versions and platforms
__Fiji macro__: the macro was used with ImageJ2 Version 2.14.0/1.54f.

__Python__: the conda environment file is `envs/focus-filtering.yml`. Direct dependencies are found in `requirements.txt`.

__Hardware__:
Computation was performed on a MacBook Pro computer on Ventura 13.4.1 with an M2 Max processor and 32G of memory.

## Development
This repo uses black and isort for formatting and flake8 for linting. These can be installed using `pip install -r requirements-dev.txt`. There are pre-commit hooks to run these tools prior to each commit; install them using `pre-commit install`. Alternatively, you can run the formatting and linting manually using `make format` and `make lint`.

## Feedback, contributions, and reuse
We try to be as open as possible with our work and make all of our code both available and usable.
We love receiving feedback at any level, through comments on our pubs or Twitter and issues or pull requests here on GitHub.
In turn, we routinely provide public feedback on other people’s work by [commenting on preprints](https://sciety.org/lists/f8459240-f79c-4bb2-bb55-b43eae25e4f6), filing issues on repositories when we encounter bugs, and contributing to open-source projects through pull requests and code review.

Anyone is welcome to contribute to our code.
When we publish new versions of pubs, we include a link to the "Contributions" page for the relevant GitHub repo in the Acknowledgements/Contributors section.
If someone’s contribution has a substantial impact on our scientific direction, the biological result of a project, or the functionality of our code, the pub’s point person may add that person as a formal contributor to the pub with "Critical Feedback" specified as their role.

Our policy is that external contributors cannot be byline-level authors on pubs, simply because we need to ensure that our byline authors are accountable for the quality and integrity of our work, and we must be able to enforce quick turnaround times for internal pub review.
We apply this same policy to feedback on the text and other non-code content in pubs.

If you make a substantial contribution, you are welcome to publish it or use it in your own work (in accordance with the license — our pubs are CC BY 4.0 and our code is openly licensed).
We encourage anyone to build upon our efforts.
