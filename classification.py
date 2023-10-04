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


def classify(tar_file):
    """Classify images contained within a TAR file."""
    
    timer_classify = time()
    logger.info("Starting classify")
    logger.debug(f"Basename for model run is {basename}.")
    logger.info(f"Current ram usage (GB): {psutil.virtual_memory()[3]/1000000000:.2f}")
    logger.info(f"Current cpu usage (%): {psutil.cpu_percent(4):.1f}")
    
    if config['general']['compress_output'] == 'True':
        image_dir = tar_file.replace(".tar.gz", "") # remove extension
        tar_identifier = os.path.basename(image_dir)
        tmp_dir = fast_scratch + '/' + tar_identifier
        os.makedirs(tmp_dir, permis, exist_ok = True)
    else:
        image_dir = tar_file.replace(".tar", "") # remove extension
        tar_identifier = os.path.basename(image_dir)
        tmp_dir = fast_scratch + '/' + tar_identifier
        os.makedirs(tmp_dir, permis, exist_ok = True)
        
    log_file = f"{classification_dir}/{tar_identifier}.log"
    image_dir = tmp_dir + '/'

    gpu_id = queue.get()

    logger.info(f"Starting on GPU {gpu_id}")
    logger.info(f'image_dir: {image_dir}')
    logger.info(f'tar_identifier: {tar_identifier}')

    logger.info(f'Creating directory: {image_dir}')
    tmp = os.makedirs(image_dir, permis, exist_ok = True)
    print(log)
    
    # Untar files
    if config['general']['compress_output'] == 'True':
        untar_cmd = f'tar -xzf "{tar_file}" -C "{image_dir}" --strip-components=4 --wildcards "*.png"  >> "{log_file}" 2>&1' # TBK change strip-components to what you need.
        logger.debug('Untarring+unzipping files: ' + untar_cmd)
    else:
        untar_cmd = f'tar -xf "{tar_file}" -C "{image_dir}" --strip-components=4 --wildcards "*.png"  >> "{log_file}" 2>&1' # TBK change strip-components to what you need.
        logger.debug('Untarring files: ' + untar_cmd)
    
    timer_untar = time()
    os.system(untar_cmd)
    timer_untar = time() - timer_untar
    logger.debug(f"Untarring files took {timer_untar:.3f} s.")

    # Perform classification.
    scnn_cmd  = f"cd '{scnn_directory}'; nohup ./scnn -start {epoch} -stop {epoch} -unl '{image_dir}' -cD {gpu_id} -basename {basename} >> '{log_file}' 2>&1"
    logger.debug('Running SCNN: ' + scnn_cmd)
    logger.info('Start SCNN.')

    timer_scnn = time()
    os.system(scnn_cmd)
    timer_scnn = time() - timer_scnn
    logger.info('End SCNN.')
    logger.debug(f"SCNN took {timer_scnn:.3f} s.")

    # Move the csv file resulting from classification.
    logger.info(f"Looking for files in {scnn_directory}/Data/{basename}/ that match the id: {tar_identifier}")
    csv_path = glob.glob(f"{scnn_directory}/Data/{basename}/*{tar_identifier[10:]}*")
    if len(csv_path) > 0:
        csv_path = csv_path[0]
        csv_file = f"{classification_dir}/{tar_identifier}.csv"

        timer_move = time()
        shutil.move(csv_path, csv_file)
        os.chmod(csv_file, permis)
        timer_move = time() - timer_move
        logger.debug(f"Moving csv(s) took {timer_move:.3f} s.")
        
    else:
        logger.error(f'No classification file found for {tar_identifier}')

    # Clean directories to make space.
    shutil.rmtree(image_dir)

    queue.put(gpu_id) # add the gpu id to the queue so that it can be allocated again
    logger.debug('End classify.')
    timer_classify = time() - timer_classify
    logger.debug(f"Total classification process took {timer_classify:.3f} s.")

    if config['R']['preprocess']:
        timer_pre = time()
        logger.debug('Preprocessing requested.')

        pre_cmd = 'Rscript "' + config['R']['script'] + '" ' + config['R']['dt'] + ' ' + config['R']['p_threshold'] + ' "' + csv_file + '"'
        logger.debug(f"Running preprocessing cmd: {pre_cmd}")
        os.system(pre_cmd)

        timer_pre = time() - timer_pre
        logger.debug(f"Preprocessing took {timer_pre:.3f} s.")


