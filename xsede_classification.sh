#!/bin/bash
#########################################################
#  xsede_classification.py
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
# This bash script will setup a job and submit it to XSEDE Comet to process.
# The script leverages python multiprocessing in order to parallelize the tasks on
# the GPUs and increase the efficiency of use of resources.
# This is done by transferring files to machine scratch, and making
# sure to set up any necessary environment variables.

# NOTE: The following lines starting with '#SBATCH' are NOT comments
#SBATCH --job-name="Classify"
#SBATCH -A osu119
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH -t 47:30:00
#SBATCH --wait=0
#SBATCH --export=ALL
#SBATCH --output="classification_%j.log"

while getopts t:l:c:b:i:e:h:P:s:d: flag
do
    case "${flag}" in
        t  ) tars_file=${OPTARG};; # File containing names of all tar files to classify
        c  ) cgrb_base=${OPTARG};; # CGRB path drive to transfer data back to 
        b  ) XSEDE_BASE=${OPTARG};; # XSEDE location to store segmentation files
        i  ) scnn_instances=${OPTARG};; # Instances to run on a GPU
        e  ) epoch=${OPTARG};; # Training Epoch
        h  ) transfer_host=${OPTARG};; # Complete login information for the file transfer host. user@host
        P  ) port=${OPTARG};; # Login port
        s  ) split=${OPTARG};; 
        d  ) scnn_dir=${OPTARG};; # isiis_scnn directory, containing executable and weights
        # \? ) echo "Unkown option: -$OPTARG" > &2; exit 1;;
    esac
done

echo Job ID: ${SLURM_JOB_ID} # same as %A
echo Concurrent JOBS: $scnn_instances
echo tars_file: $tars_file
echo Classification Epoch: $epoch
echo scnn directory: $scnn_dir

drive=$(basename $XSEDE_BASE)

# EDITHERE: This is the fast SSD storage for the node
scratch=/scratch/$USER/$SLURM_JOBID/$drive # Fast SSD storage for the allocated node

mkdir -p $scratch/classification $scratch/segmentation # for the output files

scnn_scratch=$scratch/$(basename $scnn_dir)
rsync -a -e "ssh -p $port" $transfer_host:$scnn_dir/ $scnn_scratch # copy scnn to local scratch 

# set modules for classification 
module purge
module load gnu
module load cmake
module load cuda/9.2
module load lapack
module load mkl
module load superlu

# EDITHERE: These are the required Library files
export PATH=$XSEDE_BASE:/oasis/projects/nsf/osu119/dapranod/miniconda3/bin:$PATH
export LD_LIBRARY_PATH=/home/manu1729/junk/lib/install/lib:/home/manu1729/software/opencv-3.4.7/install/lib64:/home/manu1729/junk/lib/install/lib64:/home/manu1729/junk/lib/install:$LD_LIBRARY_PATH

echo 'LD LIBRARY PATH: ' $LD_LIBRARY_PATH
echo 'Cuda device: ' $CUDA_VISIBLE_DEVICES

# copy the files in the tars file to the segmentation directory
rsync -az --files-from=$tars_file $XSEDE_BASE/segmentation/ $scratch/segmentation/

python3 $XSEDE_BASE/classification.py -s $scratch -i $scnn_instances -d $scnn_scratch -e $epoch

# move the file that has all of the info for the file download from the cgrb
mv *${SLURM_JOB_ID}*${split}.log $scratch/classification/
cp $usageFile $scratch/classification/

# function that tries to transfer the files a few times before failing
function rsync_redo {
    for i in 1 2 3
    do
        rsync -avuzr -e "ssh -p $1" $2 $3
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

# Rename and move the log file to be transfered back to CGRB
d=`date +%Y-%m-%d-%T`
mv classification_${SLURM_JOBID}.log $scratch/classification/classification_${drive}_${d}.log

# rsync the new files to CGRB
rsync_redo $port $scratch/classification/ $transfer_host:${cgrb_base}/classification
