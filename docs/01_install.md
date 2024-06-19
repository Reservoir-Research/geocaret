# Installation
## Background
To run the HEET tool on the command line, you will need to:
- Be registered to use the Google Earth Engine service
- Install a number of pre-requisites
- Be able to setup and activate a Python environment.  
- Run the Heet python script using the correct command line syntax

This document provides a guide to each step.

## Register to Use Google Earth Engine
- Create a Google account if you don't already haven one: https://support.google.com/accounts/answer/27441?hl=en
- Go to code.earthengine.google.com 
- login with your Google account
- Earth Engine will  request access to your Google account - choose ‘allow’.
- Follow the link to go to the registration page, fill out the application and submit.
- Once you receive a confirmation email, you will be able to login to code.earthengine.google.com

## Installing the Pre-requisuites

### Python

- For installation on a personal computer:
- https://swcarpentry.github.io/python-novice-inflammation/setup.html
- See: Install Python, See: Option C: plain-vanilla Python Interpreter
- For installation on a University of Manchester machine: Check software centre for Anaconda Python.


#### Python on Windows 
In order to install HEET on Windows you need to have Python 3.8 installed on your machine.

You can install Python 3.8 by following this link:

- https://www.python.org/downloads/release/python-3810/


### Terminal
- Use built-in CMD or powershell or install Git Bash on Windows (https://gitforwindows.org/).
- Use build-in terminal on OS X or linux.

### Gcloud command line tool
This tool requires the gcloud command line tool.
Download and install gcloud for your operating system here:
- https://cloud.google.com/sdk/docs/install

## Preparing a python environment

### Windows cmd/Windows powershell (anaconda prompt)
- Download the HEET tool code from GitHub and unzip the code into a folder called “HEET”
- Open Anaconda Prompt (search for “Anaconda Prompt” in Windows start menu) OR
- Open Anaconda Powershell Prompt (search for “Anaconda Prompt” in Windows start menu)
- Using the command prompt, navigate to the HEET tool folder
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

- Download the HEET tool code from GitHub and unzip the code into a folder called “HEET”
- Open Git Bash (search for “Git Bash” in Windows start menu) Using the command prompt, navigate to the HEET tool folder
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

- Download the HEET tool code from GitHub and unzip the code into a folder called “HEET”
- Open Terminal 
- Using the command prompt, navigate to the HEET tool folder
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




