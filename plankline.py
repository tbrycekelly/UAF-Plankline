#########################################################
#  plankline.py
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
 

# ASCII Art Acknowledgements
# Asci art for start up of the pipeline FONT: ASNI Shadow patorjk.com
# Shrimp by Laura Brown http://asciiartist.com/shrimp-in-ascii/
# Jellyfish: https://ascii.co.uk/art/jellyfish
# Seahorse: https://asciiart.website/index.php?art=animals/other%20(water) 
# Ground and seaweed by Michael J. Penick: https://www.asciiart.eu/animals/fish
 

# BRIEF SCRIPT DESCRIPTION
# This script facilitates the processing of the rest of the pipeline by starting
# the necessary scripts with the prompted configurations. A config file can be supplied at start or it can be        # created on the fly via the prompts.

# NOTE: all of the python modules that are needed for all python scripts are 
# included here, even if not required in this script.
import os
import fnmatch
import shutil
import configparser
import argparse
import glob
import subprocess

# Terminal color escape sequences
color_error = "\033[31m"
color_success = "\033[32m"
color_reset = "\033[0m"
color_blue = "\033[34m"
color_turq = "\033[36m"

#########################
# checks if the var was inputed in the config file if it wasn't, user is prompted
# var is then added to the new config_out file 
# optional replace parameter that will replace something even if it is not set to None in the .ini file
#########################
def check_var(section, section_name, var_name, config, replace=False):
    var_value = section.get(var_name, None)
    if (replace): var_value = None # set the variable to None so that it is definitely replaced.

    # fix this so it is triggered on blank values
    while var_value == None or var_value == "": # var was not set in the config file 
        if var_value != None:
            print("%s can't be an empty string" % (var_name))
        var_value = input("Enter a value for %s: " % (var_name))

    config.set(section_name, var_name, var_value)

    return var_value

#------------------------------------------------------------------------------------------------
# File
#
# custom arg type for argparse
def file(arg):
    if (os.path.isfile(arg)):
        if (arg.endswith(".ini")):
            return arg
        else:
            raise argparse.ArgumentTypeERROR(color_error + "Not a valid .ini file" + color_reset)
    else:
        os.system("touch {f}".format(f=arg))
        print("Creating config file {f}".format(f=arg))

########################
# Verify that the current drive is setup properly
# Make the necessary directories
# Check the general path variables from the input file
########################
def drive_setup_check(DRIVE_BASE):
    #create the necessary directories
    os.makedirs(DRIVE_BASE+"/raw", 0o755,exist_ok=True)
    os.makedirs(DRIVE_BASE+"/segmentation", 0o775, exist_ok=True)
    os.makedirs(DRIVE_BASE+"/classification", 0o775, exist_ok=True)
    os.makedirs(DRIVE_BASE+"/measurements", 0o755, exist_ok=True)

    # iterate through the current directory and add any AVI files to the raw directory
    for avi_file in os.listdir(DRIVE_BASE):
        if os.path.isfile(os.path.join(DRIVE_BASE,avi_file)):
            if ".avi" in avi_file:
                shutil.move(avi_file, DRIVE_BASE +"/raw")


########################
# Check the destination directory for the pipeline scripts
########################
def check_scripts(directory, required_scripts):
    if (not os.path.isdir(directory)):
        return False
    for script in required_scripts:
        full_script_path = "{directory}/{script}".format(directory=directory, script=script)
        if (not os.path.isfile(full_script_path)):
            print(color_error + "ERROR: The PIPELINE_REPO variable that was passed in does not contain {script}, please double check the path.".format(script=script) + color_reset)
            return False
    return True

########################
# Verify the PIPELINE_REPO environment variable then copy scripts from it to the current directory
########################
def verify_copy(config_out, required_scripts):
    try:
        general = config_out['general']
    except:
        config_out.add_section('general')
        general = config_out['general']

    # get pipeline scripts directory
    PIPELINE_REPO = check_var(general, 'general', 'PIPELINE_REPO', config_out)
    while(not check_scripts(PIPELINE_REPO, required_scripts)):
        print("Make sure this is a valid path containing all of the pipeline scripts")
        PIPELINE_REPO = check_var(general, 'general', 'PIPELINE_REPO', config_out, replace=True) 

##########################
# check for all necessary variables to run segmentation
# writes out these variables to new ini file if the user inputs there own
##########################
def seg_var_check(config_out):
    print("Getting segmentation varibles")
    try: 
        segmentation = config_out['segmentation']
    except: 
        config_out.add_section('segmentation')
        segmentation = config_out['segmentation']

    SEGMENT_PROCESSES = check_var(segmentation, 'segmentation', 'SEGMENT_PROCESSES', config_out)
    while(not SEGMENT_PROCESSES.isnumeric()):
        print("SEGMENT_PROCESSES value needs to be a numeric i.e 12, for the best results, this should match the number of cores on the CPU")
        SEGMENT_PROCESSES = check_var(segmentation, 'segmentation', 'SEGMENT_PROCESSES', config_out, replace=True)

    SIGNAL_TO_NOISE = check_var(segmentation, 'segmentation', 'SIGNAL_TO_NOISE', config_out)
    while(not SIGNAL_TO_NOISE.isnumeric()):
        print("SIGNAL_TO_NOISE value needs to be a numeric i.e 15. 15 would represent the signal strength being 15 times stronger than the background noise")
        SIGNAL_TO_NOISE = check_var(segmentation, 'segmentation', 'SIGNAL_TO_NOISE', config_out, replace=True)

    SEGMENT_HOST_options = ['localhost', 'virgil', 'sheephead', 'xsede']
    SEGMENT_HOST = check_var(segmentation, 'segmentation', 'SEGMENT_HOST', config_out)
    while(SEGMENT_HOST not in SEGMENT_HOST_options):
        print("Type the name of a valid segmentation machine i.e.", SEGMENT_HOST_options)
        print("NOTE: localhost means that it will be done in place on the resources on the current machine, make sure that is actually what you want, make sure that is actually what you want.")
        SEGMENT_HOST = check_var(segmentation, 'segmentation', 'SEGMENT_HOST', config_out, replace=True)

