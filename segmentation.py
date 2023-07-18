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


def seg_ff(avi, seg_output, SNR, segment_path):
    snr = str(SNR)
    epsilon = config['segmentation']['overlap']
    delta = config['segmentation']['delta']
    max_area = config['segmentation']['max_area']
    min_area = config['segmentation']['min_area']

    segment_log = working_dir + '/segmentation/segment_' + str(datetime.datetime.now()) + '.log'
    full_output = config['segmentation']['full_output']

    seg = f'nohup \"{segment_path}\" -i \"{avi}\" -n 1 -o \"{seg_output}\" -s {snr} -e {epsilon} -M {max_area} -m {min_area} -d {delta} {full_output} >> \"{segment_log}\" 2>&1'
    logger.info("Segmentation call: " + seg)

    os.chmod(seg_output, permis)

    timer_seg = time()
    os.system(seg)
    timer_seg = time() - timer_seg
    logger.debug(f"Segmentation finished in {timer_seg:.3f} s.")



#--------------------------------------------------------------------------
# local_main
#
# Pass in the avi file to be segmented, measured, and compressed.
# Necessary global variables: short_segment_scratch, SNR, fp_measure.
#
def local_main(avi):
    logger.info("Starting local_main.")

    # setup all of the local paths for the avi
    avi_file = os.path.basename(avi) # get only the file part of the full path
    avi_date_code = os.path.splitext(avi_file)[0] # remove .avi
    avi_segment_scratch = fast_scratch + "/" + avi_date_code
    seg_output = avi_segment_scratch + "_s"
    out_dir = segment_dir + "/" + avi_date_code

    logger.info(f'avi_file: {avi_file}')
    logger.info(f'avi_date_code: {avi_date_code}')
    logger.info(f'avi_segment_scratch: {avi_segment_scratch}')
    logger.info(f'seg_output: {seg_output}')
    logger.info(f'segment_dir: {segment_dir}')
    logger.info(f'working_dir: {working_dir}')

    logger.debug(f'Starting AVI file: {avi_file}')

    # Create necessary directory structure.
    logger.info('Setting up AVI directories.')
    os.makedirs(avi_segment_scratch, permis, exist_ok=True)
    os.makedirs(seg_output, permis, exist_ok=True)

    # Segmentation.
    #   Run the segmentation on the AVI file.
    logger.info('Starting segmentation.')
    timer_seg = time()
    seg_ff(avi, seg_output, SNR, segment_path)
    timer_seg = time() - timer_seg
    logger.debug(f"Segmentation executable took {timer_seg:.3f} s.")

    # Zip the segmentation output.
    # Create a new archive and use gzip to compress it.
    if config['general']['compress_output'] == 'True':
        logger.info('Start tarring+compressing.')
        tar_name = out_dir + ".tar.gz"
        tar = f'tar czf \"{tar_name}\" -C \"{seg_output}\" .'
        logger.debug(tar)
        
        timer_tar = time()
        os.system(tar)
        os.chmod(tar_name, permis)
        timer_tar = time() - timer_tar

        logger.info(f'End tarring+compressing in {timer_tar:.3f} s.')
    else:
        logger.info('Start tarring')
        tar_name = out_dir + ".tar"
        tar = f'tar cf \"{tar_name}\" -C \"{seg_output}\" .'
        logger.debug(tar)

        timer_tar = time()
        os.system(tar)
        os.chmod(tar_name, permis)
        timer_tar = time() - timer_tar

        logger.info(f'End tarring in {timer_tar:.3f} s.')

    shutil.rmtree(seg_output)          # remove datecode_s/
    shutil.rmtree(avi_segment_scratch) # remove datecode/
    logger.info('End local_main.')

#------------------------------------------------------------------------------
# Fix Avi Names
#
def FixAviNames(avis):
  n = 0
  for Name in avis:
    FixedName = Name.replace(' ', '-')
    if not (FixedName == Name):
      os.rename(Name, FixedName)
      avis[n] = FixedName
    n += 1

  return avis

