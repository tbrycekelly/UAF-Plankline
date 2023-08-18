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

    output_dir = os.path.abspath(args.directory)
    train_dir = config['training']['dataset_dir']
    model_dir = config['training']['model_dir']
    scratch_dir = config['training']['fast_scratch']
    scnn_cmd = config['training']['scnn_cmd']
    start = config['training']['scnn_cmd']
    end = config['training']['scnn_cmd']
    batchsize = config['training']['scnn_cmd']
    basename = config['training']['scnn_cmd']
    vsp = config['training']['validationSetRatio']
    lrd = config['training']['learningRateDecay']
    ilr = config['training']['initialLearningRate']
    permis = int(config['general']['dir_permissions'])
    

    ## Setup scratch for training
    fast_scratch = fast_scratch + "/train-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    fast_data = fast_scratch + "/Data"
    fast_weights = fast_scratch + "/weights"

    logger.info("Setting up directories.")
    logger.debug(f"Setting up {fast_scratch}")
    os.makedirs(fast_scratch, permis, exist_ok = True)
    os.makedirs(fast_data, permis, exist_ok = True)
    os.makedirs(fast_weights, permis, exist_ok = True)

    # Copy training set and create subfolders
    shutil.copy2(train_dir, fast_data)

    if start > 0:
        model_init = model_dir + "/" + basename + "_" + start
        shutil.copy2(model_init, fast_weights)

    ## Setup logger
    logging.config.fileConfig(config['logging']['config'], defaults={'date':datetime.datetime.now().strftime("%Y%m%d-%H%M%S"),'path':working_dir,'name':'segmentation'})
    logger = logging.getLogger('sLogger')

    logger.info(f"Starting training script {v_string}")

    # Print config options to screen (TBK)
    print(f"Configureation file: {args.config}")

    
    train = f'\"{scnn_cmd}\" -start {start} -end {end} -batchSize {batchsize} -basename {basename} -vsp {vsp} -lrd {lrd} -ilr {ilr} -cD 0'
    train_call = [scnn_cmd, '-start', start, '-end', end, '-batchSize', batchsize, '-basename', basename, '-vsp', vsp, '-lrd', lrd, 'ilr', ilr, '-cD 0']
    logger.info("Training call: " + train)

    timer_train = time()
    result = subprocess.run(train_call)
    logger.info(result.stdout.decode('utf-8'))
    print(result.stdout.decode('utf-8'))
    #os.system(train)
    timer_train = time() - timer_train

    logger.debug(f"Training finished in {timer_train:.3f} s.")
    print(f"Finished training in {timer_train:.1f} seconds.")

    cp_file = train_dir + '/' + str(datetime.datetime.now()) + ' ' + args.config
    logger.debug(f"Copying ini file to training directory {train_dir}")
    logger.info(f"Copy config to {cp_file}")
    shutil.copy2(args.config, cp_file)
    logger.debug("Done.")
    