##########################
# Checks all of the necessary variables to run for classification then will
# copy any changes to a config file to be used later.
# Will do different checks based on the infastructure that the pipeline is
# going to be run on.
##########################
def classification_var_check(config_out):
    print("Getting classification varibles")
    try:
        classification = config_out['classification']
    except:
        config_out.add_section('classification')
        classification = config_out['classification']

    # get the processing location
    CLASS_HOSTs = ['cgrb', 'xsede', 'localhost']
    CLASS_HOST = check_var(classification, 'classification', 'CLASS_HOST', config_out)
    acceptable = [location for location in CLASS_HOSTs] # write into array for printing
    while(CLASS_HOST not in CLASS_HOSTs):
        print("Enter a location from these options:", CLASS_HOSTs)
        CLASS_HOST = check_var(classification, 'classification', 'CLASS_HOST', config_out, replace=True) 

    
    if (CLASS_HOST == 'xsede'):
        gpu_supported = ['k80', 'p100']
        GPU_TYPE = check_var(classification, 'classification', 'GPU_TYPE', config_out)
        while(GPU_TYPE not in gpu_supported):
            print("GPU type can be one of these options:", gpu_supported)
            GPU_TYPE = check_var(classification, 'classification', 'GPU_TYPE', config_out, replace=True) 

        # the number of isiis_scnn instances is calculated based on the gpu type

    if (CLASS_HOST != 'xsede'):
        recommended_instances = ['1', '2', '3', '4'] 
        SCNN_INSTANCES = check_var(classification, 'classification', 'SCNN_INSTANCES', config_out)
        while(SCNN_INSTANCES not in recommended_instances):
            print("The number of proccesses needs to be one of these recommended amounts. 2 isiis_scnn instances is recomended on k80 and p100 GPUs", recommended_instances)
            SCNN_INSTANCES = check_var(classification, 'classification', 'SCNN_INSTANCES', config_out, replace=True) 

    epoch_supported = ['324', '400'] # choosing epoch 324 is recommended
    EPOCH = check_var(classification, 'classification', 'EPOCH', config_out)
    while(EPOCH not in epoch_supported):
        print("Select a weights file that will be used for classification, these are found in the SparseConvNet/weights directories and can be found during training")
        print("The supported classification epochs are:", epoch_supported)
        EPOCH = check_var(classification, 'classification', 'EPOCH', config_out, replace=True) 
        
