![CI-PUSH-MAIN status badge](https://github.com/UoMResearchIT/heet/actions/workflows/main.yml/badge.svg?event=push)
![CI-PUSH-MANUAL status badge](https://github.com/UoMResearchIT/heet/actions/workflows/manual.yml/badge.svg?branch=main)
![CI-PUSH-MANUAL status badge](https://github.com/UoMResearchIT/heet/actions/workflows/manual.yml/badge.svg?branch=progress)

<!-- PROJECT LOGO -->
<p align="center">
    <img alt="reemission-logo" height="175" src="https://github.com/UoMResearchIT/geocaret/assets/8837107/d01e7da4-e075-483a-9d9b-953a3dd1b5d8"/>
</p>

# About

**GeoCARET** is a command line Python tool for delineating and analysing catchments and reservoirs. It relies on [Google Earth Engine](https://earthengine.google.com/) (GEE) - Google's cloud-based platform developed for planetary-scale environmental analysis. GeoCARET uses Google Earth Engine as a backend for performing geometry operations and data processing and as a database of global spatial data in the form of GIS layers. It additionally relies on several private assets not available in GEE. We have made these assets accessible for analysis by uploading them to a dedicated GEE asset folder.

To request access to those assets please send email to:
[tomasz.k.janus@gmail.com](mailto:tomasz.k.janus@gmail.com?subject=[GeoCARET]%20Request%20Asset%20Access) or
[tjanus.heet@gmail.com](mailto:tjanus.heet@gmail.com?subject=[GeoCARET]%20Request%20Asset%20Access)
with your email address registered with Google Earth Engine.

# Requirements

Our software requires Python 3.8 or 3.9 only.

We are currently experiencing errors when trying to run our software in Python 3.10 caused by `frictionless` package being limited to version 4.40.8 or lower which does not supporting the new hierarchy of classes in Python's collections module. We are working on resolving this issue.

A number of additional python libraries are required to run the heet tool. These are listed in `requirements.txt`.

We advise that you create a separate python environment for running GeoCARET (see installation guide for step by step instructions).

# Installation

The repository does not require installation but relies on a number of packages. We recommend that you set up a virtual environment dedicated to this repository before attempting to install all the dependencies. There are several packages for creating virtual environments such as `venv`, `virtualenv`, `pyenv`, etc. Please refer to web resources and find out what works best for you, e.g. in [https://www.freecodecamp.org/news/how-to-setup-virtual-environments-in-python/](https://www.freecodecamp.org/news/how-to-setup-virtual-environments-in-python/).

The dependencies are included in `requirements.txt`. You can install these dependencies by running:
```
pip install -r requirements.txt
```

The package can also be installed as a Docker image. For more information, see [installation instructions](https://reservoir-research.github.io/geocaret/installation/index.html)

# How to use GeoCARET

Depending on the installation option, either as a Python package or as a Docker image, running GeoCARET requres a slightly different syntax. The details on how to run GeoCARET are provided [here](https://reservoir-research.github.io/geocaret/running_geocaret/index.html).

# Demo

We have provided a test data file that can be used to run GeoCARET. The file contains input data for analysis of a single reservoir. 

To run the demo using GeoCARET as a Python script, use the following syntax:

```
> python heet_cli.py tests/data/dams.csv test_project job01 standard
```

To run the demo using GeoCARET Docker container, type the following:

```
> docker compose run --rm geocaret python heet_cli.py tests/data/dams.csv test_project job01 standard
```

# Tests

The repository contains unit tests which test the behaviour of individual components of the software. They can be executed using `pytest` by typing `pytest tests` in the root folder where the `tests` directory is located.

# Disclaimer

This software has been written for research purposes and may not be as robust as the software designed to be used by the wider public. We are aware of this and we're trying to make constant improvements, developments and bug fixes. If you run into problems running this software, please submit an issue or contact us directly at <a href="mailto:tomasz.janus@manchester.ac.uk">tomasz.janus@manchester.ac.uk</a>, <a href="mailto:tomasz.k.janus@gmail.com">tomasz.k.janus@gmail.com</a> or <a href="mailto:jaise.kuriakose@manchester.ac.uk">jaise.kuriakose@manchester.ac.uk</a>
