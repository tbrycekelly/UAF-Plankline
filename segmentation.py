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
import datetime

import subprocess
from multiprocessing import Pool
from measure_parallel import measure

import time

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
        
#--------------------------------------------------------------------------
# seg_ff
#
def seg_ff(avi, seg_output, SNR):
    print (datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), ': Start seg_ff')
    print ('\tavi -->' + avi + '<--')
    print ('\tseg_output -->' + seg_output + '<--')
    print ('\tSNR -->' + str(SNR) + '<--')
    
    seg = 'segment -i {avi_file} -n 1 -o {out} -s {signal_noise_ratio} '
    print ('\tseg.format -->' + seg.format(avi_file=avi, out=seg_output, signal_noise_ratio=str(SNR)) + '<--')

    os.system (seg.format(avi_file=avi, out=seg_output, signal_noise_ratio=str(SNR)))
    print (datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), ': End seg_ff')

#--------------------------------------------------------------------------
# make_tifs
#
def make_tifs(avi, tif_structure):
    print ('Start: make_tifs')
    print ('avi -->' + avi + '<--')
    print ('tif_structure -->' + tif_structure + '<--')
    sys.stdout.flush()

    # get video framerate
    FFREPORT = "ffreport.log"
    os.environ["FFREPORT"] = "file="+FFREPORT 
    ffprobe = "ffprobe -select_streams v -show_streams {video} | grep r_frame_rate | sed -e 's/r_frame_rate=//'"

    frame_rate = subprocess.check_output(ffprobe.format(video=avi), shell=True)
    if (not frame_rate): # if no frame rate returned video is not verified
        return False

    numer, denom = frame_rate[:-1].decode("utf-8").split('/') # remove new line, decode bystring and split on forward slash
    frame_rate = int(int(numer) / int(denom)) # change from fraction to int

    print ('frame_rate -->' + str(frame_rate) + '<--', flush=True)
    sys.stdout.flush()

    ffmpeg = "ffmpeg -i {video} {output}" 
    print (ffmpeg.format(video=avi, output=tif_structure))
    os.system(ffmpeg.format(video=avi, output=tif_structure))

    print ('End: make_tifs')
    sys.stdout.flush()

    return True

#--------------------------------------------------------------------------
# command_redo
#
def command_redo(cmd, err_message):
    print ('Start: command_redo')
    res = os.system(cmd)
    for i in range(4): # retry transfer multiple times to make sure data is transfered
        if(res == 0): # res == 0 means the last command was a success
            break;
        print(err_message)
        res = os.system(cmd)
    print ('End: command_repo')

#--------------------------------------------------------------------------
# local_main
#
# Pass in the avi file to be segmented, measured, and compressed.
# Necessary global variables: short_segment_scratch, SNR, fp_measure.
#
def local_main(avi):
    print (datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), ': Start local_main')
      
    # Global Data:
    # short_segment_scratch: this is the place on the root of the machine where the seg_ff happens
    # SNR: this is the Sound to Noise Ratio
    # measurements to 
    # remote_base

    # setup all of the local paths for the avi
    avi_file = os.path.basename(avi) # get only the file part of the full path
    avi_date_code = os.path.splitext(avi_file)[0] # remove .avi
    avi_segment_scratch = short_segment_scratch + "/" + avi_date_code
    seg_output = avi_segment_scratch + "_s"
    tif_structure = avi_segment_scratch + "/" + avi_date_code + "_%04d.tif"

    print ('avi_file:', avi_file)
    print ('avi_date_code:', avi_date_code)
    print ('avi_segment_scratch:', avi_segment_scratch)
    print ('seg_output:', seg_output)
    print ('tif_structure:', tif_structure)
    print ('short_segment_scratch:', short_segment_scratch)
    print ('scratch_base: ', scratch_base)

    # Deals with the segmentation fault that results from having a output dir that is too long.
    #max_segment_output = 37
    #if (len(short_segment_scratch) > max_segment_output):
    #    print("Exiting: Program will segmentation fault if the scratch path is too long.")  
    #    exit()

    # NOTE: since the raw avi files are so large we have opted to transfer them as they are needed
    if (lazy_transfer):
        if (remote_data):  # transfer the avi from cgrb
            transfer = "rsync -azv -e 'ssh -p {port}' {remote_login}:{avi} {scratch}/".format(port=port, remote_login=remote_login, avi=avi,scratch=raw_scratch)
            command_redo(transfer, "Trying to copy image over again")
        else:
            transfer = "rsync -azv {avi} {scratch}/".format(avi=avi, scratch=raw_scratch)
            command_redo(transfer, "Trying to copy image over again")

        avi = raw_scratch + "/" + avi_file # assign to original variable so the script can function properly

    # Printout to show progress.
    #
    sys.stdout.write(avi_file + "\n")
    sys.stdout.flush()

    # Create necessary directory structure.
    #
    os.makedirs(avi_segment_scratch, 0o777, exist_ok=True)
    os.makedirs(seg_output, 0o777, exist_ok=True)
    
    # Segmentation.
    #   Run the segmentation on the AVI file.
    #
    seg_ff(avi, seg_output, SNR)
          
    # Zip the segmentation output.
    # Create a new archive and use gzip to compress it.
    #
    print (datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), ': Start Tar')
    tar_name = avi_segment_scratch + ".tar"
    tar = "tar cf {tar} -C {dir_input} ." 
    print ('\ttar.format: ', tar.format(tar=tar_name, dir_input=seg_output))
    os.system(tar.format(tar=tar_name, dir_input=seg_output))
    print (datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), ': End Tar')

    shutil.rmtree(seg_output)          # remove datecode_s/
    shutil.rmtree(avi_segment_scratch) # remove datecode/

    if (lazy_transfer):
        os.remove(avi) # remove avi from the segment scratch

    print (datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), ': End local_main')

