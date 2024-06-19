# Background
To run the HEET tool on the command line, you will need to:

- Install a number of pre-requisites
- Be able to setup and activate a Python environment.  
- Run the Heet python script using the correct command line syntax

This document provides a guide to each step.

# Installing the Pre-requisuites

## Python

- For installation on a personal computer:
- https://swcarpentry.github.io/python-novice-inflammation/setup.html
- See: Install Python, See: Option C: plain-vanilla Python Interpreter
- For installation on a UoM machine: Check software centre for Anaconda Python.

## Terminal
- Use built-in CMD or powershell or install Git Bash on windows (https://gitforwindows.org/).
- Use build-in terminal on OS X or linux.

## Preparing a python environemnt

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

```
> virtualenv heetenv
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
```
> virtualenv heetenv
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
```
> virtualenv heetenv
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