#---------------------------------------------------------------------------------------------------
# Remote Check
#
def remote_check(config_out):
    print("Running on remote server, need to check for setup of ssh-keys.")
    try:
        remote = config_out['remote']
    except:
        config_out.add_section('remote')
        remote = config_out['remote']

    # Check to make sure the there is an ssh key for passwordless login between XSEDE and CGRB hosts
    REMOTE_USER = check_var(remote, 'remote', 'REMOTE_USER', config_out) 
    REMOTE_HOST = check_var(remote, 'remote', 'REMOTE_HOST', config_out) 
    REMOTE_PORT = check_var(remote, 'remote', 'REMOTE_PORT', config_out)
    while(1):
        cmd='ssh -p {port} -qo "BatchMode=yes" {remote_user}@{remote_host} exit'
        res = subprocess.call(cmd.format(remote_user=REMOTE_USER, remote_host=REMOTE_HOST, port=REMOTE_PORT), shell=True)
        if (res != 0): # if not a succes exit code
            print(color_error + "ERROR: Invalid user, host, port or no valid ssh-key." + color_reset)
            print("Double check that there is an ssh-key setup for the user {user} going to the host {host}. After one is created, then run this script again.".format(user=REMOTE_USER, host=REMOTE_HOST))

            reprompt = ''
            while(reprompt != 'y' and reprompt != 'n'): reprompt = input("Try different credentials? (y:n): ")
            if (reprompt == 'y'):
                REMOTE_USER = check_var(remote, 'remote', 'REMOTE_USER', config_out, replace=True)
                REMOTE_HOST = check_var(remote, 'remote', 'REMOTE_HOST', config_out, replace=True) 
                REMOTE_PORT = check_var(remote, 'remote', 'REMOTE_PORT', config_out, replace=True)
                continue

            if (reprompt == 'n'):
                print(color_error + "Exiting: Create a ssh-key for the XSEDE host {host} if necessary.".format(host=REMOTE_HOST) + color_reset)
                exit(2)
        else:
            print("Passwordless login is setup properly from the CGRB to XSEDE")
            break

    # check for ssh-key from XSEDE to CGRB-files
    FILES_USER = check_var(remote, 'remote', 'FILES_USER', config_out) 
    FILES_HOST = check_var(remote, 'remote', 'FILES_HOST', config_out) 
    FILES_PORT = check_var(remote, 'remote', 'FILES_PORT', config_out) 
    while(1):
        cmd='ssh -p {remote_port} -qo "BatchMode=yes" {remote_user}@{remote_host} ssh -p {files_port} -qo "BatchMode=yes" {files_user}@{files_host} exit'
        res = subprocess.call(cmd.format(remote_user=REMOTE_USER, remote_host=REMOTE_HOST, remote_port=REMOTE_PORT, files_user=FILES_USER, files_host=FILES_HOST, files_port=FILES_PORT), shell=True)
        if (res != 0):
            print(color_error + "ERROR: Invalid user, host, port or no valid ssh-key." + color_reset)
            print("Double check that there is an ssh-key for the host {dest_host} from the host {source_host}. If not, create one then run this again".format(dest_host=FILES_HOST, source_host=REMOTE_HOST))
            
            reprompt = ''
            while(reprompt != 'y' and reprompt != 'n'): reprompt = input("Try different credentials? (y:n): ")
            if (reprompt == 'y'):
                FILES_USER = check_var(remote, 'remote', 'FILES_USER', config_out, replace=True)
                FILES_HOST = check_var(remote, 'remote', 'FILES_HOST', config_out, replace=True) 
                FILES_PORT = check_var(remote, 'remote', 'FILES_PORT', config_out, replace=True) 
                continue
            if (reprompt == 'n'): 
                print(color_error + "Exiting." + color_reset)
                exit(2) # exit if the user does not want to be reprompted
        else:
            print("Passwordless login is setup properly from XSEDE to the CGRB files")
            break

    # check remote dir
    REMOTE_STORAGE = check_var(remote, 'remote', 'REMOTE_STORAGE', config_out) 
    while(1):
        cmd='ssh -p {remote_port} {remote_user}@{remote_host} "[ -w {directory} ] ; exit"'
        res = subprocess.call(cmd.format(remote_user=REMOTE_USER, remote_host=REMOTE_HOST, remote_port=REMOTE_PORT, directory=REMOTE_STORAGE), shell=True)
        if (res != 0):
            print("This path needs to be the location of permanent storage on the remote machine.")
            print(color_error + "ERROR: Either don't have write priveleges or that path is invalid" + color_reset)
            REMOTE_STORAGE = check_var(remote, 'remote', 'REMOTE_STORAGE', config_out, replace=True) 
            continue

        else:
            print("Valid remote storage path")
            break

#########################
# Verify that there is data in the raw directory
# If verification successful return the number of avi files in the drive else return 0
#########################
def verify_data(RAW_DIR):
    # EDITHERE: This is based on the video files used in our pipeline please change
    reasonable_avi_size = 512000 # this is 100 Mebibytes
    num_unreasonable = 0
    num_avis = 0 
    for f in os.listdir(RAW_DIR):
        if (not f.endswith(".avi")):
            print(color_error + "ERROR: Non-avi file in the directory {}".format(RAW_DIR) + color_reset)
            exit(3)
        else:
            num_avis += 1
        size = os.path.getsize(RAW_DIR + '/' + f) 

        if (int(size) < reasonable_avi_size):
            num_unreasonable += 1
    if (num_avis == 0):
        print(color_error + "ERROR: No avis are in the raw data directory, {}".format(RAW_DIR) + color_reset)
        exit(3)

    if (num_unreasonable > 0):
        okay = ""
        answers = {'y', 'Y', 'n', 'N'}
        while(okay not in answers):
            okay = input("There are %d out of %d raw avis have a size less than %d Mebibytes in the dir '%s'. Is this reasonable? (y:n): " % (num_unreasonable, num_avis, reasonable_avi_size, RAW_DIR))
        if (okay == 'n' or okay == 'N'):
            print(color_error + "Exiting: Double check the raw video files." + color_reset)
            exit(3)
    else:
        print("There are %d out of %d raw avis have a size less than %d Mebibytes" % (num_unreasonable, num_avis, reasonable_avi_size))

    return num_avis