#------------------------------------------------------------------------------
# Fix Avi Names
#
def FixAviNames (avis):
  n = 0
  for Name in avis:
    FixedName = Name.replace(' ', '-')
    if not (FixedName == Name):
      os.rename (Name, FixedName)
      avis[n] = FixedName
    n += 1
    
  return avis

#------------------------------------------------------------------------------
# main
#
if __name__ == "__main__":
    print (datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), ': Start main')

    # create a parser for command line arguments
    parser = argparse.ArgumentParser(description="Segmentation tool for the plankton pipeline. Uses ffmpeg and seg_ff to segment a video into crops of plankton")
    parser.add_argument("-S", "--signal_to_noise", type=int, default=16, help="This is the Signal to Noise Ratio, often refered to as SNR")
    parser.add_argument("-c", "--chunksize", type=int, default=5, help="How many images tars are allocated to a process at a time, default is 6 for smaller ammounts of avis make this smaller")
    parser.add_argument("-p", "--num_processes", type=int, default=16, help="Number of processes you want to be running, this is how many files will be untared then found the measured concurrently. Adjust this based on the workload of the machine and the number of cores.")
    
    parser.add_argument("-l", "--lazy_transfer_dir", default=None, help="If option entered files will be transfer from this directory to scratch space as they are needed")

    # Add these if doing lazy transfer on remote host
    parser.add_argument("-r", "--remote_login", default=None, help="This is the complete user@host for the file transfering host for the remote infastructure")
    parser.add_argument("-P", "--port", type=int, default=22, help="The port for the transfer host")
    parser.add_argument("-s", "--scratch_base", type=directory, required=True, help="This is the path for your fast ssd device storage.")

    # read in the arguments
    args = parser.parse_args()
    scratch_base = os.path.abspath(args.scratch_base)
    SNR = args.signal_to_noise
    num_processes = args.num_processes
    chunksize = args.chunksize

    lazy_transfer_dir = args.lazy_transfer_dir
    remote_login = args.remote_login
    port = args.port

    # Argparse Checks that were not able to be implemented in existing argparse functionality
    remote_data = False
    lazy_transfer = False
    if lazy_transfer_dir != None:
        lazy_transfer_dir = os.path.abspath(lazy_transfer_dir)
        print("Video files for segmentation will be transfered when needed instead of all at once")
        print("If this is a remote directory add the remote_login and port so that it is able to be transfered")
        
        lazy_transfer = True

        if remote_login != None: 
            # NOTE: ssh key to the remote host will need to be setup
            cmd='ssh -p {remote_port} {remote_login} "[ -w {directory} ] ; exit"'
            res = subprocess.call(cmd.format(remote_login=remote_login, remote_port=port, directory=lazy_transfer_dir), shell=True)
            if (res != 0):
                print("Error: Make sure this directory is valid on the remote host and that ssh key is setup from this machine to the host that files are being transfered from")
                raise argparse.ArgumentTypeError("lazy_transfer_dir or remote host not valid")

            remote_data = True

        else:
            if (not os.path.isdir(lazy_transfer_dir)):
                raise argparse.ArgumentTypeError("lazy_transfer_dir not valid on local machine")

    # intro print outs
    print("Segmentation on:", scratch_base)
    print("Number of processes:", num_processes)
    print("Machine scratch", scratch_base)

    # setup the output segmentation and measurements dir
    raw_scratch = scratch_base + "/raw"
    measure_scratch = scratch_base + "/measurements"
    short_segment_scratch = scratch_base + "/s"
    segment_scratch = scratch_base + "/segmentation"
    os.makedirs(raw_scratch, 0o777,exist_ok=True)
    os.makedirs(measure_scratch, 0o777,exist_ok=True)
    os.makedirs(short_segment_scratch, 0o777,exist_ok=True)

    # Get the list of avi files if transfering lazily.
    #
    avis = []
    if lazy_transfer: 
        if remote_data: # need to create avi array from list of avis in txt file
            drive_file = os.path.join(scratch_base, "avi_list.txt")
            get_file_list = "ssh -p {port} {remote_login} 'ls {raw_dir}/*.avi' > {drive_file}"
            remote_raw = lazy_transfer_dir + "/raw"
            os.system(get_file_list.format(port=port, remote_login=remote_login, raw_dir=remote_raw, drive_file=drive_file))
            with open(drive_file, 'r') as d:
                avis = [f[:-2] for f in d]
            os.remove(drive_file)
        else:
            raw_dir = lazy_transfer_dir + "/raw"
            avis = [os.path.join(raw_dir, avi) for avi in os.listdir(raw_dir) if avi.endswith(".avi")]
    else:
        avis = [os.path.join(raw_scratch, avi) for avi in os.listdir(raw_scratch) if avi.endswith(".avi")]
        avis = FixAviNames (avis)
        
        if (len(avis) == 0):
            print("Error: no avi files found in machine_scratch/raw make sure avi files are there")
            exit()

    # Parallel portion of the code.
    #
    p = Pool(num_processes)

    # most efficient multiprocessing method, order doesn't matter so why not
    # larger chunksize is supposed to be more efficient
    #
    # local_main
    #
    p.imap_unordered(local_main, avis, chunksize=chunksize)

    p.close()
    p.join() # blocks so that we can wait for the processes to finish

    # move directory back to standard naming convention
    try:
        os.rename(short_segment_scratch, segment_scratch)
    except: 
        os.system("mv {src}/* {dst}; rm -rf {src}".format(src=short_segment_scratch, dst=segment_scratch))
    print (datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), ': End main')
    print("Finished Segmenting")
    
