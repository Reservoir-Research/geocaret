
# Running The Heet Script

## Syntax
The command line syntax to run the heet tool is:
```
> python heet/heet_cli.py dams.csv myanmar01 standard 
```
Three arguments must be supplied:
```
> python heet/heet_cli.py [1]dams.csv [2]myanmar01 [3]standard 
```
- [1] The path to the user inputs file
- [2] A short jobname to be used when creating output folders. May onlye contain the following characters A-Z, a-z, 0-9, -.
- [3] The output dataset required: standard, extended, diagnostic or dev

## Logs
Any errors and issues will be logged in the logfile heet.log. A new log file is created with each run.

## Usage Examples
### Windows cmd/Windows powershell (anaconda prompt)

- Activate the virtual environment: 
```
> .\heetenv\Scripts\activate
``` 
- Run the heet tool code
```
> python heet/heet_cli.py dams.csv myanmar01 standard
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
> python heet/heet_cli.py dams.csv myanmar01 standard 

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
> python heet/heet_cli.py dams.csv myanmar01 standard

``` 
- Deactivate environment

```
deactivate
```

