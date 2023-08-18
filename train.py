import os
import sys
import shutil
import argparse
import logging # TBK: logging module
import logging.config # TBK
import configparser # TBK: To read config file
import tqdm # TBK
import subprocess
from time import time

from multiprocessing import Pool
import datetime




if __name__ == "__main__":

    v_string = "V2023.08.18"
    print(f"Starting Plankline Training Script {v_string}")
    
    # create a parser for command line arguments
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-c", "--config", required = True, help = "Configuration ini file.")

    # read in the arguments
    args = parser.parse_args()

    if os.path.isfile(args.config) == False:
        print(f"No config file found called {args.config}. Aborting!")
        exit()

    config = configparser.ConfigParser()
    if os.path.exists('default.ini'):
        config.read('default.ini')
    config.read(args.config)

    if config.has_option('logging', 'config') == False:
        print(f"No logging:config specified in {args.config}. Aborting!")
        exit()

    ## Setup logger
    logging.config.fileConfig(config['logging']['config'], defaults={'date':datetime.datetime.now().strftime("%Y%m%d-%H%M%S"),'path':model_dir,'name':'segmentation'})
    logger = logging.getLogger('sLogger')

    logger.info(f"Starting training script {v_string}")

    # Variables read in from the config file:
    config_version = config['general']['config_version']
    model_dir = config['training']['model_dir']
    fast_scratch = config['training']['fast_scratch']
    scnn_cmd = config['training']['scnn_cmd']
    start = config['training']['start']
    stop = config['training']['stop']
    batchsize = config['training']['batchsize']
    basename = config['training']['basename']
    vsp = config['training']['validationSetRatio']
    lrd = config['training']['learningRateDecay']
    ilr = config['training']['initialLearningRate']
    permis = int(config['general']['dir_permissions'])
    
    # Print config options to screen (TBK)
    print(f"Configuration file: {args.config} (Version {config_version})")
    print(f"Performing training for {model_dir}")

    ## Setup scratch for training
    fast_scratch = fast_scratch + "/train-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    fast_data = fast_scratch + "/Data"
    fast_weights = fast_scratch + "/weights"

    
    cp_file = model_dir + '/' + str(datetime.datetime.now()) + ' ' + args.config
    logger.debug(f"Copying ini file to training directory {model_dir}")
    logger.info(f"Copy config to {cp_file}")
    shutil.copy2(args.config, cp_file)


    logger.info("Setting up directories.")
    logger.debug(f"Setting up {fast_scratch}")

    # Copy training set, and models
    time_copy = time()
    shutil.copytree(model_dir, fast_scratch)
    time_copy = time() - time_copy
    logger.info(f"Copy to scratch took {time_copy:.3f} s.")
    print(f"Copy to scratch took {time_copy:.1f} s.")

    timer_train = time()
    for i in list(range(int(start), int(stop)+1)):
        ## Format training call:
        train = f'\"{scnn_cmd}\" -project {fast_scratch} -start {i} -stop {i+1} -batchSize {batchsize} -basename {basename} -vsp {vsp} -lrd {lrd} -ilr {ilr} -cD 0'
        train_call = [scnn_cmd, '-project', fast_scratch, '-start', str(i), '-stop', str(i+1), '-batchSize', batchsize, '-basename', basename, '-vsp', vsp, '-lrd', lrd, '-ilr', ilr, '-cD', '0']
        logger.info("Training call: " + train)

        result = subprocess.run(train_call, stdout = subprocess.PIPE)
        result = result.stdout.decode('utf-8')
        result = result.split('\n')

        if len(result) > 84:
            print(result[84:])
            logger.debug(result[84:])
        else:
            logger.debug(result)
            print(result)
    
    timer_train = time() - timer_train

    logger.debug(f"Training finished in {timer_train:.3f} s.")
    print(f"Finished training in {timer_train:.1f} seconds.")
    shutil.copytree(fast_scratch, model_dir)
    shutil.rmtree(fast_scratch, ignore_errors=True)

    logger.debug("Done.")
    
