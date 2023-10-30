# Assessment of feature- and edge-detection algorithms for identifying frames of cells in focus

This repository contains code for image processing and analysis to identify frames from video micrographs with *Chlamydomonas* cells in the focal plane. [Comparison of feature- and edge-detection algorithms for identifying cells in focus](TODO https://doi.org/10.57844/arcadia-35f0-3e16).

![TODO](analysis.gif)

Release v1

Github

[![DOI](TODO https://zenodo.org/badge/644048016.svg)]( TODO https://zenodo.org/badge/latestdoi/644048016)

Data Repository

[![DOI](TODO https://zenodo.org/badge/DOI/10.5281/zenodo.8326749.svg)](TODO https://doi.org/10.5281/zenodo.8326749)

# Computational Protocols

For each step run the commands indicated in code blocks from the "focus-filtering" directory. This repository uses conda to manage software environments and installations.
You can find operating system-specific instructions for installing miniconda [here](https://docs.conda.io/en/latest/miniconda.html). We installed Miniconda3 version `23.7.3'.

                curl -JLO https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh # download the miniconda installation script
                bash Miniconda3-latest-Linux-x86_64.sh # run the miniconda installation script. Accept the license and follow the defaults.
                source ~/.bashrc # source the .bashrc for miniconda to be available in the environment

                # configure miniconda channel order
                conda config --add channels defaults
                conda config --add channels bioconda
                conda config --add channels conda-forge
                conda config --set channel_priority strict

## Getting started with this repository

After installing conda run the following command to create the pipeline run environment.


        conda env create -n focus --file envs/focus.yml
        conda activate focus

## Protocol to identify frames of cells in focus using different feature- and edge-detection algorithms

This protocol is a step by step computational guide to assess different feature- and edge-detection algorithms for identying frames of cells in focus in video micrographs. The input is video data of algal cells collected by brightfield or differential interference contrast microscopy. The output includes computed images and focus measures. For related experimental results [TODO follow this link](https://research.arcadiascience.com/pub/result-chlamydomonas-phenotypes#nj8khdxj90e).

1. Open the sampled image data in Fiji. [Link to tif image stack](./experiment_images/sampled_sequence.tif)

2. Run Fiji macro to enable users to select frames of a 180-frame video that are in or out of focus. **Output** = csv file with a random six-digit ID in the name with focus assessment for each frame.  [Link to Fiji macro](./code/fiji_macro/user_assessment.ijm) [Link to assessments](./analysis/user_assessments/focus_results_****.csv)

3. Calculate focus measures and associated images. **Input** = experiment images. **Output** = csv file with measures and individual frames calculated with edge-detection algorithms.

    python3 code/python/measures_and_images.py

# Versions and platforms
*Fiji macro* was used with ImageJ2 Version 2.14.0/1.54f

*Python* code was run with Python 3.11.5

*Python libraries* TODO

Computation was performed on MacBook Pro computer with the following specifications:

macOS: Ventura 13.4.1 (c)
Chip Apple M2 Max
Memory 32 Gb

# Feedback, contributions, and reuse

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
