import os
import sys
import shutil
import argparse
import logging # TBK: logging module
import logging.config # TBK
import configparser # TBK: To read config file
import tqdm # TBK
from time import time

from multiprocessing import Pool
import datetime

if __name__ == "__main__":

    v_string = "V2023.02.02"

    # create a parser for command line arguments
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-c", "--config", required = True, help = "Configuration ini file.")

    # read in the arguments
    args = parser.parse_args()

    if os.path.isfile(args.config) == False:
        print(f"No config file found called {args.config}. Aborting!")
        exit()

    ## Read in config options:
    working_dir = config['general']['working_dir'] # TBK: Working directory
    fast_scratch = config['segmentation']['fast_scratch'] # TBK: Fastest IO option for temporary files.

    shutil.rmtree(fast_scratch, ignore_errors=True)
    shutil.rmtree(working_dir + '/segmentation/', ignore_errors=True)
    shutil.rmtree(working_dir + '/classification/', ignore_errors=True)
    shutil.rmtree(working_dir + '/R/', ignore_errors=True)

    print('Done.')