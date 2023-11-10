#!/usr/bin/env python3
"""Classification script for UAF-Plankline

Usage:
    ./classification.py -c <config.ini> -d <project directory>

License:
    MIT License

    Copyright (c) 2023 Thomas Kelly

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
"""

import os
import sys
import shutil
import argparse
import glob
import logging
import configparser
import logging.config
import tqdm
import subprocess
import datetime
from time import time
from multiprocessing import Pool, Queue
import psutil
import tensorflow as tf
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pathlib
import csv
from PIL import Image
import os


def classify(model, tar_file):
    """Classify images contained within a TAR file."""
    
    timer_classify = time()
    logger.info("Starting classify")
    logger.debug(f"Basename for model run is {basename}.")
    logger.info(f"Current ram usage (GB): {psutil.virtual_memory()[3]/1000000000:.2f}")
    logger.info(f"Current cpu usage (%): {psutil.cpu_percent(4):.1f}")
    
    if config['general']['compress_output'] == 'True':
        image_dir = tar_file.replace(".tar.gz", "") # remove extension
    else:
        image_dir = tar_file.replace(".tar", "") # remove extension
        
    tar_identifier = os.path.basename(image_dir)
    tmp_dir = fast_scratch + '/' + tar_identifier
    os.makedirs(tmp_dir, permis, exist_ok = True)
    
    log_file = f"{classification_dir}/{tar_identifier}.log"
    image_dir = tmp_dir + '/'

    logger.info(f'image_dir: {tmp_dir}')
    logger.info(f'tar_identifier: {tar_identifier}')
    
    # Untar files
    if config['general']['compress_output'] == 'True':
        untar_cmd = f'tar -xzf "{tar_file}" -C "{tmp_dir}" --strip-components=4 --wildcards "*crop*.png"  >> "{log_file}" 2>&1' # TBK change strip-components to what you need.
        logger.debug('Untarring+unzipping files: ' + untar_cmd)
    else:
        untar_cmd = f'tar -xf "{tar_file}" -C "{tmp_dir}" --strip-components=4 --wildcards "*crop*.png"  >> "{log_file}" 2>&1' # TBK change strip-components to what you need.
        logger.debug('Untarring files: ' + untar_cmd)
    
    timer_untar = time()
    os.system(untar_cmd)
    timer_untar = time() - timer_untar
    logger.debug(f"Untarring files took {timer_untar:.3f} s.")

    # Load Dataset
    pad(tmp_dir)
    images = []
    image_files = []
    for img in os.listdir(tmp_dir):
        image_files.append(img)
        img = tf.keras.preprocessing.image.load_img(tmp_dir+img, target_size=(128, 128), color_mode='grayscale')
        img = np.expand_dims(img, axis=0)
        images.append(img)
    images = np.vstack(images)
    logger.debug(f'Found {len(image_files)} image files in {tmp_dir}.')

    # Perform classification.
    #scnn_cmd  = f"cd '{os.path.dirname(scnn_command)}'; nohup ./scnn -start {epoch} -stop {epoch} -unl '{tmp_dir}' -cD {gpu_id} -basename {basename} >> '{log_file}' 2>&1"
    timer_scnn = time()
    predictions = model.predict(images)
    timer_scnn = time() - timer_scnn
    logger.info('End SCNN.')
    logger.debug(f"SCNN took {timer_scnn:.3f} s.")

    prediction_labels = np.argmax(predictions, axis=-1)
    np.savetxt('prediction.csv', predictions, delimiter=',')

    with open('prediction_names.csv', newline='', mode='w') as csvfile:
        csvwritter = csv.writer(csvfile, delimiter='\n')
        csvwritter.writerow(image_files)

    logger.debug('End classify.')
    timer_classify = time() - timer_classify
    logger.debug(f"Total classification process took {timer_classify:.3f} s.")


def pad(path, ratio=0.2):
    dirs = os.listdir(path)
    count = 0
    for item in dirs:
        if not os.path.isfile(path + item):
            dirs2 = os.listdir(path + item + "/")
            for item2 in dirs2:
                if os.path.isfile(path+item+"/"+item2):
                    im = Image.open(path+item+"/"+item2)
                    width, height = im.size
                    if width > height * (1. + ratio):
                        left = 0
                        right = width
                        top = (width - height)//2
                        bottom = width
                        result = Image.new(im.mode, (right, bottom), (255))
                        result.paste(im, (left, top))
                        im.close()
                        result.save(path+item+"/"+item2)
                        #print(f"({width}x{height}) -> ({right}x{bottom})")
                        count+=1
                    elif height > width * (1. + ratio):
                        left = (height - width)//2
                        right = height
                        top = 0
                        bottom = height
                        result = Image.new(im.mode, (right, bottom), (255))
                        result.paste(im, (left, top))
                        im.close()
                        result.save(path+item+"/"+item2,)
                        #print(f"({width}x{height}) -> ({right}x{bottom})")
                        count+=1
    count


