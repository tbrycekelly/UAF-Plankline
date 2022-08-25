#########################################################
#  pull_images.py
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
# Tool that was created to help expand data for taxa of which we needed more images in the training library, and for puling images for test confusion matrices.
# This tool takes in command line options in order to find the images that were classified as being a
# certain taxon by looking through the outputed csv files from classification and then pulls these images
# from their corresponding tar file and puts them into folders based on the taxon that was being 
# searched for.

import os
import glob
import argparse
import csv # to parse all of the csv files 
import tarfile # untar the images
import re
import shutil # for copying files

# arg types
def directory(arg):
    if os.path.isdir(arg):
        return arg
    else:
        raise argparse.ArgumentTypeError("Not a valid directory path")

def csv_type(arg):
    if not os.path.isfile(arg):
        raise argparse.ArgumentTypeError("Not a file")
    if not arg.endswith(".csv"):
        raise argparse.ArgumentTypeError("Not a csv file")
    else:
         return arg
def float01(arg):
    if not float(arg):
        raise argparse.ArgumentTypeError("Not a floating point number")
    arg = float(arg)
    if not (arg < 1.0 and arg > 0.0):
        raise argparse.ArgumentTypeError("Not a floating point value between 0 and 1")
    else:
        return arg 

# check to make sure the image doesn't already exist. Some images in different tars are given the same name
def add_unique_postfix(fn): 
    if not os.path.exists(fn): # if the file name doesn't exist, don't change the name
        return fn

    path, name = os.path.split(fn)
    name, ext = os.path.splitext(name)

    make_fn = lambda i: os.path.join(path, '%s(%d)%s' % (name, i, ext))

    for i in range(2, 10000): # finds a number that is not used to put as the suffix
        uni_fn = make_fn(i)
        if not os.path.exists(uni_fn):
            return uni_fn

    return None
def get_parser(): # get command line options
    parser = argparse.ArgumentParser(description="Tool that was created to help expand the data for the taxon that we do not have many images of by utilizing the data from the images that were already classified.")
    # you should do many taxon at once since a lot of the time is lost unzipping files so it is only slightly less efficient
    parser.add_argument("-t", "--taxon", required=True, type=str, nargs='+', help="The taxons that you are looking to find from the csv files. This should be given as a list of taxon separated by a space.")
    
    selectgroup = parser.add_mutually_exclusive_group(required=True)
    selectgroup.add_argument("-p", "--probability_taxon", type=float01, help="The probability that a taxon needs to be over for the program to extract image extract the image, this should be a value between (0,1)")
    selectgroup.add_argument("-b", "--best_taxon", action="store_true", help="Extracts the images if the image was classified as a certain taxa, that is one of the taxons that you are trying to find.")
    
    inputgroup = parser.add_mutually_exclusive_group(required=True)
    inputgroup.add_argument("-d", "--input_drive", type=directory, help="The directory that you want to be pulling csv files from to look for images")
    inputgroup.add_argument("-c", "--input_csv", type=csv_type, help="The csv file that you want to look for taxon images.")
    
    parser.add_argument("-o", "--output", required=True, type=directory, help="The directory that you want to put the taxon folders of images")
    parser.add_argument("-r", "--raw_tars", required=True, type=directory, help="The directory of all of the tar images that correspond to the csv data")
    parser.add_argument("-m", "--min_images", type=int, default=0, help="The minimum number of images you need to have in a tar.gz in order to unzip it, this defaults to 0")

    parser.add_argument("-dc", "--different_columns", action="store_true", default=False, help="Checks all of the csvs and tar.gz files. This should be used if the csv files do not follow the same pattern.")
    parser.add_argument("-s", "--strict_subclasses", action="store_true", default=False, help="Doesn't find any substrings, only uses the taxon names that you input exactly")
    
    return parser

