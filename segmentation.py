#########################################################
#  segmentation.py
#
#  Copyright © 2021 Oregon State University
#
#  Moritz S. Schmid
#  Dominic W. Daprano
#  Kyler M. Jacobson
#  Christopher M. Sullivan
#  Christian Briseño-Avena
#  Jessica Y. Luo
#  Robert K. Cowen
#
#  Hatfield Marine Science Center
#  Center for Genome Research and Biocomputing
#  Oregon State University
#  Corvallis, OR 97331
#
#  This program is distributed WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# 
#  This program is distributed under the 
#  GNU GPL v 2.0 or later license.
#
#  Any User wishing to make commercial use of the Software must contact the authors 
#  or Oregon State University directly to arrange an appropriate license.
#  Commercial use includes (1) use of the software for commercial purposes, including 
#  integrating or incorporating all or part of the source code into a product 
#  for sale or license by, or on behalf of, User to third parties, or (2) distribution 
#  of the binary or source code to third parties for use with a commercial 
#  product sold or licensed by, or on behalf of, User.
# 
#  CITE AS:
# 
#  Schmid MS, Daprano D, Jacobson KM, Sullivan CM, Briseño-Avena C, Luo JY, Cowen RK. 2021.
#  A Convolutional Neural Network based high-throughput image 
#  classification pipeline - code and documentation to process
#  plankton underwater imagery using local HPC infrastructure 
#  and NSF’s XSEDE. [Software]. Zenodo. 
#  http://dx.doi.org/10.5281/zenodo.4641158
#
#########################################################

# BRIEF SCRIPT DESCRIPTION
# This script facilitates the starting of seg_ff which performs
# segmentation, and the measurement script which measures the sizes of objects in the images.
# Input data are expected to be AVI video files.
# Due to usual storage limitations on fast SSD storage, the script will only sync the
# files to SSD storage as needed.
#
# Make sure seg_ff, ffmpeg, and ffprobe are all within the path environment
# variable before running this.

import os
import sys
import shutil
import argparse
import logging # TBK: logging module
import logging.config # TBK 
import configparser # TBK: To read config file
import tqdm # TBK

from multiprocessing import Pool
import datetime


def directory(arg):
    if os.path.isdir(arg):
        if arg.endswith("/"): 
            arg = arg[:-1]
        return arg
    else:
        raise argparse.ArgumentTypeError("Not a valid directory path")
        

def seg_ff(avi, seg_output, SNR, segment_path):
    snr = str(SNR)
    epsilon = config['segmentation']['overlap']
    segment_log = scratch_base + '/segmentation/segment_' + str(datetime.datetime.now()) + '.log'
    full_output = config['segmentation']['full_output']
    
    seg = f'nohup {segment_path} -i {avi} -n 1 -o {seg_output} -s {snr} -e {epsilon} {full_output} > "{segment_log}" 2>&1'
    logger.info("Segmentation call: " + seg)

    os.system(seg)



#--------------------------------------------------------------------------
# local_main
#
# Pass in the avi file to be segmented, measured, and compressed.
# Necessary global variables: short_segment_scratch, SNR, fp_measure.
#
def local_main(avi):
    logging.info("Starting local_main.")
    
    # setup all of the local paths for the avi
    avi_file = os.path.basename(avi) # get only the file part of the full path
    avi_date_code = os.path.splitext(avi_file)[0] # remove .avi
    avi_segment_scratch = short_segment_scratch + "/" + avi_date_code
    seg_output = avi_segment_scratch + "_s"
    tif_structure = avi_segment_scratch + "/" + avi_date_code + "_%04d.tif"

    logging.info(f'avi_file: {avi_file}')
    logging.info(f'avi_date_code: {avi_date_code}')
    logging.info(f'avi_segment_scratch: {avi_segment_scratch}')
    logging.info(f'seg_output: {seg_output}')
    logging.info(f'tif_structure: {tif_structure}')
    logging.info(f'short_segment_scratch: {short_segment_scratch}')
    logging.info(f'scratch_base: {scratch_base}')

    # Printout to show progress.
    #
    logging.debug(f'Starting AVI file: {avi_file}')

    # Create necessary directory structure.
    #
    logging.info('Setting up AVI directories.')
    os.makedirs(avi_segment_scratch, permis, exist_ok=True)
    os.makedirs(seg_output, permis, exist_ok=True)
    
    # Segmentation.
    #   Run the segmentation on the AVI file.
    #
    logging.info('Starting segmentation.')
    seg_ff(avi, seg_output, SNR, segment_path)
          
    # Zip the segmentation output.
    # Create a new archive and use gzip to compress it.
    #
    logging.info('Start tarring.')
    tar_name = avi_segment_scratch + ".tar.gz"
    tar = "tar czf {tar} -C {dir_input} ." 
    logging.debug(tar.format(tar=tar_name, dir_input=seg_output))
    os.system(tar.format(tar=tar_name, dir_input=seg_output))
    logging.info('End tarring.')

    shutil.rmtree(seg_output)          # remove datecode_s/
    shutil.rmtree(avi_segment_scratch) # remove datecode/
    logging.info('End local_main.')

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

    # create a parser for command line arguments
    parser = argparse.ArgumentParser(description="Segmentation tool for the plankton pipeline. Uses ffmpeg and seg_ff to segment a video into crops of plankton")
    parser.add_argument("-c", "--config", required = True, help = "Configuration ini file.")
    
    # read in the arguments
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(args.config)
    
    logging.config.fileConfig(config['logging']['config'], defaults={'date':datetime.datetime.now(),'path':config['general']['working_dir'],'name':'segmentation'})
    logger = logging.getLogger('sLogger')
    
    ## Read in config options:
    permis = int(config['general']['dir_permissions'])
    SNR = int(config['segmentation']['signal_to_noise'])
    num_processes = int(config['segmentation']['segment_processes'])
    chunksize = int(config['segmentation']['chunksize'])
    scratch_base = os.path.abspath(config['general']['working_dir'])
    segment_path = config['segmentation']['segment']
    
    logger.debug(f"Segmentation on: {scratch_base}")
    logger.debug(f"Number of processes: {num_processes}")
    logger.debug(f"Machine scratch: {scratch_base}")

    # setup the output segmentation and measurements dir
    raw_scratch = scratch_base + "/raw"
    segment_scratch = scratch_base + "/segmentation"
    short_segment_scratch = segment_scratch # TBK: make so the work is done in the final directories since we don't need to move them around.
    
    
    logger.info("Setting up directories.")
    os.makedirs(raw_scratch, permis, exist_ok=True)
    os.makedirs(short_segment_scratch, permis, exist_ok=True)
    
    logger.info("Starting AVI loop.")
    
    # Get the list of avi files if transfering lazily.
    avis = []
    logging.info("Looking at avi filepaths without lazy_transfer")
    avis = [os.path.join(raw_scratch, avi) for avi in os.listdir(raw_scratch) if avi.endswith(".avi")]
    avis = FixAviNames(avis)
        
    logging.debug("Found {length} AVI files.".format(length = len(avis)))
    if (len(avis) == 0):
        logging.error("No avi files found in machine_scratch/raw make sure avi files are there")
        exit()

    # Parallel portion of the code.
    logging.info("Starting multithreaded segmentation call.")
    p = Pool(num_processes)

    # TBK:
    for _ in tqdm.tqdm(p.imap_unordered(local_main, avis, chunksize=chunksize), total=len(avis)):
        pass

    p.close()
    p.join() # blocks so that we can wait for the processes to finish

    logger.debug("Finished segmentation.")
    print("Finished Segmenting.")
    
