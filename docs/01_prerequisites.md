# GeoCARET Prerequisites

## Background
Before you can run the GeoCARET tool, you will need to:

1. Be registered to use the Google Earth Engine service and create an associated Cloud Project.
2. Request access to the GeoCARET private assets

This document provides a guide to each step.

## 1. Register to Use Google Earth Engine and create an associated Cloud Project

GeoCARET relies on Google Earth Engine - Google's cloud-based platform developed for planetary-scale environmental analysis. GeoCARET uses Google Earth Engine as a backend for performing geomatry operations and data processing and as a database of global spatial data in the form of GIS layers.

You must be registered with Google Earth Engine to make use of GeoCARET. You must also have a Google Cloud Project associated with your Earth Engine account, which is where the GeoCARET tool outputs will be stored.

### Register with Google Earth Engine

A Google account is required to access Earth Engine. To facilitate the Earth Engine registration approval process, we suggest that you use a Google account created with an email associated with your organization.  For example, if you belong to an academic institution such as a University, you can create a Google account using your institution email address. This account can be created in addition to any personal Google account you may have. https://support.google.com/accounts/answer/27441?hl=en

Once you have a suitable Google account, follow these steps to access Earth Engine:

- Go to the Earth Engine Code Editor https://code.earthengine.google.com 
- You will be taken to the 'Choose an account' page
- Select the appropriate Google account to use and enter your password when prompted
- Earth Engine may request access to your Google account - choose ‘allow’.
- Follow the link to go to the registration page, fill out the application and submit.
- Once you receive a confirmation email, you will be able to login to https://code.earthengine.google.com

### Add a Cloud Project

You will also need to create a Google Cloud Project and add this to Earth Engine. GeoCARET will store its outputs inside the Cloud Project. 

Visit https://code.earthengine.google.com and click on the ‘Assets’ tab in the left-hand column.  Under the ‘CLOUD ASSETS’ section you should see either:

- The name of an existing cloud project, or
- The message: _“You haven’t selected any Cloud Projects yet. Click ‘Add a Project’ to access or upload assets.”_ 

If you need to add a Cloud Project, you have 2 options - add an existing project, or create a new one.

To add an existing project: 
 
1. Click the ‘ADD A PROJECT’ button and the ‘Select a Cloud Project’ dialog box will appear.  
2. Click the ‘Project’ box and a list of available cloud projects will appear. This list might be empty. 
3. If possible, choose the appropriate project and click the blue ‘SELECT’ button. The selected project will now appear under ‘CLOUD ASSETS’. 
 
However, if there were no cloud projects in the list to choose from, you’ll need to add a new project: 
 
1. First, click the ‘user’ icon at the top-right of the page, and choose ‘Register a new Cloud Project’ from the menu.  
2. On the next page click 'Register a Noncommercial or Commercial Cloud project' and follow the step-by-step instructions as appropriate. For example, you’ll probably want to choose ‘Unpaid usage’ and set ‘Academia & Research’ as the project type.  Click ‘Next’. 
3. Choose an organization, ID & name for the project and click ‘Continue to summary’. 
4. Click ‘Confirm’ to create the new project. 
 
Your Cloud Project will be created and you should be taken back to https://code.earthengine.google.com/, where your new project should appear under ‘CLOUD ASSETS’. If not, click the ‘refresh’ icon, or click ‘ADD A PROJECT” and this time your project should appear in the list.  
 
### Add an assets folder to the Cloud Project

The Cloud Project must contain at least one top-level 'assets' folder, which is where GeoCARET will store its outputs (inside a sub-folder it will create for you).

If required, click on the ‘expand’ icon next to the name of the project in the CLOUD ASSETS tree, to check if it contains any folders. 

If there are no folders under the project, you'll need to add one. If there already is a folder, but you'd like to use a different one, you'll need to add it. To add a folder, click the red ‘NEW’ button and choose ‘Folder’ from the menu. Enter a name for the folder when prompted.  
 
**NOTE**: GeoCARET will use the _first_ folder it finds alphabetically, so bear this in mind if adding more than one top-level folder to your Cloud Project.

## 2. Request access to the GeoCARET private assets

GeoCARET relies on several private assets not available in Google Earth Engine. You must be given access to these assets before you can run GeoCARET.

To request access to those assets please send email to:
[tomasz.k.janus@gmail.com](mailto:tomasz.k.janus@gmail.com?subject=[GeoCARET]%20Request%20Asset%20Access) or
[tjanus.heet@gmail.com](mailto:tjanus.heet@gmail.com?subject=[GeoCARET]%20Request%20Asset%20Access)
with the email address your registered with Google Earth Engine.