#########################
# Verify that segmentation was done properly
# Check that the file numbers match those of the raw data
# Verify that the file sizes are all reasonable
#########################
def verify_seg(SEGMENT_DIR, num_avis=-1):
    tar_files = fnmatch.filter(os.listdir(SEGMENT_DIR), '*.tar.gz')
    error_files = fnmatch.filter(os.listdir(SEGMENT_DIR), '*_error.txt')
    num_tars = len(tar_files)
    num_errors = len(error_files)
    if (num_avis == -1):
        num_avis = num_tars # circumvent the file ammount testing

    # EDITHERE: size of the resulting files is an good indicator of segmentation running properly.
    reasonable_tar_size = 10000000 # not many tars are below this mark 
    num_unreasonable = 0

    # store which files are below the size and print them out
    unreasonable_tars = []
    for tar in tar_files:
        size = os.path.getsize(SEGMENT_DIR + '/' + tar)
        if (size < reasonable_tar_size):
            unreasonable_tars.append((tar, size))
            num_unreasonable += 1 

    # check the progress file to make sure segmentation is not currently running
    if (os.path.isfile(SEGMENT_IN_PROGRESS)):
        if (num_tars == 0):
            # segmentation may fail, may need to remove this manually.
            print(color_blue + "WARNING: This drive is currently being segmented" + color_reset)
            print("Manually remove the file '%s' if recieved this message in error." % (SEGMENT_IN_PROGRESS))
            exit(4)
        if ((num_tars + num_errors) != num_avis):
            print(color_error + "ERROR: Files missing segmentation needs to be redone." + color_reset)
            exit(4)

    if(num_tars == 0 and num_errors == 0): # no .tar.gz files, not segmented yet
        return 0, num_tars

    if (num_avis == (num_tars + num_errors)): # segmentation has already been done on this drive
        answers = {'y', 'Y', 'n', 'N'}
        okay = ""
        if (num_unreasonable > 0):
            print("Found %d/%d unreasably small tar files (<%d) that resulted from segmentation" % (num_unreasonable, num_tars, reasonable_tar_size))

            # print out names of all small tar files
            print("\ntar file, size in bytes")
            for tar, size in unreasonable_tars:
                print("%s, %d" % (tar, size))
            
            while okay not in answers:
                okay = input("Continue, anyway? (y:n)")
            if (okay == 'n' or okay == 'N'):
                print(color_error + "Exiting: Double check tar files, this may be indicative of a larger issue." + color_reset)
                exit(4)
        else: # if no unreasonably sized files move on
            print("Found %d/%d unreasably small tar files that resulted from segmentation" % (num_unreasonable, num_tars))

        # check for the error files
        if (num_errors != 0):
            print(color_blue + "WARNING: Corrupted video files were found" + color_reset)
            return 2, num_tars
        else:
            return 1, num_tars

##########################
# Check if classification ran successfully
# Look at the input and output directories 
##########################
def verify_classification(CLASSIFY_DIR, num_tars=-1):
    
    # after classification on xsede there may be some tar files in the classification directory
    classify_tars = fnmatch.filter(os.listdir(CLASSIFY_DIR), '*.tar.gz') # check for the tars from XSEDE
    if (len(classify_tars) != 0):
        print("Untaring files in classify directory")
        tars_backup = CLASSIFY_DIR+'/tars' 
        os.makedirs(tars_backup, exist_ok=True)
        command_string = ""
        for t in classify_tars:
            untar = "tar -xzf {classification_dir}/{tar} -C {classification_dir} --strip-components=5;"
            command_string = untar.format(classification_dir=CLASSIFY_DIR,tar=t) + command_string

        print("Untaring the classification files on sheephead")
        untar_cmd = "SGE_Batch -q sheephead -P 2 -c '{command} mv {classification_dir}/*.tar.gz {tar_dir}' -r tar_log" # untar and get rid of the directory structure
        os.system(untar_cmd.format(command=command_string, tar_dir=tars_backup, classification_dir=CLASSIFY_DIR))

    csvs = fnmatch.filter(os.listdir(CLASSIFY_DIR), '*.csv')
    num_csvs = len(csvs)
    if (num_tars == -1):
        num_tars = num_csvs

    # check if the drive is currently being classified
    if (os.path.isfile(CLASSIFY_IN_PROGRESS) and num_csvs != num_tars):
        # Classification may fail, in this case the in progress file will need to be removed
        print(color_blue + "WARNING: This drive is currently being classified" + color_reset)
        print("Manually remove the file '%s' if recieved this message in error." % (CLASSIFY_IN_PROGRESS))
        exit(5) 

    # check classification status
    if (num_csvs == 0):
        print("Classification has not been run yet")
        return 0, num_csvs # run classification
    if (num_csvs != num_tars): # num files don't match up
        print(color_error + "Classification unsuccessful, number of files from classification don't match to the number of files from segmentation." + color_reset)
        exit(5) 

    # checkout the stats of the csv files from classification
    unreasonable_csvs = []
    if (num_csvs == num_tars):
        remove = "rm -f {}"
        os.system(remove.format(CLASSIFY_IN_PROGRESS)) # remove the IN_PROGRESS file
    
        num_unreasonable = 0
        reasonable_csv_size = 1500000 # 1.4 Mebibytes , 1.5 Megabytes
        for csv in csvs: 
            size = os.path.getsize(CLASSIFY_DIR + '/' + csv)
            if (int(size) < reasonable_csv_size): # file sizes not large enough
                unreasonable_csvs.append((csv, size)) 
                num_unreasonable += 1
        if (num_unreasonable > 0): # there are some unreasonable csv files
            print("Found %d/%d unreasably small csv files (<%d) that resulted from classification" % (num_unreasonable, num_csvs, reasonable_csv_size))
            # print out the unreasonably small csv files
            print("\ncsv file, size in bytes")
            for csv, size in unreasonable_csvs:
                print("%s, %d" % (csv, size))

            print("If this is a signicant portion of the files it is recommended to check out the files further then re-run classification if something went wrong by moving the csv files that were created into a backup directory")

            # get user validation
            answers = {'y', 'Y', 'n', 'N'}
            okay = ""
            while okay not in answers:
                okay = input("Continue anyway? (y:n)")
            if (okay == 'n' or okay == 'N'):
                print(color_error + "Exiting: Double check csv files, this may be indicative of a larger issue." + color_reset)
                exit(5)
            return 1, num_csvs
        else: # no unreasonable csv files
            print("Found %d/%d unreasably small csv files that resulted from the classification" % (num_unreasonable, num_csvs))
            return 1, num_csvs

    return 1, num_csvs # segmented properly