def validate_args(parser): # verify the command line options that the user plugged in and print them out
    args = parser.parse_args()
    tars_dir = args.raw_tars

    csvs = []
    file_dict = {}
    if(args.input_drive): # several csv files
        csvs = glob.glob(args.input_drive + "/*.csv")# do something here so that program goes through and gets all of the csv files
        if(len(csvs) == 0):
            parser.error("-d, --input_drive Directory does not contain any csv files")
        print("Input Drive: %s" % (args.input_drive))
        print("Number of Input CSVs: %d" % (len(csvs)))

        # create dictionary linking between tar files and csvs
        file_dict = {}
        for tar in os.listdir(tars_dir):
            unique_name = os.path.basename(tar).replace(".tar.gz","")
            matches = glob.glob(str(args.input_drive) + "/*" + str(unique_name) + "*.csv")
            if (len(matches) >= 1):
                csv_filename = matches[0]
                if (csv_filename not in file_dict):
                    file_dict[csv_filename] = os.path.join(tars_dir, tar)
                else:
                    print("Error: More than one tar file have been matched with a csv file.")
                    exit()

    else: # a single csv files 
        print("Input CSV:", args.input_csv)
        for tar in os.listdir(tars_dir):
            unique_name = os.path.basename(tar).replace(".tar.gz","")
            if (unique_name in os.path.basename(args.input_csv)): 

                if (args.input_csv not in file_dict):
                    file_dict[args.input_csv] = os.path.join(tars_dir, tar)
                else:
                    print("Error: More than one tar file have been matched with the given csv file.")
                    exit()

        csvs.append(args.input_csv)

    for csv_file in csvs:
        if (csv_file not in file_dict):
            print(file_dict)
            parser.error("r, --raw_tars does not have a corresponding tar for the csv file %s" % csv_file) 
 
    print("Raw tar Directory:", tars_dir)
    
    if(args.output):
        out_dir = args.output
        if(len(glob.glob(out_dir + "/*")) > 0):
            parser.error("-o, --output Directory can not contain any any files or directories so that we can avoid overwriting existing files.")
        print("Output Directory:", out_dir)
    
    min_images = args.min_images
    if(min_images < 0):
        parser.error("-m, --min_images The minimum numbers of images you extract needs to be a positive integer.")
    print("Minimum images needed to unzip:", min_images)
    
    if(args.best_taxon):
        print("\n----- Finding chosen taxon where they are the top probability -----")
    else:
        probability = args.probability_taxon
        print("\n----- Finding chosen taxon with probabilities above %s -----" % probability)

    return csvs, tars_dir, out_dir, file_dict, args.taxon, min_images, args.best_taxon, args.probability_taxon, args.different_columns, args.strict_subclasses

def find_all_taxon(csv, all_taxon, strict): # NOTE: this is assuming the csv's collumns are all the same. 
    taxon_locations = dict()  
    taxon_exist = set()
    for i, col in enumerate(next(_csv)): # loop through the columns to see which ones we need to look at. 
        for taxon in all_taxon:
            if strict:
                if col == taxon:
                    taxon_locations[i] = (taxon, col)
                    taxon_exists.add(taxon)
            else:
                if col.startswith(taxon): # see if the taxon col starts with one of your selected taxon.
                    taxon_locations[i] = (taxon, col) # add to an hashmap that can be used to loop through/index to the correct rows
                    taxon_exist.add(taxon)
    return taxon_locations, taxon_exist

            
def invalid_taxon(parser, taxon_exist, all_taxon): # see if any of the taxon were not substrings of the column names in the csv files. 
    args = parser.parse_args()
    numInvalid = 0 # store the number of invalid taxon
    for i, taxon in enumerate(all_taxon): 
        if(taxon not in taxon_exist):
            if(args.different_columns):  
                numInvalid += 1
                print("\"%s\" was ignored since it isn't a valid substring of a taxon name for this csv file" % (taxon))
            else:
                parser.error("-t, --taxon Taxon \"%s\" is not a valid substring of a taxon name" % (taxon))
    if numInvalid == len(all_taxon): # determine if there are any valid taxon that were inputted
        return True 
    return False 

# print out all of the taxon this program is searching for
def print_taxon(taxon_locations):
    print("Finding the sub_taxon:")
    for i, (taxon, sub_taxon) in enumerate(taxon_locations.values()):
        print("%d. %s" % (i, sub_taxon))

def find_top(csv, taxon_locations):
    matched_images = dict()
    for row in csv:
        top_col = 1
        for col, prob in enumerate(row):
            if col < 2: continue # skip the image name row
            # TODO maybe add quickselect here to get the top k elements
            if float(prob) > float(row[top_col]):
                 top_col = col
        if top_col in taxon_locations: # check if top_col is in the dictionary
            image = os.path.basename(row[0])
            matched_images[image] = [taxon_locations[top_col]] # add the image to the matched images dict 
    return matched_images

