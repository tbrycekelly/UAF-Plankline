# Documentation for UAF-Plankline
N.B. This version of plankline was forked and adapted significantly from the [original OSU version](https://zenodo.org/record/4641158)(DOI: 10.5281/zenodo.4641158)[1](#1). The following is a high-level summary of the changes applied in no particular order.

1. The segmentation and SCNN executables have been relocated to /opt/Threshold-MSER and /opt/SCNN, respectively. This allows all users to use these utilities without having to change/fix the paths.

2. All settings for segmentation and classification are now set within the .ini file itself. This is the only file that should be modified between projects/runs/etc. I am still working on the inline documentation in the config file. Eventually will make a "default.ini" to make copies of.

3. A new set of logging utilities are built in to allow for detailed and configurable logging routines to be used. All log entries are timestamped and given a status level: INFO, DEBUG, WARN, ERROR, CRITICAL. Default log files are places into the working directory (e.g. /media/plankline/Data/Data/projectX/) and timestamped. Logs for the executables are located in their respective folders.

4. Only some messages are printed to the screen by default (except warnings and errors), including only key information. A progress bar is shown for the majority of the processing.

5. Both scripts are now run by calling the python file directly.

6. Currently I have not implemented/adapted the previous directory/file verification functions that plankline used. So both scripts will rewrite all existing files and does not check/verify if output exists.

---








## References

<a id="1">[1]</a> Schmid, Moritz S, Daprano, Dominic, Jacobson, Kyler M, Sullivan, Christopher, Briseño-Avena, Christian, Luo, Jessica Y, & Cowen, Robert K. (2021). A Convolutional Neural Network based high-throughput image classification pipeline - code and documentation to process plankton underwater imagery using local HPC infrastructure and NSF's XSEDE (1.0.0). Zenodo. https://doi.org/10.5281/zenodo.4641158


