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

    v_string = "V2023.08.16"
    print(f"Starting Plankline Training Script {v_string}")
    
    # create a parser for command line arguments
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-c", "--config", required = True, help = "Configuration ini file.")
    parser.add_argument("-d", "--directory", required = True, help = "Training Directory")

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

    working_dir = os.path.abspath(args.directory)
    model_dir = config['training']['model_dir']
    fast_scratch = config['training']['fast_scratch']
    scnn_cmd = config['training']['scnn_cmd']
    start = config['training']['start']
    end = config['training']['end']
    batchsize = config['training']['batchsize']
    basename = config['training']['basename']
    vsp = config['training']['validationSetRatio']
    lrd = config['training']['learningRateDecay']
    ilr = config['training']['initialLearningRate']
    permis = int(config['general']['dir_permissions'])
    

    ## Setup logger
    logging.config.fileConfig(config['logging']['config'], defaults={'date':datetime.datetime.now().strftime("%Y%m%d-%H%M%S"),'path':working_dir,'name':'segmentation'})
    logger = logging.getLogger('sLogger')

    logger.info(f"Starting training script {v_string}")

    # Print config options to screen (TBK)
    print(f"Configureation file: {args.config}")


    ## Setup scratch for training
    fast_scratch = fast_scratch + "/train-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    fast_data = fast_scratch + "/Data"
    fast_weights = fast_scratch + "/weights"

    
    cp_file = working_dir + '/' + str(datetime.datetime.now()) + ' ' + args.config
    logger.debug(f"Copying ini file to training directory {working_dir}")
    logger.info(f"Copy config to {cp_file}")
    shutil.copy2(args.config, cp_file)


    logger.info("Setting up directories.")
    logger.debug(f"Setting up {fast_scratch}")
    os.makedirs(fast_scratch, permis, exist_ok = True)
    #os.makedirs(fast_data, permis, exist_ok = True)
    #os.makedirs(fast_weights, permis, exist_ok = True)

    # Copy training set, and models
    shutil.copytree(model_dir, fast_data)

    timer_train = time()
    for i in list(range(int(start), int(end)+1)):
        ## Format training call:
        train = f'\"{scnn_cmd}\" -project {fast_scratch} -start {i} -end {i+1} -batchSize {batchsize} -basename {basename} -vsp {vsp} -lrd {lrd} -ilr {ilr} -cD 0'
        train_call = [scnn_cmd, '-project', fast_scratch, '-start', i, '-end', i+1, '-batchSize', batchsize, '-basename', basename, '-vsp', vsp, '-lrd', lrd, 'ilr', ilr, '-cD 0']
        logger.info("Training call: " + train)

        result = subprocess.run(train_call)
        logger.info(result.stdout.decode('utf-8'))
        print(result.stdout.decode('utf-8'))
        #os.system(train)
    
    timer_train = time() - timer_train

    logger.debug(f"Training finished in {timer_train:.3f} s.")
    print(f"Finished training in {timer_train:.1f} seconds.")
    shutil.copytree(fast_weights, model_dir + "/weights")

    logger.debug("Done.")
    