def find_above_prob(csv, taxon_locations, probability):    
    matched_images = dict()
    for row in csv:
        for i, (taxon, sub_taxon) in taxon_locations.items():
            if float(row[i]) > probability: # if one is found this tar.gz now needs to be unzipped
                image = os.path.basename(row[0])
                if image not in matched_images: matched_images[image] = [(taxon, sub_taxon)]
                else: matched_images[image].append((taxon, sub_taxon)) # add taxon to hashmap for the image
    return matched_images

def untar(tar, out_dir, matched_images):
    print("Unzipping %s into %s" % (tar, out_dir))
    t = tarfile.open(tar, 'r') # set up the file pointer for the tar file
    images = [img for img in matched_images] 
    images = set(images)
    memberImages = []
    for img in t.getmembers():
        img.name = os.path.basename(img.name)
        # print(img.name)
        if img.name in images:
            memberImages.append(img)

    t.extractall(out_dir, memberImages) # all images into the out_dir

def build_structure(path_array):
    for i, (taxon, sub_taxon) in enumerate(path_array): # shouldn't ever be that many, dependant on your minimum detection probability.
        dir_structure = "/" + taxon + "/" + sub_taxon + "/"
        if sub_taxon == taxon: dir_structure = "/" + taxon + "/"  # if subtaxon was selected make sure it doesn't have parent directory 
        os.makedirs(out_dir + dir_structure, exist_ok = True) # TODO: maybe move this to another place so that it is not done in a loop
        if(len(path_array) > 1): # then we will need to copy the image to multiple directories 
            if(i < len(path_array) - 1):
                shutil.copy2(img, out_dir + dir_structure)
            else: # move the last one instead of copying it
                shutil.move(img, out_dir + dir_structure) 
        else:  # move to one directory
            image_unique = add_unique_postfix(out_dir + dir_structure + os.path.basename(img)) # make sure there is a unique image name
            shutil.move(img, image_unique)

if __name__ == "__main__":

    parser = get_parser() # get command line arguments
    csvs, tars_dir, out_dir, file_dict, all_taxon, min_images, best, probability, different, strict = validate_args(parser) # error check arguments further
    print(file_dict)
    
    if not different: # if the csv files all follow the same pattern that you inputted
        f = open(csvs[0])
        _csv = csv.reader(f)
        taxon_locations, e_taxon = find_all_taxon(_csv, all_taxon, strict) # read the taxon from the first csv file
        f.close()

        invalid_taxon(parser, e_taxon, all_taxon) # gives errors if there are invalid taxon
        print_taxon(taxon_locations) # print out taxon that the program will collect images of 

    # this is the main processing part of the program
    for csv_file in csvs: # loop through all of the csv files
        print("\nFinding images from", csv_file)

        if different: # find taxon locations based on each individual csv file; based on command line option
            f = open(csv_file)
            _csv = csv.reader(f)
            taxon_locations, e_taxon = find_all_taxon(_csv, all_taxon, strict)
            f.close()
            skip = invalid_taxon(parser, e_taxon, all_taxon) # gives errors if there are invalid taxon
        
            if skip: # if there are no valid taxon found in the csv, skip to the next one
                print("No valid taxon of your given substrings were found, skipping to the next csv file")
                continue

            print_taxon(taxon_locations)

        matched_images = dict() 
        f = open(csv_file)
        _csv = csv.reader(f)
        name_line = next(_csv) # remove nameline
        if best: # if wanting to find your taxon in the top taxon for an image
            matched_images = find_top(_csv, taxon_locations)
        else:
            matched_images = find_above_prob(_csv, taxon_locations, probability)
    
        print("Found %d images in %s" % (len(matched_images), csv_file))
        if len(matched_images) > min_images: # if it is greater than the set minimum then you can unzip the directory.
            tar_file = file_dict[csv_file]
            untar(tar_file, out_dir, matched_images)
            
            print("Building file structure")
            for img in glob.glob(out_dir + '/*.jpg'): # loop through all the images in the untared directory
                path_array = matched_images[os.path.basename(img)]
                build_structure(path_array) # move all of the images to the correct sub-directory
        f.close()
    
    print("----- Done -----")
    