if __name__ == "__main__":
    """Main entry point for classification.py"""
    
    v_string = "V2023.10.03"
    session_id = str(datetime.datetime.now().strftime("%Y%m%d %H%M%S"))
    print(f"Starting Plankline Classification Script {v_string}")

    # create a parser for command line arguments
    parser = argparse.ArgumentParser(description="Classification tool for managing the isiis_scnn processes")
    parser.add_argument("-c", "--config", required = True, help = "Configuration ini file.")
    parser.add_argument("-d", "--directory", required = True)

    # read in the arguments
    args = parser.parse_args()
    config = configparser.ConfigParser()
    config.read(args.config)
    
    basename = config['classification']['scnn_basename']
    permis = int(config['general']['dir_permissions'])
    scnn_instances = int(config['classification']['scnn_instances'])
    scnn_directory = config['classification']['scnn_dir']
    scnn_command = config['classification']['scnn_cmd']
    epoch = int(config['classification']['epoch'])
    fast_scratch = config['segmentation']['fast_scratch']

    segmentation_dir = os.path.abspath(args.directory)  # /media/plankline/Data/analysis/segmentation/Camera1/Transect1 (reg)
    classification_dir = segmentation_dir.replace('segmentation', 'classification')  # /media/plankline/Data/analysis/segmentation/Camera1/Transect1 (reg)
    classification_dir = classification_dir.replace(')', f'-{basename})')  # /media/plankline/Data/analysis/segmentation/Camera1/Transect1 (reg plankton)
    fast_scratch = fast_scratch + "/classify-" + session_id
    
    os.makedirs(classification_dir, permis, exist_ok = True)
    os.makedirs(fast_scratch, permis, exist_ok = True)
    
    logging.config.fileConfig(config['logging']['config'], defaults={'date':session_id,'path':classification_dir,'name':'classification'}) # TBK
    logger = logging.getLogger('sLogger')

    # Print config options to screen (TBK)
    logger.info(f"Starting plankline classification {v_string}")
    print(f"Configureation file: {args.config}")
    print(f"Segmentation on: {segmentation_dir}")
    print(f"Number of instances: {scnn_instances}")
    print(f"Epoch: {epoch}")
    print(f"Log configuration file: {config['logging']['config']}")

    #  Check the permissions
    if os.access(segmentation_dir, os.W_OK) == False:
        logger.error(f"Cannot write to project directory {segmentation_dir}!")
        exit()
        
    if os.access(scnn_directory, os.W_OK) == False:
        logger.error(f"Cannot write to model directory {scnn_directory}!")
        exit()

    if os.access(fast_scratch, os.W_OK) == False:
        logger.error(f"Cannot write to temporary directory {fast_scratch}!")
        exit()

    # make sure this is a valid directory
    if not os.path.exists(segmentation_dir):
        logger.error(f"Segmentation directory {segmentation_dir} does not exist (and it should)!")
        exit()
        
    cp_file = classification_dir + '/' + session_id + ' ' + args.config
    logger.debug(f"Copying ini file to classification directory {classification_dir}")
    logger.info(f"Copy of log file in {cp_file}")
    shutil.copy2(args.config, cp_file)
    logger.debug("Done.")
    
    shutil.copy2(scnn_command, scnn_directory + '/scnn')

    if config['general']['compress_output'] == 'True':
        tars = [os.path.join(segmentation_dir, tar) for tar in os.listdir(segmentation_dir) if tar.endswith(".tar.gz")]
    else :
        tars = [os.path.join(segmentation_dir, tar) for tar in os.listdir(segmentation_dir) if tar.endswith(".tar")]

    if len(tars) == 0:
        sys.exit("Error: No tars file in segmenation directory")

    # setup gpu queue
    num_gpus = str(subprocess.check_output(["nvidia-smi", "-L"])).count('UUID') # read number of gpus from nvidia-smi output

    queue = Queue()
    for gpu_id in range(num_gpus):
        for _ in range(scnn_instances):
            queue.put(gpu_id)

    num_processes = scnn_instances * num_gpus
    tar_length = len(tars)
    logger.debug(f"Number of GPUs: {num_gpus}")
    logger.debug(f"SCNN Instances per GPU: {scnn_instances}")
    logger.debug(f"Total Processes: {num_processes}")
    logger.info(f"Identified {tar_length} tar.gz files")

    # this is the parallel portion of the code
    p = Pool(num_processes)

    # Start the Classification processes.
    timer_pool = time()
    for _ in tqdm.tqdm(p.imap_unordered(classify, tars, chunksize = 1), total = len(tars)):
        pass

    p.close()
    p.join() # blocks so that we can wait for the processes to finish
    
    timer_pool = time() - timer_pool
    logger.debug(f"Finished classification in {timer_pool:.3f} seconds.")
    print(f"Finished Classification in {timer_pool:.1f} seconds.")

    logger.debug(f"Deleting temporary directory {fast_scratch}.")
    shutil.rmtree(fast_scratch, ignore_errors=True)


