import os
import sys
import shutil
import argparse
import glob
import logging # TBK: logging module
import configparser # TBK: To read config file
import logging.config # TBK
import tqdm # TBK
import subprocess
import datetime
from time import time
from multiprocessing import Pool, Queue


#----------------------------------------------------------------------------------------
# classify
#
# Global Variables: scnn_directory, classification_dir, epoch, queue
#
def classify(tar_file):
    timer_classify = time()
    logger.info("Starting classify")
    date = datetime.datetime.now().strftime("%Y-%m-%d")

    if config['general']['compress_output'] == 'True':
        image_dir = tar_file.replace(".tar.gz", "") # remove extension
        tar_identifier = os.path.basename(image_dir)
        tmp_dir = config['segmentation']['fast_scratch'] + '/' + tar_identifier
        os.makedirs(tmp_dir, permis, exist_ok = True)
        log_file = f"{classification_dir}/{tar_identifier}-{date}.log"
    else:
        image_dir = tar_file.replace(".tar", "") # remove extension
        tar_identifier = os.path.basename(image_dir)
        tmp_dir = config['segmentation']['fast_scratch'] + '/' + tar_identifier
        os.makedirs(tmp_dir, permis, exist_ok = True)
        log_file = f"{classification_dir}/{tar_identifier}-{date}.log"

    image_dir = tmp_dir

    gpu_id = queue.get()

    logger.info(f"Starting on GPU {gpu_id}")
    logger.info(f'image_dir: {image_dir}')
    logger.info(f'tar_identifier: {tar_identifier}')

    # Untar files
    if config['general']['compress_output'] == 'True':
        untar_cmd = f'tar -xzf {tar_file} -C {image_dir} --strip-components=4 --wildcards "*.png"  >> {log_file} 2>&1' # TBK change strip-components to what you need.
        logger.debug('Untarring+unzipping files: ' + untar_cmd)
    else:
        untar_cmd = f'tar -xf {tar_file} -C {image_dir} --strip-components=4 --wildcards "*.png"  >> {log_file} 2>&1' # TBK change strip-components to what you need.
        logger.debug('Untarring files: ' + untar_cmd)
    
    timer_untar = time()
    os.system(untar_cmd)
    timer__untar = time() - timer_untar
    logger.debug(f"Untarring files took {timer_untar:.3f} s.")

    # Perform classification.
    scnn_cmd  = f"cd {scnn_directory}; nohup ./wp2 -start {epoch} -stop {epoch} -unl {image_dir} -cD {gpu_id} >> {log_file} 2>&1"
    logger.debug('Running SCNN: ' + scnn_cmd)
    logger.info('Start SCNN.')

    timer_scnn = time()
    os.system(scnn_cmd)
    timer_scnn = time() - timer_scnn
    logger.info('End SCNN.')
    logger.debug(f"SCNN took {timer_scnn:.3f} s.")

    # Move the csv file resulting from classification.
    logger.info(f"Looking for files in {scnn_directory}/Data/plankton/ that match the id: {tar_identifier}")
    csv_path = glob.glob(f"{scnn_directory}/Data/plankton/*{tar_identifier[10:]}*")
    if len(csv_path) > 0:
        csv_path = csv_path[0]
        csv_file = f"{classification_dir}/{tar_identifier}-{date}.csv"

        timer_move = time()
        shutil.move(csv_path, csv_file)
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

#----------------------------------------------------------------------------------------
# __main__
#
if __name__ == "__main__":
    v_string = "V2022.12.13"

    # create a parser for command line arguments
    parser = argparse.ArgumentParser(description="Classification tool for managing the isiis_scnn processes")
    parser.add_argument("-c", "--config", required = True, help = "Configuration ini file.")


    # read in the arguments
    args = parser.parse_args()
    config = configparser.ConfigParser() # TBK
    config.read(args.config) # TBK

    logging.config.fileConfig(config['logging']['config'], defaults={'date':datetime.datetime.now(),'path':config['general']['working_dir'],'name':'classification'}) # TBK
    logger = logging.getLogger('sLogger') # TBK

    permis = int(config['general']['dir_permissions'])
    scnn_instances = int(config['classification']['scnn_instances'])
    scnn_directory = config['classification']['scnn_dir']
    epoch = int(config['classification']['epoch'])
    scratch_base = os.path.abspath(config['general']['working_dir'])


    # Print config options to screen (TBK)
    logger.info(f"Starting plankline classification {v_string}")
    print(f"Starting Plankline Classification Script {v_string}")
    print(f"Configureation file: {args.config}")
    print(f"Segmentation on: {scratch_base}")
    print(f"Number of instances: {scnn_instances}")
    print(f"Epoch: {epoch}")
    print(f"Log configuration file: {config['logging']['config']}")

    # segmentation_dir is where the input data is taken from
    segmentation_dir = scratch_base + "/segmentation"
    classification_dir = scratch_base + "/classification"
    os.makedirs(classification_dir, permis, exist_ok = True)

    # make sure this is a valid directory
    if not os.path.exists(segmentation_dir):
        sys.exit("No directory segmentation")

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

    cp_file = classification_dir + '/' + str(datetime.datetime.now()) + args.config
    logger.debug(f"Copying ini file to classification directory {classification_dir}")
    logger.info(f"Copy of log file in {cp_file}")
    shutil.copy2(args.config, cp_file)
    logger.debug("Done.")
