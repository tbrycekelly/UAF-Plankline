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
        def get_size(start_path = '.'):
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(start_path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    # skip if it is symbolic link
                    if not os.path.islink(fp):
                        total_size += os.path.getsize(fp)

            return total_size

        print("No -f flag provided. Rerun with -f flag if you want to delete the following directories:")
        if os.path.isdir(fast_scratch + '/segment/'):
            print(f"Directory: {fast_scratch + '/segment/':30} containing {(get_size(fast_scratch + '/segment/')/10**9):.1f} GB")
        else:
            print(f"Directory: {fast_scratch + '/segment/':30} not found.")
        
        if os.path.isdir(working_dir + '/segmentation/'):
            print(f"Directory: {working_dir + '/segmentation/':30} containing {(get_size(working_dir + '/segmentation/')/10**9):.1f} GB")
        else:
            print(f"Directory: {working_dir + '/segmentation/':30} not found.")
        
        if os.path.isdir(working_dir + '/classification/'):
            print(f"Directory: {working_dir + '/classification/':30} containing {(get_size(working_dir + '/classification/')/10**9):.1f} GB")
        else:
            print(f"Directory: {working_dir + '/classification/':30} not found.")
        
        if os.path.isdir(working_dir + '/R/'):
            print(f"Directory: {working_dir + '/R/':30} containing {(get_size(working_dir + '/R/')/10**9):.1f} GB")
        else:
            print(f"Directory: {working_dir + '/R/':30} not found.")
        

    print('Done.')