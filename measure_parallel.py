#########################################################
#  measure_parallel.py
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
# Get size estimates of plankton using the skiimage library. This program manipulates,
# the images so that the darker regions are connected and can be measured using the
# measure function of skiimage.
# 
# This program can be used standalone with the data from segmentation to e.g., redo
# measurements, and also has the measure function that can be imported to other programs,
# the way it is implemented in the pipeline.


import os
import cv2
import glob
from skimage import measure as measure_
import skimage.morphology as morph
from skimage import filters

from multiprocessing import Pool
import csv
import sys
import shutil
import argparse

import tarfile
import numpy as np


# custom arg type for argparse
def directory(arg):
    if os.path.isdir(arg):
        if arg.endswith("/"): 
            arg = arg[:-1]
        return arg
    else:
        raise argparse.ArgumentTypeError("Not a valid directory path")


# useful function
def get_particle_area(x) :
    """
    Fast way to get the area from an object of type RegionProperties
    Does not compute all the other properties.
    "Reverse engineered" from the code in scikit-image/skimage/measure/_regionprops.py
    x : object of type RegionProperties
    """

    return(np.sum(x._label_image[x._slice] == x.label))

# import this function in other programs to implement the measuring a different context
# file_pointer: this should be a file pointer created through os.open(), this is necessary
# so that we can make the atomic write calls
# images: this should be an array of full paths to images
def measure(file_pointer, images):
    threshold = 253 # pixel value 255 is white, 0 is black
    test = False # FIXME: this feature is not supported at the moment

    for f in images:
        # read image
        img = cv2.imread(f, cv2.IMREAD_GRAYSCALE)
        # img.shape
        
        # img modification
        imgopen = morph.opening(img, selem=morph.disk(3)) # closes gaps between pixels
        imger = morph.erosion(imgopen, selem=morph.disk(1.5))
        imgthr = imger < threshold
        
        f_base = os.path.basename(f) # get the file name without the path
        if ( test ):
            # check threshold
            cv2.imwrite(f_base,img)
            cv2.imwrite(f_base+'binary.jpg', imgthr * 255)
        
        # flag particles
        imglabelled = measure_.label(imgthr, connectivity=2)
        particles_properties = measure_.regionprops(label_image=imglabelled, intensity_image=img)
        n_part = len(particles_properties)
        
        # find the largest particle by aera
        max_area = 0
        main_particle_prop = None
        for x in particles_properties:
            area = get_particle_area(x)
            if area > max_area:
                max_area = area
                main_particle_prop = x

        # this means that the measurements were done on an image where no material was found.
        if main_particle_prop == None:
            max_area = major = minor = perim = orient = euler_num = 'NA'
            print("Blank Image:", f) # NOTE: some of the images actually appear to be blank...

            # move the images to a seperate directory
            # blank_dir = "blank_images/"
            # os.makedirs(blank_dir, exist_ok=True)
            # shutil.copy(f, blank_dir)
            
        else:
            # get other properties of this particle
            # http://scikit-image.org/docs/dev/api/skimage.measure.html#regionprops
            major = round(main_particle_prop['major_axis_length'], 2) # round to keep the csv file small
            minor = round(main_particle_prop['minor_axis_length'], 2)
            perim = round(main_particle_prop['perimeter'], 2)
            orient = round(main_particle_prop['orientation'], 2) # Angle between the X-axis and the major axis of the ellipse. Ranging from -pi/2 to pi/2 in counter-clockwise direction.
            euler_num = round(main_particle_prop['euler_number'], 2) # Euler characteristic of region. Computed as number of objects (= 1) subtracted by number of holes (8-connectivity).
            
        # write particle properties in a csv file
        row = f"{f_base},{max_area},{major},{minor},{perim},{orient},{euler_num}\n"
        row = str.encode(row) # change string into bytestring
        os.write(file_pointer, row) # atomic write

