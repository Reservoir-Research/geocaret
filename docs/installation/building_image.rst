Building the GeoCARET Docker Image
==================================

.. _GeoCARET: https://github.com/Reservoir-Research/geocaret
.. _git: https://git-scm.com/book/en/v2/Getting-Started-What-is-Git%3F

Docker can be used to quickly & easily create a run-time environment for running GeoCARET_, without having to install the correct version of **Python**, **gcloud CLI**, or **other required dependencies**.

To use GeoCARET with Docker you will need to build and run an instance of a Docker image - see :ref:`What are Docker Images`.

Generally, you will not need to build your own image, as we provide a **pre-built image** as a package on GitHub, that will be suitable for most purposes. See :ref:`Pulling GeoCARET Docker image` for accessing & using the pre-built GeoCARET docker image.

However, if you want to build your own image, this guide will take you through the process.

As a prerequisite, you need to first install Docker `Docker Desktop <https://www.docker.com/products/docker-desktop/>`_ - an application that provides an easy-to-use interface for working with Docker on a desktop operating system. Docker Desktop is free and can be installed on Windows, Mac & Linux computers, Please visit https://docs.docker.com/get-docker/ and follow the appropriate instructions for installing Docker Desktop on your computer. For Linux distributions, you can alternatively install `Docker Engine <https://docs.docker.com/engine/install/>`_. 

.. note::
   This documentation assumes that the reader is comfortable working in the shell (linux/macOS) or PowerShell (Windows) and has
   basic experience with git_.

Once installed, make sure that Docker is running. To do so, open a shell prompt (Linux/macOS) or PowerShell (Windows) and type the following:

.. code-block:: bash

   docker -v

This should return the version number of the installed version of docker. If you see an error message along the lines of *‘Cannot connect to the Docker daemon’* then restart Docker Desktop / Docker Engine and try again.

Building the GeoCARET Docker image
----------------------------------

Clone the GeoCARET GitHub repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First clone the GeoCARET GutHub repository to your computer:

.. code-block:: bash

   git clone https://github.com/UoMResearchIT/geocaret
   
Alternatively, if you don't use git_, download the package from the `GitHub page <https://github.com/UoMResearchIT/geocaret>`_ and extract to the working folder.

.. _build-the-geocaret-docker-image-1:

Build the GeoCARET Docker Image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Building the GeoCARET image is simple. Make sure that 

* Docker Desktop / Docker Engine is running
* You are in the root folder of the GeoCARET code base that you cloned in the previous step. 

Then inside the root directory of GeoCARET, i.e. where `setup.py` is located, type:

.. code-block:: bash

   docker build -t geocaret .

Building the image might take a short while. The resulting image will be stored in a dedicated Docker folder on your computer. If you open Docker Desktop and go to the **‘Images’** section, you should see the **‘geocaret’** image in the list.

You can now refer to :doc:`using_image` for details on how to run GeoCARET using your newly built Docker image.
