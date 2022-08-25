#########################################################
#  classification.py
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
# This script will facilitate the starting of isiis_scnn on multiple GPUs
# based on the given arguments. Input data is expected to be in the form
# that the segmentation.py script will output.

import os
import sys
import shutil
import argparse
import glob

import subprocess
from datetime import datetime
from multiprocessing import Pool, Queue

#----------------------------------------------------------------------------------------
# directory
#
# custom arg type for argparse
#
def directory(arg):
    if os.path.isdir(arg):
        if arg.endswith("/"): 
            arg = arg[:-1]
        return arg
    else:
        raise argparse.ArgumentTypeError("Not a valid directory path")
        
        
#----------------------------------------------------------------------------------------
# classify
#
# Global Variables: scnn_directory, classification_dir, epoch, queue
#
def classify(tar_file):
    print ('Start: classify')
    stdout = sys.stdout

    today = datetime.now()
    date = today.strftime("%Y-%m-%d")

    image_dir = tar_file.replace(".tar.gz", "") # remove extension
    tar_identifier = os.path.basename(image_dir)

    log_file = "{classification_dir}/{tar_identifier}-{date}.log".format(classification_dir=classification_dir, tar_identifier=tar_identifier, date=date)

    with open(log_file, 'w') as l:
        sys.stdout = l 

        gpu_id = queue.get()

        print("Date:", date)
        print("Starting on GPU {gpu_id}".format(gpu_id=gpu_id))

        print ('image_dir: ', image_dir)
        image_dir = tar_file.replace(".tar.gz", "") # remove extension

        print ('tar_identifier: ', tar_identifier)
        tar_identifier = os.path.basename(image_dir)
        
        os.makedirs(image_dir, 0o755,exist_ok=True)
        untar_cmd = 'tar --no-overwrite-dir -xzf {tar_file} -C {image_dir} --strip-components=5 --wildcards "*.png"'

        print ('untar_cmd: ', untar_cmd.format(tar_file=tar_file, image_dir=image_dir))
        os.system(untar_cmd.format(tar_file=tar_file, image_dir=image_dir))

        # Perform classification.
        #
        # untar_cmd = 'tar --no-overwrite-dir -xzf {tar_file} -C {image_dir} --strip-components=3 --wildcards "*.png"'
        scnn_cmd  = "cd {scnn_dir}; isiis_scnn -start {epoch} -stop {epoch} -unl {image_dir} -cD {gpu_target} >> {log_file}"
        
        # print ('untar_cmd: ', untar_cmd)
        print ('scnn_cmd: ', scnn_cmd.format(scnn_dir=scnn_directory, epoch=epoch, image_dir=image_dir, gpu_target=gpu_id, log_file=log_file))
        print ('Start: SCNN')
        os.system(scnn_cmd.format(scnn_dir=scnn_directory, epoch=epoch, image_dir=image_dir, gpu_target=gpu_id, log_file=log_file))
        print ('End: SCNN')

        # Move the csv file resulting from classification.
        #
        csv_path = glob.glob("{scnn_dir}/Data/plankton/*{tar_identifier}*".format(scnn_dir=scnn_directory, tar_identifier=tar_identifier))[0]
        csv_file = "{classification_dir}/{tar_identifier}-{date}.csv".format(classification_dir=classification_dir, tar_identifier=tar_identifier, date=date)
        shutil.move(csv_path, csv_file)

        # Clean directories to make space.
        #
        shutil.rmtree(image_dir)

        queue.put(gpu_id) # add the gpu id to the queue so that it can be allocated again

    sys.stdout = stdout # switch back to standard stdout
    
    print ('End: classify')


#----------------------------------------------------------------------------------------
# __main__
#
if __name__ == "__main__":
    # create a parser for command line arguments
    parser = argparse.ArgumentParser(description="Classification tool for managing the isiis_scnn processes")
    parser.add_argument("-s", "--scratch_base", type=directory, required=True, help="This is the path for fast ssd device storage where the segmentation data is already")
    parser.add_argument("-i", "--scnn_instances", type=int, default=2, required=True, help="Number of isiis_scnn instances to be run on a GPU")
    parser.add_argument("-d", "--scnn_directory", type=directory, required=True, help="Directory containing the isiis_scnn executable and the epochs directory")
    parser.add_argument("-e", "--epoch", type=int, required=True, help="Epoch weight file to be used for inference")

    # read in the arguments
    args = parser.parse_args()
    scratch_base = os.path.abspath(args.scratch_base)
    scnn_instances = args.scnn_instances
    scnn_directory = args.scnn_directory
    epoch = args.epoch
    chunksize = 1

    # segmentation_dir is where the input data is taken from
    segmentation_dir = scratch_base + "/segmentation"  
    classification_dir = scratch_base + "/classification"
    os.makedirs(classification_dir, 0o755,exist_ok=True)

    # make sure this is a valid directory
    if not os.path.exists(segmentation_dir):
        sys.exit("No directory segmentation")

    tars = [os.path.join(segmentation_dir, tar) for tar in os.listdir(segmentation_dir) if tar.endswith(".tar.gz")]
    if len(tars) == 0:
        sys.exit("Error: No tars file in segmenation directory")

    # setup gpu queue
    num_gpus = str(subprocess.check_output(["nvidia-smi", "-L"])).count('UUID') # read number of gpus from nvidia-smi output
    print("number of gpus", num_gpus)

    queue = Queue()
    for gpu_id in range(num_gpus):
        for _ in range(scnn_instances):
            queue.put(gpu_id)

    num_processes = scnn_instances * num_gpus
    print("scnn_instances", scnn_instances)
    print("processes", num_processes)

    # this is the parallel portion of the code
    p = Pool(num_processes)

    # most efficient multiprocessing method, order doesn't matter so why not
    # larger chunksize is supposed to be more efficient
    #
    # Start the Classification processes.
    #
    p.imap_unordered(classify, tars, chunksize=chunksize)

    p.close()
    p.join() # blocks so that we can wait for the processes to finish
    

