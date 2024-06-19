# Running The GeoCARET Script

## Syntax
The command line syntax to run the GeoCARET tool is:
```
> python heet_cli.py data/input-filename.csv projectname jobname dataset
```

Where:
* `data/input-filename.csv` is the path to the user inputs file. 
* `projectname` is the name of your Earth Engine project
* `jobname` is a short 10 character jobname to be used when creating output folders. May only contain the following characters A-Z, a-z, 0-9, -.
* `dataset` is the output dataset required: standard, extended, diagnostic, diagnostic-catch, diagnostic-res, diagnostic-riv


The data/ folder is currently empty; an example dams.csv file is available in tests/data;
copy this to data/ to do an example run. Assuming your Earth Engine project is called 'my-ee-project', you could run the GeoCARET tool by typing:

```
> python heet_cli.py data/dams.csv my-ee-project myanmar01 standard 
```

### Google cloud authentication

If this is the first time you've run the GeoCARET tool, you will be asked to authenticate with Google's cloud services:

1. You'll be shown a URL, which you should copy and paste into a web browser. In Windows PowerShell you can hold down the `Ctrl` key and click the URL to open it automatically.  
2. Follow the instructions to authenticate with Google
3. After authenticating, you'll be given a token, which you should paste back into the GeoCARET tool command line.
4. Press enter to start the analysis.

Once authenticated the GeoCARET analysis will run. This could take several minutes to complete. 

## Results and Visualization Script

!! **FIXME**: the visualization script will likely change and, if so, this part will need updating !!


Once GeoCARET completes its analysis, it will generate a number of output data files, both locally and inside your Cloud Project. See the [Output data documentation](05A_output_data.md) for full details of these outputs.

You will also be shown a link to a Google Earth Engine script for visualizing the results inside Earth Engine. If you paste this link into a web browser, you will be taken to the Earth Engine Code Editor, with the script pre-loaded.

The visualization script is generic and the 'user specified parameters' section at the top will need to be modified to visualize the results of a specific GeoCARET analysis. There are instructions for how to do this in the comments at the top of the script. 

Most importantly, you will need to change the `asset_folder` variable to point to the location of the outputs of GeoCARET analysis you wish to visualize:

```
var asset_folder = "projects/your-project-name/assets/top-level-folder/XHEET/JOBNAME_YYYYMMDD-HHMM";
```
Where:

* `your-project-name` should be replaced with the name of your Earth Engine Cloud Project
* `top-level-folder` should be replaced with the name of the top-level assets folder inside that project
* `JOBNAME_YYYYMMDD-HHMM` should be replaced with the appropriate GeoCARET outputs folder 

Once you've modified the parameters as appropriate, you can run the script. 

!! **FIXME**: Add some documentation explaining the visualization produced by the script here !!

## Logs
Any errors and issues will be logged in the logfile heet.log. A new log file is created with each run.

## Usage Examples
### Windows cmd/Windows PowerShell (anaconda prompt)

- Activate the virtual environment: 
```
> .\heetenv\Scripts\activate
``` 
- Run the GeoCARET tool code
```
> python heet_cli.py data/dams.csv myanmar01 standard
``` 
- When done, deactivate environment

```
deactivate
```

### Windows (git bash)
- Activate the virtual environment: 
```
> source heetenv/Scripts/activate
``` 
- Ensure UTF-8 characters display in terminal:

```
> export PYTHONIOENCODING=utf-8
```
- Run code

```
> python heet_cli.py data/dams.csv myanmar01 standard 

``` 
- When done, deactivate environment.

```
deactivate
```

### Mac os x / linux
- Activate the virtual environment: 
```
> source heetenv/bin/activate
``` 
- Run code

```
> python heet_cli.py data/dams.csv myanmar01 standard

``` 
- Deactivate environment

```
deactivate
```

