#!/usr/bin/env python3
"""Segmentation script for UAF-Plankline

Usage:
    ./segmentation.py -c <config.ini> -d <project directory>

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
from time import time
import psutil
from PIL import Image
import cv2
import numpy as np
import time

from multiprocessing import Pool
import datetime


def bbox_area(bbox):
    res = []
    for p in bbox:
        res.append(abs(p[2]*p[3]))
    return res

def intersection(boxA, boxB):
    # determine the (x, y)-coordinates of the intersection rectangle
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    # compute the area of intersection rectangle
    interArea = abs(max((xB - xA, 0)) * max((yB - yA), 0))

    return interArea


def seg_image(imgs, config):
    for path in imgs:
        time1 = time.time()

        ## Read img and flatfield
        img = cv2.imread(path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = np.array(gray)
        field = np.quantile(gray, q=float(config['segmentation']['flatfield_q']), axis=0)
        gray = (gray / field.T * 255.0)
        gray = gray.clip(0,255).astype(np.uint8)

        # Detect regions
        mser = cv2.MSER_create(delta=int(config['segmentation']['delta']), min_area=int(config['segmentation']['min_area']), max_area=int(config['segmentation']['max_area']), max_variation=0.5, min_diversity=0.1)
        regions, bboxes = mser.detectRegions(gray)
        area = bbox_area(bboxes)

        for x in range(len(area)-1):
            for y in range(x+1, len(area)):
                overlap = intersection([bboxes[x][0], bboxes[x][1], bboxes[x][0]+bboxes[x][2], bboxes[x][1] + bboxes[x][3]], [bboxes[y][0], bboxes[y][1], bboxes[y][0]+bboxes[y][2], bboxes[y][1] + bboxes[y][3]])
                if overlap * 1. / max(area[x], area[y]) > float(config['segmentation']['overlap']):
                    if area[x] > area[y]:
                        bboxes[y] = [0,0,0,0]
                    else:
                        bboxes[x] = [0,0,0,0]

        area = bbox_area(bboxes)
        bboxes = bboxes[np.array(area) > 0]
        time2 = time.time()

        # Draw the regions on the image
        #for p in bboxes:
        #    cv2.rectangle(gray, (p[0], p[1]), (p[0] + p[2], p[1] + p[3]), (255, 0, 0), 2)

        for i in range(len(bboxes)):
            im = Image.fromarray(gray[bboxes[i][1]:(bboxes[i][1] + bboxes[i][3]), bboxes[i][0]:(bboxes[i][0] + bboxes[i][2])])
            im.save(f"./full_frames/test_{i:04}.png")

        #cv2.imshow("MSER regions", gray)
        #cv2.waitKey(0)

        print(f'Number of ROIs: {len(bboxes):,}')
        print(f'Total area of ROIs: {sum(area):,}')
        print(f'Time spend: {time2-time1:.1f} sec')
    

def split_avi(path):
    
    ffmpeg_call = f"ffmpeg -i myfile.avi -r 1000 -f image2 image-%07d.png"
    return path

def config_checks(config):
    if config.has_option('logging', 'config') == False:
        print(f"No logging:config specified in {args.config}. Aborting!")
        exit()
    
    

if __name__ == "__main__":
    """The main entry point and script for segmentation."""

    v_string = "V2023.10.10"
    print(f"Starting Segmentation Script {v_string}")
    session_id = str(datetime.datetime.now().strftime("%Y%m%d_%H%M%S")).replace(':', '')
    
    # create a parser for command line arguments
    parser = argparse.ArgumentParser(description="Segmentation tool for the plankton pipeline. Uses ffmpeg and seg_ff to segment a video into crops of plankton")
    parser.add_argument("-c", "--config", required = True, help = "Configuration ini file.")
    parser.add_argument("-d", "--directory", required = True, help = "Input directory containing ./raw/")

    # read in the arguments
    args = parser.parse_args()

    if os.path.isfile(args.config) == False:
        print(f"No config file found called {args.config}. Aborting!")
        exit()

    config = configparser.ConfigParser()
    config.read(args.config)

    config_checks(config)

    ## Read in config options:
    basename = config['segmentation']['segment_basename']
    permis = int(config['general']['dir_permissions'])
    SNR = int(config['segmentation']['signal_to_noise'])
    num_processes = int(config['segmentation']['segment_processes'])
    segment_path = config['segmentation']['segment'] # TBK: Absolute path to segmentation executable.
    fast_scratch = config['segmentation']['fast_scratch'] # TBK: Fastest IO option for temporary files.
    
    ## Determine directories
    raw_dir = os.path.abspath(args.directory) # /media/plankline/Data/raw/Camera1/Transect1
    working_dir = raw_dir.replace("raw", "analysis") # /media/plankline/Data/analysis/Camera1/Transect1
    working_dir = working_dir.replace("camera0/", "camera0/segmentation/") # /media/plankline/Data/analysis/Camera1/Transect1
    working_dir = working_dir.replace("camera1/", "camera1/segmentation/") # /media/plankline/Data/analysis/Camera1/segmentation/Transect1
    working_dir = working_dir.replace("camera2/", "camera2/segmentation/") # /media/plankline/Data/analysis/Camera1/segmentation/Transect1
    working_dir = working_dir.replace("camera3/", "camera3/segmentation/") # /media/plankline/Data/analysis/Camera1/segmentation/Transect1
    
    segment_dir = working_dir + f"-{basename}" # /media/plankline/Data/analysis/segmentation/Camera1/segmentation/Transect1(reg)
    fast_scratch = fast_scratch + "/segment-" + session_id

    os.makedirs(segment_dir, permis, exist_ok = True)
    os.makedirs(fast_scratch, permis, exist_ok = True)

    ## Setup logger
    logging.config.fileConfig(config['logging']['config'], defaults={'date':session_id,'path':segment_dir,'name':'segmentation'})
    logger = logging.getLogger('sLogger')

    cp_file = segment_dir + '/' + session_id + ' ' + args.config
    logger.debug(f"Copying ini file to segmentation directory {segment_dir}")
    logger.info(f"Copy config to {cp_file}")
    shutil.copy2(args.config, cp_file)


    logger.info(f"Starting plankline segmentation {v_string}")
    logger.debug(f"Segmentation on: {working_dir}")
    logger.debug(f"Machine scratch: {fast_scratch}")

    # Print config options to screen (TBK)
    print(f"Configureation file: {args.config}")
    print(f"Segmentation basename: {basename}")
    print(f"Segmentation from: {raw_dir}")
    print(f"Segmentation to: {segment_dir}")
    print(f"Scratch to: {fast_scratch}")
    print(f"SNR: {SNR}")
    print(f"Log configuration file: {config['logging']['config']}")

    # Check the permissions
    if os.access(segment_dir, os.W_OK) == False:
        logger.error(f"Cannot write to project directory {segment_dir}!")
        exit()

    if os.access(fast_scratch, os.W_OK) == False:
        logger.error(f"Cannot write to temporary directory {fast_scratch}!")
        exit()


    logger.info("Starting AVI loop.")

    avis = []
    logger.info("Looking at avi filepaths.")
    avis = [os.path.join(raw_dir, avi) for avi in os.listdir(raw_dir) if avi.endswith(".avi")]

    logger.debug("Found {length} AVI files.".format(length = len(avis)))
    print("Found {length} AVI files.".format(length = len(avis)))

    if (len(avis) == 0):
        logger.error(f"No avi files found in machine_scratch/raw make sure avi files are in {raw_dir}.")
        sys.exit(f"No avi files found in machine_scratch/raw make sure avi files are in {raw_dir}.")

    timer_pool = time()
    for f in tqdm(avis):
        img_path = split_avis(f)
        imgs = [os.path.join(img_path, i) for i in os.list.dir(img_path) if i.endswith('.png')]
        seg_image(imgs)
    timer_pool = time() - timer_pool

    logger.debug(f"Finished segmentation in {timer_pool:.3f} s.")
    print(f"Finished segmentation in {timer_pool:.1f} seconds.")

    logger.debug(f"Deleting temporary directory {fast_scratch}.")
    shutil.rmtree(fast_scratch, ignore_errors=True)

    logger.debug("Done.")
    