# this function takes one argument, the tar file that has images inside that the
# measurements need to be calculated for
# Necessary global variables: scratch_dir and fp
def measure_untar(tar):
    # global variables
    # fp: this is the output file pointer that is writen to by all of the processes
    # the writes to this file are done atomically. This needs to be a file pointer
    # created by os.open
    # scratch_dir: this is the temporary directory where the images are unzipped into
    # before the measurements are calculated

    # unzip the images into the directory
    sys.stdout.write(tar + "\n")
    sys.stdout.flush()

    # create output file for each tar date_code 
    date_code = os.path.basename(tar)[:-7] # remove .tar.gz

    output_file = scratch_measurements_folder + "/" + date_code + "_measurements.csv"
    fp = os.open(output_file, os.O_WRONLY|os.O_CREAT) # open file write only
    row = f"img,area,major,minor,perim,orientation,Euler_num\n"
    row = str.encode(row) # change string into bytestring
    os.write(fp, row) # atomic write


    # unzip all of the images in the folder then run the measurement script on them
    tar_scratch_dir = scratch_dir + "/" + date_code
    os.makedirs(tar_scratch_dir)

    cmd = "tar --no-overwrite-dir -xzf {tar_file} -C {output_dir} --strip-components=3 '*.jpg'"
    os.system(cmd.format(tar_file=tar, output_dir=tar_scratch_dir))
    
    images = [os.path.join(tar_scratch_dir,image) for image in os.listdir(tar_scratch_dir)]

    # call to measure with images and file-pointer
    measure(fp, images)

    shutil.rmtree(tar_scratch_dir)

    # final print out so that we can make sure it exited properly
    row = str.encode("End of Measurement\n") # change string into bytestring
    os.write(fp, row) # atomic write
    os.close(fp)

if __name__ == "__main__":

    # create a parser for command line arguments
    parser = argparse.ArgumentParser(description="Measurement tool for images inside of tar files")
    parser.add_argument("-d", "--drive_base", type=directory, default=".", help="Directory path of a drive, for example the drive 101A")
    parser.add_argument("-c", "--chunksize", type=int, default=1, help="How many images tars are allocated to a process at a time, default is 1 but for large ammounts of tars this should be higher")
    parser.add_argument("-p", "--num_processes", type=int, default=16, help="Number of processes to run, this is how many files will be untared then found the measured concurrently. Adjust this based on the workload of the machine.")
    parser.add_argument("-s", "--scratch", type=directory, help="Scratch directory where the files should be unzipped")

    # read in the arguments
    args = parser.parse_args()
    num_processes = args.num_processes
    chunksize = args.chunksize
    drive_base = args.drive_base

    drive_base = os.path.abspath(drive_base)
    drive_name = os.path.basename(drive_base)
    scratch_dir = args.scratch
    scratch_measurements_folder = os.path.join(scratch_dir, "measurements")

    print("Drive:", drive_name)
    print("Scratch", scratch_dir)
    print("Number of Processors:", num_processes)
    

    # setup the output segmentation and measurements folder
    os.makedirs(scratch_dir, 0o755,exist_ok=True)
    segment_folder = drive_base + "/segmentation"
    measurements_folder = drive_base + "/measurements"
    os.makedirs(segment_folder, 0o755,exist_ok=True)
    os.makedirs(measurements_folder, 0o755,exist_ok=True)
    os.makedirs(scratch_measurements_folder, 0o755,exist_ok=True)

    tars = [ os.path.join(segment_folder, f) for f in os.listdir(segment_folder) if f.endswith(".tar.gz") ]

    # set up multi-processing
    p = Pool(num_processes)

    # most efficient multiprocessing method, order doesn't matter so why not
    result = p.imap_unordered(measure_untar, tars, chunksize=chunksize)

    p.close() # pool can't be used for submissions anymore
    p.join() # blocks so that we can wait for the tasks to finish

    # move the contents of the temporary measurements folder
    copy = "rsync -auzr {scratch_measurements_folder}/* {measurements_folder}/"
    res = os.system(copy.format(scratch_measurements_folder=scratch_measurements_folder, measurements_folder=measurements_folder))
    for i in range(3):
        if (res == 0):
            break
        print("redoing rsync...")
        res = os.system(copy.format(scratch_measurements_folder=scratch_measurements_folder, measurements_folder=measurements_folder))

    shutil.rmtree(scratch_dir)
