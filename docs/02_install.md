# Installation

## Background

GeoCARET is a command-line tool written in Python. This documentation assumes that the reader is comfortable working in the shell (linux/macOS) or PowerShell (Windows) and has basic experience with git. Experience using Python is advantageous but not essential.

To install & run the GeoCARET tool on the command line, you will need to 

1. Install a number of dependencies
2. Be able to setup and activate a Python environment.  

This document provides a guide to each step.

>**NOTE** alternatively you can use the **GeoCARET Docker image**, which provides a simple way to run GeoCARET without having to install any of the dependencies (other than Docker itself). See [Using the GeoCARET Docker image](../README.Docker.md) for full instructions.
>
>If you've already installed the Docker image, you should continue to read [Preparing Your Input File](03_input_data.md) & [Running The GeoCARET Script](04_run.md) for full details of how to use GeoCARET.

## 1. Installing the dependencies

### Python

GeoCARET requires python 3.8.

- For installation on a personal computer:
- https://swcarpentry.github.io/python-novice-inflammation/setup.html
- See: Install Python, See: Option C: plain-vanilla Python Interpreter
- For installation on a University of Manchester machine: Check software centre for Anaconda Python.


#### Python on Windows 
In order to install GeoCARET on Windows you need to have Python 3.8 installed on your machine.

You can install Python 3.8 by following this link:

- https://www.python.org/downloads/release/python-3810/


### Terminal
- Use built-in CMD or powershell or install Git Bash on Windows (https://gitforwindows.org/).
- Use build-in terminal on OS X or linux.

### Gcloud command line tool
This tool requires the gcloud command line tool.
Download and install gcloud for your operating system here:
- https://cloud.google.com/sdk/docs/install

## 2. Preparing a python environment

### Windows cmd/Windows powershell (anaconda prompt)
- Download the GeoCARET tool code from GitHub and unzip the code into a folder called “HEET”
- Open Anaconda Prompt (search for “Anaconda Prompt” in Windows start menu) OR
- Open Anaconda Powershell Prompt (search for “Anaconda Prompt” in Windows start menu)
- Using the command prompt, navigate to the GeoCARET tool folder
- Install virtualenv:  
```
> pip install virtualenv
```

- Create a new virtual environment: 
- Check the location of you python 3.8 installation with `py --list-paths`
```
> virtualenv --python="C:\Users\mxcxcxc1\AppData\Local\Programs\Python\Python38\python.exe" heetenv
``` 
- Activate the virtual environment: 
```
> .\heetenv\Scripts\activate
``` 
- Install required libraries

```
pip install -r requirements.txt
```
Deactivate environment

```
deactivate
```

### Windows (git bash)

- Download the GeoCARET tool code from GitHub and unzip the code into a folder called “HEET”
- Open Git Bash (search for “Git Bash” in Windows start menu) Using the command prompt, navigate to the GeoCARET tool folder
- Install virtualenv:  
```
> pip install virtualenv
```
- Create a new virtual environment: 
  - Find python location `where python`
```
> virtualenv --python="C:\Users\mxcxcxc1\AppData\Local\Programs\Python\Python38\python.exe" heetenv
``` 
-	Activate the virtual environment: 
```
> source heetenv/Scripts/activate
``` 
- Install required libraries
```
pip install -r requirements.txt
```
- Deactivate environment
```
deactivate
```

### MAC OS X/ LINUX

- Download the GeoCARET tool code from GitHub and unzip the code into a folder called “HEET”
- Open Terminal 
- Using the command prompt, navigate to the GeoCARET tool folder
- Install virtualenv:  

```
> pip install virtualenv
```
-	Create a new virtual environment: 
  - Check the location of Python using `which -a python` and then `ls` to check path e.g.  `ls /usr/bin/python*`
```
> virtualenv --python="/usr/bin/python3.8" heetenv
``` 
-	Activate the virtual environment: 
```
> source heetenv/bin/activate
``` 
-	Install required libraries

```
pip install -r requirements.txt
```
-	Deactivate environment

```
deactivate
```




