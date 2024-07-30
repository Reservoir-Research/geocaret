# Using the GeoCARET Docker image

The GeoCARET Docker image is the simplest way to run GeoCARET. This guide will take you through the required steps:

1. Install Docker Desktop.
2. Pull the GeoCARET Docker image.
3. Use Docker compose to run GeoCARET. 

>**NOTE** This documentation assumes that the reader:
>* Understands how to use Google Earth Engine (GEE) and has a properly configured GEE cloud project. See the main GeoCARET documentation, [GeoCARET Prerequisites](docs/01_prerequisites.md) for details.
>* Understands how to use the GeoCARET tool. See the main GeoCARET documentation, [Preparing Your Input File](docs/03_input_data.md) & [Running The GeoCARET Script](docs/04_run.md) for full details.
>* Has a basic familiarity with the shell (macOS or linux) or PowerShell (Windows).

## Install Docker Desktop

### What is Docker?

!! **FIXME**: this section might not be required? Maybe just keep the 'Installing Docker Desktop' part? !!

Docker is a tool for packaging applications, and their dependencies, so they can be executed anywhere.

If you already have Docker installed on your computer then skip to the next section, `Pull the GeoCARET Docker image`.

You don't really need to know how Docker works to use it to run GeoCARET, but it's worth understanding the two most important Docker concepts *images* and *containers*. 

#### Docker images
A Docker image is a template that contains all the necessary files and instructions to run a *containerized* application: a base operating system, the application source code & any libraries, dependencies, and other resources needed to execute the application.

#### Docker containers
A Docker container is a running instance of a Docker image. It is an isolated environment that contains all the necessary resources for the application to run. Think of it as a very lightweight virtual machine running on your host computer, with the application running inside it.

### Installing Docker Desktop

Docker Desktop is free and can be installed on Windows, Mac & Linux computers, Please visit https://docs.docker.com/get-docker/ and follow the appropriate instructions for installing Docker Desktop on your computer. 

Once installed, make sure Docker Desktop is running, and open a shell prompt (linux/macOS) or PowerShell (Windows) and typing the following:

    docker -v

This should return the version number of the installed version of docker.  If you see an error message along the lines of 'Cannot connect to the Docker daemon' then restart Docker Desktop and try again.

## Pull the GeoCARET Docker image

[**FIXME** this will need to be updated when the GeoCARET image is hosted as a package]

Open a shell prompt (macOS/linux) or PowerShell (Windows) and type:

    docker pull ghcr.io/Reservoir-Research/geocaret

## Use Docker compose to run GeoCARET

### Prepare your workspace

Docker compose is a tool for simplifying the execution of docker containers. We'll use it to run GeoCARET. 

First you'll need to create a new folder for your GeoCARET workspace, and then inside this you must then create three sub-folders:

* `data`, which will hold your input data files. 
* `outputs`, which will hold the analyses output files
* `auth`, which will hold your GEE authentication credentials

For example on linux or macOS, open a shell prompt, or on Windows open PowerShell, and then type:

    mkdir my_geocaret_work_folder
    cd my_geocaret_work_folder
    mkdir data
    mkdir outputs
    mkdir auth

You'll also need to download the file [compose.yml](https://github.com/UoMResearchIT/geocaret/blob/geocaret_docker/compose.yml) and save it inside your GeoCARET workspace folder (e.g. `my_geocaret_work_folder` in the above example). 

> **Important: linux users & directory permissions**
> 
>  When run on a linux host computer, the GeoCARET docker image will only work if the user ID & group ID (UID:GID) of your user account is 1000:1000. Otherwise, GeoCARET will not be able to write to the auth/ or outputs/ folders. 
>
>If you use linux on a personal laptop, then it is very likely your user account UID:GID will be 1000:1000. However, this may not be the case if you log in to a linux server with multiple users. To check your user account, type:
>
>```
>id -u  # print user ID (UID)
>id -g  # print group ID (GID)
>```
>If your user account has a different UID and/or GID then you should follow the instructions in [Installation](docs/02_install.md) to install the GeoCARET Python script directly.

### Test GeoCARET works:

To test everything is working correctly, you should first run the following from inside the GeoCARET workspace folder you just created:

    cd my_geocaret_work_folder
    docker compose run --rm geocaret

You should see the message *"You must specify a command to run. See README.Docker.md for details."* and GeoCARET will exit.

### Run a GeoCARET analysis

First, copy your input data file to the `data` sub-folder and then start the GeoCARET tool by typing the following:

    $ docker compose run --rm geocaret python heet_cli.py data/input-filename.csv projectname jobname dataset

Where:
* `data/input-filename.csv` is the input file. **Note for Windows users:** ensure you use a / and not a \ when specifying the path to the data file.
* `projectname` is the name of your Earth Engine project
* `jobname` is a short 10 character jobname to be used when creating output folders. May only contain the following characters A-Z, a-z, 0-9, -.
* `dataset` is the output dataset required: standard, extended, diagnostic, diagnostic-catch, diagnostic-res, diagnostic-riv

See the main GeoCARET documentation, [Preparing Your Input File](docs/03_input_data.md) and [Running The GeoCARET Script](docs/04_run.md) for full details of input data files and all of the arguments that are passed to the GeoCARET tool.

### Google cloud authentication

If this is the first time you've run GeoCARET, you will be asked to authenticate with Google's cloud services:

1. You'll be shown a URL, which you should copy and paste into a web browser. In Windows PowerShell you can hold down the `Ctrl` key and click the URL to open it automatically.  
2. Follow the instructions to authenticate with Google
3. After authenticating, you'll be given a token, which you should paste back into the GeoCARET tool command line.
4. Press enter to continue the GeoCARET analysis.

>**NOTE** Your authentication details will be cached in the `auth` sub-folder inside the GeoCARET workspace folder. When you subsequently run GeoCARET from this folder, you will not need to reauthenticate.  

Once authenticated the GeoCARET analysis will run. This could take several minutes to complete. 

#### Use existing Google cloud credentials

If you have previously authenticated with the Google cloud / GEE APIs, you may already have the necessary credentials stored on your computer (e.g. in /home/username/.config, which is the default location on linux/macOS). 

You can use your existing credentials to avoid the need to authenticate when running GeoCARET, by setting the `GEOCARET_AUTH_PATH` environment variable:

    GEOCARET_AUTH_PATH=/home/username/.config docker compose run --rm geocaret python heet_cli.py data/input-filename.csv projectname jobname dataset

### Analysis Outputs

When the GeoCARET analysis is complete, all output files generated are saved to a sub-folder of your Google Earth Engine project Assets folder, called XHEET:

    XHEET/<<JOBNAME>>-<<TIMESTAMP>> e.g. XHEET/MYANMAR01-20220130-1450

Calculated properties (output_parameters) are also downloaded to a local results sub-folder, named `outputs`, as a CSV file (output_parameters.csv).

Please see the main GeoCARET documentation, [GeoCARET Output data](docs/05A_output_data.md) for full details of the GeoCARET analysis outputs. 