#------------------------------------------------------------------------------
# main
#
if __name__ == "__main__":

    v_string = "V2023.07.13"

    # create a parser for command line arguments
    parser = argparse.ArgumentParser(description="Segmentation tool for the plankton pipeline. Uses ffmpeg and seg_ff to segment a video into crops of plankton")
    parser.add_argument("-c", "--config", required = True, help = "Configuration ini file.")
    parser.add_argument("-d", "--directory", required = False, help = "Input directory containing ./raw/")

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

    if args.directory is not None:
        working_dir = os.path.abspath(args.directory)
    else:
        working_dir = os.path.abspath(config['general']['working_dir'])

    ## Setup logger
    logging.config.fileConfig(config['logging']['config'], defaults={'date':datetime.datetime.now().strftime("%Y%m%d-%H%M%S"),'path':working_dir,'name':'segmentation'})
    logger = logging.getLogger('sLogger')

    ## Read in config options:
    permis = int(config['general']['dir_permissions'])
    SNR = int(config['segmentation']['signal_to_noise'])
    num_processes = int(config['segmentation']['segment_processes'])
    segment_path = config['segmentation']['segment'] # TBK: Absolute path to segmentation executable.
    fast_scratch = config['segmentation']['fast_scratch'] # TBK: Fastest IO option for temporary files.

    logger.info(f"Starting plankline segmentation {v_string}")
    logger.debug(f"Segmentation on: {working_dir}")
    logger.debug(f"Number of processes: {num_processes}")
    logger.debug(f"Machine scratch: {fast_scratch}")

    # Print config options to screen (TBK)
    print(f"Starting Plankline Segmentation Script {v_string}")
    print(f"Configureation file: {args.config}")
    print(f"Segmentation on: {working_dir}")
    print(f"Scratch to: {fast_scratch}")
    print(f"Number of processes: {num_processes}")
    print(f"SNR: {SNR}")
    print(f"Log configuration file: {config['logging']['config']}")
    print(f"Compressing output: {config['general']['compress_output'] == 'True'}")

    # Check the permissions
    if os.access(working_dir, os.W_OK) == False:
        logger.error(f"Cannot write to project directory {working_dir}!")
        exit()

    if os.access(fast_scratch, os.W_OK) == False:
        logger.error(f"Cannot write to temporary directory {fast_scratch}!")
        exit()

    # setup the output segmentation and measurements dir
    raw_dir = working_dir + "/raw"
    segment_dir = working_dir + "/segmentation"
    fast_scratch = fast_scratch + "/segment-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    logger.info("Setting up directories.")
    logger.debug(f"Setting up {segment_dir} and {fast_scratch}")
    os.makedirs(segment_dir, permis, exist_ok = True)
    os.makedirs(fast_scratch, permis, exist_ok = True)

    logger.info("Starting AVI loop.")

    avis = []
    logger.info("Looking at avi filepaths without lazy_transfer")
    avis = [os.path.join(raw_dir, avi) for avi in os.listdir(raw_dir) if avi.endswith(".avi")]
    #avis = FixAviNames(avis)

    logger.debug("Found {length} AVI files.".format(length = len(avis)))
    print("Found {length} AVI files.".format(length = len(avis)))

    if (len(avis) == 0):
        logger.error("No avi files found in machine_scratch/raw make sure avi files are there")
        exit()

    # Parallel portion of the code.
    logger.info("Starting multithreaded segmentation call.")
    p = Pool(num_processes)

    # TBK:
    timer_pool = time()
    for _ in tqdm.tqdm(p.imap_unordered(local_main, avis), total = len(avis)):
        pass
    timer_pool = time() - timer_pool

    p.close()
    p.join() # blocks so that we can wait for the processes to finish

    logger.debug(f"Finished segmentation in {timer_pool:.3f} s.")
    print(f"Finished segmentation in {timer_pool:.1f} seconds.")

    logger.debug(f"Deleting temporary directory {fast_scratch}.")
    shutil.rmtree(fast_scratch, ignore_errors=True)

    cp_file = segment_dir + '/' + str(datetime.datetime.now()) + ' ' + args.config
    logger.debug(f"Copying ini file to segmentation directory {segment_dir}")
    logger.info(f"Copy config to {cp_file}")
    shutil.copy2(args.config, cp_file)
    logger.debug("Done.")
    
