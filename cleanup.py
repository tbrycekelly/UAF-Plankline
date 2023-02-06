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
    parser.add_argument("-f", action = 'store_true')

    # read in the arguments
    args = parser.parse_args()

    if os.path.isfile(args.config) == False:
        print(f"No config file found called {args.config}. Aborting!")
        exit()

    config = configparser.ConfigParser()
    config.read(args.config)

    ## Read in config options:
    working_dir = config['general']['working_dir'] # TBK: Working directory
    fast_scratch = config['segmentation']['fast_scratch'] # TBK: Fastest IO option for temporary files.

    if args.f is True:
        if os.path.isdir(fast_scratch + '/segment/'):
            shutil.rmtree(fast_scratch + '/segment/', ignore_errors = True)

        if os.path.isdir(working_dir + '/segmentation/'):
            shutil.rmtree(working_dir + '/segmentation/', ignore_errors = True)

        if os.path.isdir(working_dir + '/classification/'):
            shutil.rmtree(working_dir + '/classification/', ignore_errors = True)

        if os.path.isdir(working_dir + '/R/'):
            shutil.rmtree(working_dir + '/R/', ignore_errors = True)
    else:
        print("No -f flag provided. Rerun with -f flag if you want to delete the following directories:")
        if os.path.isdir(fast_scratch + '/segment/'):
            print(f"Directory: {fast_scratch + '/segment/':30} containing {(float(shutil.disk_usage(fast_scratch + '/segment/')[2])/10**9):.1f} GB")
        else:
            print(f"Directory: {fast_scratch + '/segment/':30} not found.")
        
        if os.path.isdir(working_dir + '/segmentation/'):
            print(f"Directory: {working_dir + '/segmentation/':30} containing {(float(shutil.disk_usage(working_dir + '/segmentation/')[2])/10**9):.1f} GB")
        else:
            print(f"Directory: {working_dir + '/segmentation/':30} not found.")
        
        if os.path.isdir(working_dir + '/classification/'):
            print(f"Directory: {working_dir + '/classification/':30} containing {(float(shutil.disk_usage(working_dir + '/classification/')[2])/10**9):.1f} GB")
        else:
            print(f"Directory: {working_dir + '/classification/':30} not found.")
        
        if os.path.isdir(working_dir + '/R/'):
            print(f"Directory: {working_dir + '/R/':30} containing {(float(shutil.disk_usage(working_dir + '/R/')[2])/10**9):.1f} GB")
        else:
            print(f"Directory: {working_dir + '/R/':30} not found.")
        

    print('Done.')