##########################
# Copy the pipeline repository to the drive where the classification is happending on xsede 
###########################
def copy_xsede_repo(FILES_USER, FILES_HOST, FILES_PORT, REMOTE_USER, REMOTE_HOST, REMOTE_PORT, REMOTE_BASE, PIPELINE_REPO):
    # create directory if possible return error if not
    mkdir = "ssh -p {remote_port} {remote_user}@{remote_host} 'mkdir -p {base}'" 
    res = subprocess.call(mkdir.format(remote_user=REMOTE_USER, remote_host=REMOTE_HOST, base=REMOTE_BASE, remote_port=REMOTE_PORT), shell=True)
    if(res != 0):
        print(color_error + "ERROR: Could not create the directory, {base} is not valid.".format(base=REMOTE_BASE) + color_reset)
        exit(5)

    # copy the repo
    copy_repo = "ssh -p {remote_port} {remote_user}@{remote_host} 'rsync -avL -e \"ssh -p {files_port}\" {files_user}@{files_host}:{repo_dir}/* {remote_drive_base}/'" 
    os.system(copy_repo.format(files_user=FILES_USER, files_host=FILES_HOST, files_port=FILES_PORT, repo_dir=PIPELINE_REPO, remote_user=REMOTE_USER, remote_host=REMOTE_HOST, remote_drive_base=REMOTE_BASE, remote_port=REMOTE_PORT))

##########################
# Run segmentation on XSEDE comet
# copies all of the xsede script files over to the xsede scratch space
# Submits an sbatch to start processes
##########################
def xsede_segmentation(REMOTE_USER, REMOTE_HOST, REMOTE_BASE, DRIVE_BASE, SEGMENT_PROCESSES, SIGNAL_TO_NOISE):
    # copy the pipeline scripts from the github repository to the xsede user scratch
    copy_xsede_repo(FILES_USER, FILES_HOST, FILES_PORT, REMOTE_USER, REMOTE_HOST, REMOTE_PORT, REMOTE_BASE, PIPELINE_REPO)

    # run the sbatch script on xsede
    segment = 'ssh -p {remote_port} {remote_user}@{remote_host} "cd {xsede_base}; sbatch xsede_segmentation.sh -p {p} -s {snr} -c {cgrb_base} -x {xsede_base} -t {USER_HOST} -P {port}; squeue -u {remote_user}"' 
    os.system(segment.format(remote_user=REMOTE_USER, remote_host=REMOTE_HOST, remote_port=REMOTE_PORT, xsede_base=REMOTE_BASE, p=SEGMENT_PROCESSES, snr=SIGNAL_TO_NOISE, cgrb_base=DRIVE_BASE, USER_HOST=USER_HOST, port=FILES_PORT))

###########################
# Run segmentation on the cgrb infastructure
# Uses Sbatch submission system to allocate cores on a CPU machine
# This utilizes CPUs to run
###########################
def cgrb_segmentation(DRIVE_BASE, DRIVE_NAME, SEGMENT_HOST, SEGMENT_PROCESSES, CONFIG_FILE):
    # seg_environement needs to be called since the environment variables are not preserved when submitting a job with SGE_Batch
    seg_log_dir = "segmentation_{drive_name}_log".format(drive_name=DRIVE_NAME)
    segment = "cd {drive_base}; SGE_Batch -q {SEGMENT_HOST} -P {processes} -c 'bash {pipeline_repo}/cgrb_segmentation.sh -b {drive_base} -c {config}' -r {logs}"
    os.system(segment.format(SEGMENT_HOST=SEGMENT_HOST, processes=SEGMENT_PROCESSES, pipeline_repo=PIPELINE_REPO, drive_base=DRIVE_BASE, logs=seg_log_dir, config=CONFIG_FILE))

###########################
# Run segmentation on your local machine. This is done when on a workstation with a
# capable CPU and GPU.
# NOTE: Segmentation will be done in place, so make sure the video data is already in
# fast SSD storage (if possible)
###########################
def local_segmentation(DRIVE_BASE, DRIVE_NAME, CONFIG_FILE):
    # seg_environement needs to be called since the environment variables are not preserved when submitting a job with SGE_Batch
    log_file = "{drive_base}/segmentation_{drive_name}.log".format(drive_base=DRIVE_BASE, drive_name=DRIVE_NAME)
    segment = "nohup bash {pipeline_repo}/local_segmentation.sh -b {drive_base} -c {config} > {log_file} 2>&1 &"
    os.system(segment.format(drive_base=DRIVE_BASE, pipeline_repo=PIPELINE_REPO, config=CONFIG_FILE, log_file=log_file))

