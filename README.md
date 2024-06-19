![CI-PUSH-MAIN status badge](https://github.com/UoMResearchIT/heet/actions/workflows/main.yml/badge.svg?event=push)
![CI-PUSH-MANUAL status badge](https://github.com/UoMResearchIT/heet/actions/workflows/manual.yml/badge.svg?branch=main)
![CI-PUSH-MANUAL status badge](https://github.com/UoMResearchIT/heet/actions/workflows/manual.yml/badge.svg?branch=progress)

<!-- PROJECT LOGO -->
<p align="center">
    <img alt="reemission-logo" height="175" src="https://github.com/UoMResearchIT/geocaret/assets/8837107/d01e7da4-e075-483a-9d9b-953a3dd1b5d8"/>
</p>

# About
GeoCARET is a command line Python tool for delineating and analysing catchments and reservoirs. It relies on Google Earth Engine (GEE) - Google's cloud-based platform developed for planetary-scale environmental analysis. GeoCARET uses Google Earth Engine as a backend for performing geomatry operations and data processing and as a database of global spatial data in the form of GIS layers. It additionally relies on several private assets not available in GEE. We have made these assets accessible for analysis by uploading them to a dedicated GEE asset folder.

To request access to those assets please send email to:
[tomasz.k.janus@gmail.com](mailto:tomasz.k.janus@gmail.com?subject=[GeoCARET]%20Request%20Asset%20Access) or
[tjanus.heet@gmail.com](mailto:tjanus.heet@gmail.com?subject=[GeoCARET]%20Request%20Asset%20Access)
with your email address registered with Google Earth Engine.

## How to use GeoCARET

Full instructions for installing and using GeoCARET can be found in the [docs folder](docs). Here you'll find detailed instructions to help you:

1. [Register to use Google Earth Engine](docs/01_prerequisites.md) and prepare for running GeoCARET.
2. Install GeoCARET on your computer. We recommend using the [GeoCARET Docker image](README.Docker.md).  More technical users can also  [Install GeoCARET and its dependencies](docs/02_install.md) if they prefer.
3. [Prepare suitable input data](docs/03_input_data.md).
4. [Run an analysis](docs/04_run.md).
5. [Explore the outputs](docs/05A_output_data.md).


<!-- # Requirements
Requires Python 3.8 or higher.

A number of additional python libraries are required to run the heet tool. These are listed in `requirements.txt`.

We advise that you create a separate python environment for running GeoCARET (see installation guide for step by step instructions).

# Documentation
Please see the `docs` folder for instructions on (i) how to install and run GeoCARET (ii) how to prepare the input data. -->


