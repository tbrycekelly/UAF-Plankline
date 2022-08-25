#!/bin/bash
#########################################################
#  xsede_segmentation.sh
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
# This script allocates the CPU time on XSEDE Comet. 
# As mentioned in the segmentation.py script, this script needs to 
# include paths to seg_ff, ffprobe and ffmpeg as well as including 
# the necessary libraries for them to run.

# NOTE: The following lines starting with '#SBATCH' are NOT comments
# 24 cores per node

#SBATCH --job-name="Segment"
#SBATCH -A osu119
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=24 
#SBATCH --export=ALL
#SBATCH --time=47:30:00 
#SBATCH --output="segment_%j.log"

# function to facilitate the transfering of files to cgrb
function rsync_redo {
    for i in 1 2 3
    do
        rsync -avuzr -e "ssh -p $port" $1 $2
        if [ $? -eq 0 ]; then
            echo Transfer success
            break
        else
            echo "ERROR: Transfer failure, trying to transfer again"
            if [ $i -eq 3 ]; then
                echo "ERROR: Transfer failed 3 times, not trying again"
            fi
        fi
    done
}


while getopts p:s:c:x:t:P: flag
do
    case "${flag}" in
        p  ) processes=${OPTARG};; # Number of instances to run
        c  ) cgrb_base=${OPTARG};; # Full path to the drive at the cgrb where data is synced to and from
        s  ) SNR=${OPTARG};; # Signal to Noise Ratio
        x  ) XSEDE_BASE=${OPTARG};; # Where to store the segmentation files after segmentation, this should be where large ammounts of data can be stored
        t  ) transfer_host=${OPTARG};; # The complete login information for the file transfer host. user@host
        P  ) port=${OPTARG};; # Transfer host port
        # \? ) echo "Unkown option: -$OPTARG" > &2; exit 1;;
    esac
done

echo Processes: $processes
echo CGRB DRIVE Base:$cgrb_base
echo Signal to Noise Ratio: $SNR
echo XSEDE Base Directory: $XSEDE_BASE
echo Transfer Host: $transfer_host
echo Process ID: $$
echo Job ID: $SLURM_JOBID

# EDITHERE: This is the fast SSD storage for the node
drive=$(basename $cgrb_base)
scratch=/scratch/$USER/$SLURM_JOBID/$drive
mkdir -p $scratch

# Set up the environment variables.
# EDITHERE: Make sure that to include all of the libraries necessary for ffmpeg, ffprobe and seg_ff to run.
# NOTE: XSEDE_BASE contains ffmpeg and ffprobe, also include the right python3 with all the necessary modules as well.
export PATH=$XSEDE_BASE:/oasis/projects/nsf/osu119/dapranod/miniconda3/bin:$PATH
export LD_LIBRARY_PATH=/oasis/projects/nsf/osu119/dapranod/lib:/oasis/projects/nsf/osu119/dapranod/lib64:$LD_LIBRARY_PATH

# run segmentation on the cpus
python3 $XSEDE_BASE/segmentation.py -p $processes -c 1 -S $SNR -s $scratch -l $cgrb_base -r $transfer_host -P $port 

# Rename and move the log file to be transfered back to CGRB
d=`date +%Y-%m-%d-%T`
mv segment_${SLURM_JOBID}.log $scratch/segmentation/segment_${drive}_${d}.log

# transfer data to be stored
rsync -az $scratch/segmentation $XSEDE_BASE
rsync -az $scratch/measurements $XSEDE_BASE

# rsync the segmented files and measurements to CGRB
rsync_redo $scratch/segmentation ${transfer_host}:${cgrb_base}
rsync_redo $scratch/measurements ${transfer_host}:${cgrb_base}