##########################
# checks if all of the neccessary variables have been set and derives additional variables
# Runs bash script on XSEDE that copies over segmented data
# Submits job for classification
##########################
def xsede_classification(REMOTE_USER, REMOTE_HOST, REMOTE_BASE, DRIVE_BASE, GPU_TYPE, EPOCH, SCNN_DIR): 
    input_dir = DRIVE_BASE + '/segmentation' # input data 
    output_dir = DRIVE_BASE + '/classification' # Check directory for output

    # copy the pipeline scripts from the github repository to the xsede user scratch
    copy_xsede_repo(FILES_USER, FILES_HOST, FILES_PORT, REMOTE_USER, REMOTE_HOST, REMOTE_PORT, REMOTE_BASE, PIPELINE_REPO) 
    # run the proccessing comand on the XSEDE infastructure
    submit_command="ssh -p {remote_port} {remote_user}@{remote_host} 'cd {xsede_base}; bash split_xsede_classification.sh -b {xsede_base} -g {gpu} -c {drive_base} -e {epoch} -P {port} -h {host} -d {scnn_dir}'"
    os.system(submit_command.format(remote_user=REMOTE_USER, remote_host=REMOTE_HOST, remote_port=REMOTE_PORT, xsede_base=REMOTE_BASE, drive_base=DRIVE_BASE, gpu=GPU_TYPE, epoch=EPOCH, host=USER_HOST, port=FILES_PORT, scnn_dir=SCNN_DIR))

###########################
# run classification on the cgrb infastructure for the current drive of images
# Check out the resources by USING SGE_Batch to allocate GPU resources
# NOTE: This assumes access to the ibm-power3 machine
###########################
def cgrb_classification(DRIVE_BASE, DRIVE_NAME, CONFIG_FILE):
    class_log_dir = "classification_{drive_name}_log".format(drive_name=DRIVE_NAME)
    cmd = "cd {drive_base}; SGE_Batch -q ibm-cgrb@ibm-power3 -c 'bash {pipeline_repo}/cgrb_classification.sh -b {drive_base} -c {config}' -r {logs}"
    os.system(cmd.format(drive_base=DRIVE_BASE, pipeline_repo=PIPELINE_REPO, config=CONFIG_FILE, logs=class_log_dir))

###########################
# Run classification on your local machine. This is done when on a workstation with a
# capable CPU and GPU
# NOTE: Classification will be done in place, so make sure the image data from 
# segmentation is already in fast SSD storage (if possible)
###########################
def local_classification(DRIVE_BASE, DRIVE_NAME, CONFIG_FILE):
    log_file = "{drive_base}/classification_{drive_name}.log".format(drive_base=DRIVE_BASE, drive_name=DRIVE_NAME)
    cmd = "nohup bash {pipeline_repo}/local_classification.sh -b {drive_base} -c {config} > {log_file} 2>&1 &"
    os.system(cmd.format(drive_base=DRIVE_BASE, pipeline_repo=PIPELINE_REPO, config=CONFIG_FILE, log_file=log_file))