def print_config(config):
    logger.info(f"Starting plankline classification {v_string}")
    print(f"Configureation file: {args.config}")
    print(f"Segmentation on: {segmentation_dir}")
    print(f"Model: {config['classification']['model_name']}")
    print(f"Batchsize: {config['classification']['batchsize']}")
    print(f"Log configuration file: {config['logging']['config']}")
    
    logger.info(f'Basename of Model: {config["classification"]["model_name"]}')
    logger.info(f'Segmentation Directory: {segmentation_dir}')
    logger.info(f'Batchsize: {config["classification"]["batchsize"]}')


if __name__ == "__main__":
    """Main entry point for classification.py"""
    
    v_string = "V2023.10.05"
    session_id = str(datetime.datetime.now().strftime("%Y%m%d_%H%M%S")).replace(':', '')
    print(f"Starting Plankline Classification Script {v_string}")

    # create a parser for command line arguments
    parser = argparse.ArgumentParser(description="Classification tool for managing the isiis_scnn processes")
    parser.add_argument("-c", "--config", required = True, help = "Configuration ini file.")
    parser.add_argument("-d", "--directory", required = True)

    # read in the arguments
    args = parser.parse_args()
    config = configparser.ConfigParser()
    config.read(args.config)
    

    segmentation_dir = os.path.abspath(args.directory)  # /media/plankline/Data/analysis/segmentation/Camera1/Transect1-reg
    classification_dir = segmentation_dir.replace('segmentation', 'classification')  # /media/plankline/Data/analysis/segmentation/Camera1/Transect1-reg
    classification_dir = classification_dir + '-' + config["classification"]["model_name"] # /media/plankline/Data/analysis/segmentation/Camera1/Transect1-reg-Plankton
    fast_scratch = config['classification']['fast_scratch'] + "/classify-" + session_id
    
    os.makedirs(classification_dir, config['general']['dir_permissions'], exist_ok = True)
    os.makedirs(fast_scratch, config['general']['dir_permissions'], exist_ok = True)
    
    logging.config.fileConfig(config['logging']['config'], defaults={'date':session_id,'path':classification_dir,'name':'classification'}) # TBK
    logger = logging.getLogger('sLogger')

    print_config(config)
    
    
    ##  Check the permissions
    # segmentation_dir: Read
    # model_dir: Read
    # classification_dir: Write
    # Scratch: Write
    if os.access(segmentation_dir, os.R_OK) == False:
        logger.error(f"Cannot read segmentation directory {segmentation_dir}!")
        exit()

    if os.access(config['classification']['model_dir'], os.R_OK) == False:
        logger.error(f"Cannot read from model directory {config['classification']['model_dir']}!")
        exit()
        
    if os.access(classification_dir, os.W_OK) == False:
        logger.error(f"Cannot write to classification directory {classification_dir}!")
        exit()
        
    if os.access(fast_scratch, os.W_OK) == False:
        logger.error(f"Cannot write to temporary directory {fast_scratch}!")
        exit()
        
    logger.info('All directory permissions appear satisfied.')

        
    cp_file = classification_dir + '/' + args.config + session_id
    logger.debug(f"Copying ini file to classification directory {classification_dir}")
    logger.info(f"Copy of log file in {cp_file}")
    shutil.copy2(args.config, cp_file)
    logger.debug("Done.")
    
    tars = [os.path.join(segmentation_dir, tar) for tar in os.listdir(segmentation_dir) if tar.endswith(".tar")]
    
    if len(tars) == 0:
        logger.error(f'No tar files found in {segmentation_dir}.')
        sys.exit(f"Error: No tars file in segmenation directory: {segmentation_dir}")


    tar_length = len(tars)
    logger.info(f"Identified {tar_length} tar.gz files")
    model_path = config['classification']['model_dir'] + '/' + config['classification']['model_name']
    
    if not os.path.isdir(mode_path):
        logger.error(f'No model found at {model_path}!')
        sys.exit('Error, no model found at {model_path}')
    
    logger.debug(f'Loading model from {model_path}.')
    model = tf.keras.models.load_model(model_path)

    timer_pool = time()
    logger.info('Starting classification loop.')
    for f in tqdm(tars):
        classify(model, f)

    timer_pool = time() - timer_pool
    logger.debug(f"Finished classification in {timer_pool:.3f} seconds.")
    print(f"Finished Classification in {timer_pool:.1f} seconds.")

    logger.debug(f"Deleting temporary directory {fast_scratch}.")
    shutil.rmtree(fast_scratch, ignore_errors=True)


