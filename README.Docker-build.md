# Building a GeoCARET docker image

Docker can be used to quickly & easily create a run-time environment for running the GeoCARET tool, without having to install the correct version of Python, gcloud CLI, or other required dependencies.

Generally you will not need to build your own image, as we provide a pre-built image that will be suitable for most purposes. See [README.Docker.md](README.Docker.md) for accessing & using the pre-built GeoCARET docker image.

However, if you _do_ want to build your own image, this guide will take you through the required steps:

1. Install Docker Desktop.
2. Build the GeoCARET Docker image.
3. Use Docker compose to run GeoCARET. 

>**NOTE**  This documentation assumes that the reader is comfortable working in the shell (linux/macOS) or PowerShell (Windows) and has basic experience with git. 

## Install Docker Desktop

### What is Docker?

Docker is a tool for packaging applications, and their dependencies, so they can be executed anywhere.

If you already have Docker installed on your computer then skip to the next section, `Build the GeoCARET Docker image`.

You don't really need to know how Docker works to use it to run GeoCARET, but it's worth understanding the two most important Docker concepts *images* and *containers*. 

#### Docker images
A Docker image is a template that contains all the necessary files and instructions to run a *containerized* application: a base operating system, the application source code & any libraries, dependencies, and other resources needed to execute the application.

#### Docker containers
A Docker container is a running instance of a Docker image. It is an isolated environment that contains all the necessary resources for the application to run. Think of it as a very lightweight virtual machine running on your host computer, with the application running inside it.

Later on we'll be building the GeoCARET image, and then launching a GeoCARET container from that image, inside which GeoCARET itself will run. Step 1 is to install Docker Desktop. 

### Installing Docker Desktop

Docker Desktop is free and can be installed on Windows, Mac & Linux computers, Please visit https://docs.docker.com/get-docker/ and follow the appropriate instructions for installing Docker Desktop on your computer. 

Once installed, make sure Docker Desktop is running, and open a shell prompt (linux/macOS) or PowerShell (Windows) and typing the following:

    docker -v

This should return the version number of the installed version of docker.  If you see an error message along the lines of 'Cannot connect to the Docker daemon' then restart Docker Desktop and try again.

## Build the GeoCARET Docker image

### Clone the GeoCARET GitHub repository

First clone the GeoCARET GutHub repository to your computer:

    git clone https://github.com/UoMResearchIT/geocaret

### Build the GeoCARET Docker image

Building the GeoCARET image is simple. Make sure (a) Docker Desktop is running and (b) you are in the root folder of the GeoCARET code base that you cloned in the previous step. Then type:

    docker build -t geocaret .

Building the image might take a short while. The resulting image will be stored in a dedicated Docker folder on your computer. If you open Docker Desktop and go to the 'Images' section, you should see the 'geocaret' image in the list.

You can now refer to [README.Docker.md](README.Docker.md), and read the section `Use Docker compose to run GeoCARET` for details of how to run GeoCARET using your docker image. 