#--------------------------------------------------------------------------------------------
# __main__
#    
if __name__ == '__main__':
    # parse the arguments
    parser = argparse.ArgumentParser(description="plankline manages the running of the entire pipeline by making sure data is in the correct places and all of the configurations are saved.")
    parser.add_argument("-c", "--config_file", type=file, required=False, help="Config file in .ini format, if none is provided then one will be created that can be use for future runs")
    parser.add_argument("-d", "--drive_base", type=str, required=True, help="Directory containing raw data to be run through the pipeline")

    args = parser.parse_args()
    config_file = os.path.abspath(args.config_file)
    DRIVE_BASE = os.path.abspath(args.drive_base)

    # Asci art for start up of the pipeline FONT: ASNI Shadow patorjk.com
    # Shrimp by Laura Brown http://asciiartist.com/shrimp-in-ascii/
    # Jelly Fish: https://ascii.co.uk/art/jellyfish
    # Seahorse: https://asciiart.website/index.php?art=animals/other%20(water) 
    # Ground and seaweed by Michael J. Penick: https://www.asciiart.eu/animals/fish
    print("                                .                                              ")
    print("          .-;':':'-.                             _.--------,..           ")
    print("         {'.'.'.'.'.}            `             ;:____________ `--,_      ")
    print("          )        '`.                        (_.-(o)-,-,-.. `''--,_     ")
    print("         '-. ._ ,_.-='    '                     ''-.__)_)_,'`\           ")
    print("           `). ( `);(             .    ,            /||//| )-;  '        ")
    print("           ('. .)(,'.)                              ||\ |/         .     ")
    print("            ) ( ,').(                               '' ' (/)             ")
    print("           ( .').'(').           _,-``.                           (             ")
    print("           .) (' ).('          .`..''(o\                        (\)                  ")
    print("            '  ) (  ).        :;_:,,,_.`._    '                  ))                 ")
    print("             .'( .)'           \--\--\ `.'       `            (\//   )                 ")
    print("               .).'            |--:'-|                       ) ))   ((                 ")
    print("                               |--\"-'|                     ((((   /)\`                 ")
    print("         '             '       ;-';--/           '           \\)) (( (                 ")
    print("              .               /--;_.'                        ((   ))))                 ")
    print("                              |_./  _                         )) ((//                 ")
    print("                               \\'\_',;                  .   ,-.  )/                 ")
    print("                  '             '.__.'           .           ,;'))((                 ")
    print("         .                                                     ((  ))                 ")
    print("                      .                             ,         (((\\'/                 ")
    print("                               _.-'`-._______                  \`))               ")
    print("     ___________--'`-.____.--'`.   `.   `.   `----._______.-'`-\((__            ")
    print("      ', ; ', ; ', ; ', ; ', ; ', ; ', ; ', ; ', ; ', ; ', ; ', ; ',`'--._  ")
    print("     .    `.   `.   `.   `.   `.   `.   `.   `.   `.   `.   `.   `.   `.  `.     ") 
    print("      ', ; ', ; ', ; ', ; ', ; ', ; ', ; ', ; ', ; ', ; ', ; ', ; ', ; ', ;,    ")
    print("     ██████╗ ██╗      █████╗ ███╗   ██╗██╗  ██╗██╗     ██╗███╗   ██╗███████╗   ")
    print("     ██╔══██╗██║     ██╔══██╗████╗  ██║██║ ██╔╝██║     ██║████╗  ██║██╔════╝   ")
    print("     ██████╔╝██║     ███████║██╔██╗ ██║█████╔╝ ██║     ██║██╔██╗ ██║█████╗     ")
    print(color_turq + "     ██╔═══╝ ██║     ██╔══██║██║╚██╗██║██╔═██╗ ██║     ██║██║╚██╗██║██╔══╝     ")
    print("     ██║     ███████╗██║  ██║██║ ╚████║██║  ██╗███████╗██║██║ ╚████║███████╗   ") 
    print("     ╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝╚═╝╚═╝  ╚═══╝╚══════╝   " + color_reset)
    print("     ")
    print("     ")

    ####################################################################################
    # Derived variables based on where this script is running
    ####################################################################################

    SEGMENT_DIR = DRIVE_BASE + '/segmentation'
    CLASSIFY_DIR = DRIVE_BASE + '/classification'
    MEASURE_DIR = DRIVE_BASE + '/classification'
    SEGMENT_IN_PROGRESS = SEGMENT_DIR + "/SEGMENT_IN_PROGRESS"
    CLASSIFY_IN_PROGRESS = CLASSIFY_DIR + "/CLASSIFY_IN_PROGRESS"
    RAW_DIR = DRIVE_BASE + '/raw'
    DRIVE_NAME = os.path.basename(DRIVE_BASE)
    
    #####################################################################################
    # Verify the variables from .ini file
    # If any don't exist prompt the user and get new ones
    #####################################################################################
    config = configparser.ConfigParser()
    
    # if no config file is passed in create one that can be used
    if (config_file == None):
        # create the new .ini file
        pid = str(os.getpid())
        config_file = "config_{pid}.ini".format(pid=pid)
        print(color_success + "Creating new .ini file named {ini}, this file will save all of the configurations made".format(ini=config_file) + color_reset)
        os.system("touch {config}".format(config=config_file))

    config.read(config_file) 

    # Copy the scripts from the repository
    required_scripts = ["measure_parallel.py", "segmentation.py", "cgrb_segmentation.sh", "classification.py", "cgrb_classification.sh", "local_segmentation.sh", "local_classification.sh"]
    verify_copy(config, required_scripts)
    with open(config_file, 'w') as output_config: config.write(output_config) # write out the changed variables to the new config file

    # Segmentation variables
    seg_var_check(config) # checks all of the segmentation variables and sets them in the new config file
    with open(config_file, 'w') as output_config: config.write(output_config) # write out the changed variables to the new config file

    segmentation = config['segmentation']
    SEGMENT_HOST = segmentation.get('SEGMENT_HOST')
    SEGMENT_PROCESSES = segmentation.get('SEGMENT_PROCESSES')
    SIGNAL_TO_NOISE = segmentation.get('SIGNAL_TO_NOISE')
    NO_RAW = segmentation.get('NO_RAW', 0) # put NO_RAW = 1 in the ini file to skip checking the raw avi files

    # Classification variables
    classification_var_check(config) # this will prompt the user until all necessary classification variables are found
    with open(config_file, 'w') as output_config: config.write(output_config) # write out the changed variables to the new config file

    classification = config['classification']
    CLASS_HOST = classification.get('CLASS_HOST')
    EPOCH = classification.get('EPOCH') # the number of the weights file that should be used
    SCNN_INSTANCES = classification.get('SCNN_INSTANCES', None)
    GPU_TYPE = classification.get('GPU_TYPE', None) 

    # General variables
    if (CLASS_HOST == 'xsede' or SEGMENT_HOST == 'xsede'):
        remote_check(config) # additional variables need to be setup
        with open(config_file, 'w') as output_config: config.write(output_config) # write out the changed variables to the new config file

        remote = config['remote']
        REMOTE_USER = remote.get('REMOTE_USER', None) 
        REMOTE_HOST = remote.get('REMOTE_HOST', None) 
        REMOTE_PORT = remote.get('REMOTE_PORT', None) 
        FILES_USER = remote.get('FILES_USER', None)
        FILES_HOST = remote.get('FILES_HOST', None)
        FILES_PORT = remote.get('FILES_PORT', None)
        REMOTE_STORAGE = remote.get('REMOTE_STORAGE', None)

        USER_HOST = "{user}@{host}".format(user=FILES_USER, host=FILES_HOST)
        # this is the mirror to the drive storage that is on the cgrb, it is used to store drive data between segmentation and classification
        if (REMOTE_STORAGE): 
            REMOTE_BASE = os.path.join(REMOTE_STORAGE, DRIVE_NAME) 

    general = config['general']
    PIPELINE_REPO = general.get('PIPELINE_REPO') # this is what is used to synce between locations
    SCNN_DIR = general.get('ISIIS_SCNN_DIR')

    ########################################################################################
    # This is where the pipeline starts the processing
    # This will make sure that all of the previous steps have completed before moving on
    ########################################################################################
    drive_setup_check(DRIVE_BASE) # creates the necessary directories if they don't already exist

    num_uploaded = None 
    if (NO_RAW == 0): # check for the no_raw flag
        num_uploaded = verify_data(RAW_DIR) # verify that there is raw data to segment
        print(color_success + "This drive has {num} avi files, moving to segmentation".format(num=num_uploaded) + color_reset)
    else: # NO_RAW = 1
        num_uploaded = -1 # this will circumvent the number of files check in verify_seg 

    # SEGMENTATION
    segmented, num_tars = verify_seg(SEGMENT_DIR, num_uploaded) # returns bool for weather or not this drive has been segmented

    if (segmented == 2): # if there are avi files that had errors
        print("There are video files that are corrupted, moving these to the directory raw_corrupt")
        RAW_CORRUPT = RAW_DIR + "_corrupt/" 
        os.makedirs(RAW_CORRUPT, exist_ok=True)
        for error_txt in [e for e in os.listdir(SEGMENT_DIR) if e.endswith("_error.txt")]:
            error_avi = glob.glob(RAW_DIR + "/" + error_txt[:-10] + "*")[0]
            shutil.move(error_avi, RAW_CORRUPT)
            error_txt_full_path = os.path.join(SEGMENT_DIR, error_txt)
            os.remove(error_txt_full_path)

        os.system("rm -f {}".format(SEGMENT_IN_PROGRESS)) # remove the IN_PROGRESS file

    if (segmented == 1): # data already segmented so this can be skipped
        print(color_success + "This drive has already been segmented moving on to classification" + color_reset)
        os.system("rm -f {}".format(SEGMENT_IN_PROGRESS)) # remove the IN_PROGRESS file

    if (segmented == 0): # hasn't been segmented yet 
        print("This drive has not been segmented, segmentation will begin shortly.")
        os.system("touch {}".format(SEGMENT_IN_PROGRESS)) # create the in progress file

        if (SEGMENT_HOST == 'sheephead' or SEGMENT_HOST == 'virgil'):
            print(color_success + "Segmenting now on {host}".format(host=SEGMENT_HOST) + color_reset)
            cgrb_segmentation(DRIVE_BASE, DRIVE_NAME, SEGMENT_HOST, SEGMENT_PROCESSES, config_file) # run segmentation by submitting a job to virgil
        if (SEGMENT_HOST == 'xsede'):
            print(color_success + "Segmenting now on XSEDE." + color_reset)
            xsede_segmentation(REMOTE_USER, REMOTE_HOST, REMOTE_BASE, DRIVE_BASE, SEGMENT_PROCESSES, SIGNAL_TO_NOISE)
        if (SEGMENT_HOST == 'localhost'):
            print(color_success + "Segmenting now locally." + color_reset)
            local_segmentation(DRIVE_BASE, DRIVE_NAME, config_file)

        # EDITHERE: To add another location to segment data add it here
    
        # verify that the drive has been segmented after running segmentation
        segmented, num_tars = verify_seg(SEGMENT_DIR, num_uploaded) # this should error since it is just submitting a job
        if(segmented == 1):
            print(color_success + "The drive was segmented properly, moving to classification" + color_reset)
        if(segmented == 0):
            print(color_error + "ERROR: The drive was not segmented properly, please double check segmentation data" + color_reset)
            exit(4)

    # CLASSIFICATION
    classified, _ = verify_classification(CLASSIFY_DIR, num_tars)
    if (classified == 1):
        print(color_success + "\nClassification has been completed on this drive. Exiting.." + color_reset) 
        exit(0) # exit normally since the drive must be done then
    if (classified == 0): # run classification
        os.system("touch {f}".format(f=CLASSIFY_IN_PROGRESS)) # create the in progress file

        if (CLASS_HOST == 'cgrb'):
            print(color_success + "Classifying now at the cgrb." + color_reset)
            cgrb_classification(DRIVE_BASE, DRIVE_NAME, config_file)
        if (CLASS_HOST == 'xsede'):
            print(color_success + "Classifying now on XSEDE." + color_reset)
            xsede_classification(REMOTE_USER, REMOTE_HOST, REMOTE_BASE, DRIVE_BASE, GPU_TYPE, EPOCH, SCNN_DIR) 
        if (CLASS_HOST == 'localhost'):
            print(color_success + "Classifying now on locally on the current machine" + color_reset)
            local_classification(DRIVE_BASE, DRIVE_NAME, config_file)

        # EDITHERE: To add another location to classify data add it here

    # verify classification was successful before removing the IN_PROGRESS file
    classified, _ = verify_classification(CLASSIFY_DIR, num_tars)
    exit(0)
