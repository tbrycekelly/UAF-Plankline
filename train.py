#!/usr/bin/env python3
"""Training script for UAF-Plankline
    This is the training script used to facilitate training of new SCNN models.
    Settings for this script come exclusively from the configuration ini file
    passed: 
        
        e.g. python3 train.py -c config.ini
    
    Importantly, teh script copies all data to a temporary scratch directory and 
    then copies results back onces completed. If there is a failure then no model
    epochs will be saved. The user is free to grab them from the scratch_dir.

Usage:
    ./train.py -c <config.ini>

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
import logging # TBK: logging module
import logging.config # TBK
import configparser # TBK: To read config file
import tqdm # TBK
import subprocess
from time import time
import psutil
from multiprocessing import Pool
import datetime
import tensorflow as tf
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pathlib
import defs
import os
from PIL import Image


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


def classify(model_file, input_dir):
    model = tf.keras.models.load_model(model_file)

    pad(input_dir)
    images = []
    image_files = []
    for img in os.listdir(input_dir):
        image_files.append(img)
        img = tf.keras.preprocessing.image.load_img(input_dir+img, target_size=(128, 128), color_mode='grayscale')
        #img = img.img_to_array(img)
        img = np.expand_dims(img, axis=0)
        images.append(img)
    images = np.vstack(images)


    predictions = model.predict(images)
    prediction_labels = np.argmax(predictions, axis=-1)
    np.savetxt('prediction.csv', predictions, delimiter=',')

    with open('prediction_names.csv', newline='', mode='w') as csvfile:
        csvwritter = csv.writer(csvfile, delimiter='\n')
        csvwritter.writerow(image_files)


def print_config(config):
    # This function provides information for the user to both their screen and to the configured log file.
    logger.info(f"Starting training script {v_string}")

    print(f"Configuration file:    {args.config} (Version {config_version})")
    print(f"Performing training for {model_name}")
    print(f"Performing training from {model_dir}")
    print(f"Starting Epoch:        {start_epoch}")
    print(f"Stopping Epoch:        {stop_epoch}")
    print(f"Validation Ratio:      {val_ratio}")


def load_model(config):
    if int(config['start']) > 0:
        return(tf.keras.models.load_model(config['training_dir'], config))
    
    init_model(config)
    

def train_model(model, config):
    history = model.fit(train_ds,
                        validation_data=val_ds,
                        epochs=int(config['start']),
                        initial_epoch=config['stop'],
                        batch_size = config['batchsize'])
    
    logger.info(print(history))
    model

if __name__ == "__main__":

    v_string = "V2023.10.09"
    print(f"Starting CNN Model Training Script {v_string}")
    
    # create a parser for command line arguments
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-c", "--config", required = True, help = "Configuration ini file.")
    args = parser.parse_args()

    if os.path.isfile(args.config) == False:
        print(f"No config file found called {args.config}. Aborting!")
        exit()

    config = configparser.ConfigParser()
    config.read(args.config)

    if config.has_option('logging', 'config') == False:
        print(f"No logging:config specified in {args.config}. Aborting!")
        exit()

    permis = int(config['general']['dir_permissions'])
    logging.config.fileConfig(config['logging']['config'], defaults={'date':datetime.datetime.now().strftime("%Y%m%d-%H%M%S"),'path':model_dir,'name':'train'})
    logger = logging.getLogger('sLogger')

    print_config(config)

    # Save INI file
    cp_file = model_dir + '/' + str(datetime.datetime.now().strftime("%Y%m%d-%H%M%S")) + ' ' + args.config
    logger.debug(f"Copying ini file to training directory {model_dir}")
    logger.info(f"Copy config to {cp_file}")
    shutil.copy2(args.config, cp_file)
    
    timer_train = time()
    model = load_model(config['training'])
    model = train_model(model, config['training'])
    model.save() ## TODO: Name??
    timer_train = time() - timer_train

    logger.debug(f"Training finished in {timer_train:.3f} s.")
    print(f"Finished training in {timer_train:.1f} seconds.")

    logger.debug("Done.")
    
