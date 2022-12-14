### Documentation for kelly-plankline
This version of plankline can be run from the command line and differs from the previous
version in the following ways:

1. The segmentation and SCNN executables have been relocated to /opt/Threshold-MSER and 
/opt/SCNN, respectively. This allows all users to use these utilities without having to 
change/fix the paths.

2. All settings for segmentation and classification are now set within the .ini file itself. 
This is the only file that should be modified between projects/runs/etc. I am still working
on the inline documentation in the config file. Eventually will make a "default.ini" to make
copies of.

3. A new set of logging utilities are built in to allow for detailed and configurable logging
routines to be used. All log entries are timestamped and given a status level: INFO, DEBUG,
WARN, ERROR, CRITICAL. Default log files are places into the working directory (e.g. /media/
plankline/Data/Data/projectX/) and timestamped. Logs for the executables are located in their
respective folders.

4. Messages are not printed to the screen by default (except warnings and errors) and instead
only a progress bar is shown. Later we can add more functionality, but KISS.

5. Both scripts are now run by calling the python file directly.

6. Currently I have not implemented/adapted the previous directory/file verification functions 
that plankline used. So both scripts will rewrite all existing files and not check/verify if output 
exists.

## To download (github):
git clone https://github.com/IBOOL/kelly-plankline.git

## To update (from within kelly-plankline directory):
git pull

## To run:

Edit the config file (or save a copy!):
./kelly-plankline/plankton_config.ini

In the command line, navigate to the base directory:
> cd /home/tbkelly/Documents/kelly-plankline

Run segmentation:
> python3 segmentation.py -c plankton_config.ini

Run classification:
> python3 classification.py -c plankton_config.ini


## If there are errors, then you shuld at least get an on screen message about the issue. Hopefully
the log files will also contain some information!





