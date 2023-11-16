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
import shutil
import argparse
import logging # TBK: logging module
import logging.config # TBK
import configparser # TBK: To read config file
import tqdm # TBK
from time import time
import psutil
from multiprocessing import Pool
import datetime
import tensorflow as tf
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pathlib
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



def init_model(num_classes, img_height, img_width):

    #### # Plankline-ish
    model = tf.keras.models.Sequential(name=config['training']['model_name']) # Sequential alphabetic names in Alaska
    model.add(tf.keras.layers.InputLayer(input_shape=(img_height,img_width,1)))
    model.add(tf.keras.layers.Rescaling(-1./255, 1))
    model.add(tf.keras.layers.RandomRotation(1))
    model.add(tf.keras.layers.RandomFlip("horizontal"))

    model.add(tf.keras.layers.Conv2D(96, 11, activation='relu'))
    model.add(tf.keras.layers.Conv2D(96, 3, activation='relu'))
    model.add(tf.keras.layers.MaxPooling2D(pool_size=(2,2)))
    model.add(tf.keras.layers.BatchNormalization())

    model.add(tf.keras.layers.Conv2D(96, 3, activation='relu', padding='same'))
    model.add(tf.keras.layers.Conv2D(96, 3, activation='relu', padding='same'))
    model.add(tf.keras.layers.MaxPooling2D(pool_size=(2,2)))

    model.add(tf.keras.layers.Conv2D(128, 3, activation='relu', padding='same'))
    model.add(tf.keras.layers.Conv2D(128, 3, activation='relu', padding='same'))
    model.add(tf.keras.layers.MaxPooling2D(pool_size=(2,2)))
    model.add(tf.keras.layers.BatchNormalization())

    model.add(tf.keras.layers.Conv2D(256, 3, activation='relu', padding='same'))
    model.add(tf.keras.layers.Conv2D(256, 3, activation='relu', padding='same'))
    model.add(tf.keras.layers.MaxPooling2D(pool_size=(2,2)))
    model.add(tf.keras.layers.BatchNormalization())

    model.add(tf.keras.layers.Conv2D(192, 3, activation='relu', padding='same'))
    model.add(tf.keras.layers.Conv2D(192, 1, activation='relu', padding='same'))
    model.add(tf.keras.layers.MaxPooling2D(pool_size=(2,2)))
    model.add(tf.keras.layers.BatchNormalization())
    #model.add(tf.keras.layers.Dropout(0.1))

    model.add(tf.keras.layers.Conv2D(256, 1, activation='relu', padding='same'))
    model.add(tf.keras.layers.Conv2D(256, 1, activation='relu', padding='same'))
    #model.add(tf.keras.layers.MaxPooling2D(pool_size=(2,2)))
    #model.add(tf.keras.layers.BatchNormalization())
    #model.add(tf.keras.layers.Dropout(0.1))

    #model.add(tf.keras.layers.Conv2D(256, 2, activation='relu', padding='same'))
    #model.add(tf.keras.layers.Conv2D(256, 2, activation='relu', padding='same'))

    model.add(tf.keras.layers.GlobalAveragePooling2D())
    model.add(tf.keras.layers.Dense(256, activation='relu'))
    model.add(tf.keras.layers.Dropout(0.3))
    model.add(tf.keras.layers.Dense(256, activation='relu'))
    model.add(tf.keras.layers.Dropout(0.3))
    model.add(tf.keras.layers.Dense(num_classes, activation='softmax'))
    model.summary()

    model.compile(optimizer='adam', loss=tf.keras.losses.SparseCategoricalCrossentropy(), metrics=['accuracy'])
    
    return(model)


def load_model(config):
    #if int(config['training']['start']) > 0:
    #    return(tf.keras.models.load_model(config['training']['training_dir'], config))
    
    return(init_model(109, int(config['training']['image_size']), int(config['training']['image_size'])))
    

def train_model(model, config, train_ds, val_ds):
    history = model.fit(train_ds,
                        validation_data=val_ds,
                        epochs=int(config['training']['stop'])-int(config['training']['start']),
                        initial_epoch=int(config['training']['start']),
                        batch_size = int(config['training']['batchsize']))
    
    
    return(model)


def init_ts(config):
    train_ds, val_ds = tf.keras.utils.image_dataset_from_directory(
        config['training']['scnn_dir'] + '/data',
        interpolation='area',
        validation_split = 0.2,
        subset = "both",
        seed = 123,
        image_size = (int(config['training']['image_size']), int(config['training']['image_size'])),
        batch_size = int(config['training']['batchsize']),
        color_mode = 'grayscale')
    return(train_ds, val_ds)

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
    
    train_ds, val_ds = init_ts(config)
    model = load_model(config)
    model = train_model(model, config, train_ds, val_ds)
    model.save(config['training']['scnn_dir'] + '/' + config['training']['model_name'])
