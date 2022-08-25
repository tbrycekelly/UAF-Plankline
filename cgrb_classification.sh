#########################################################
#  cgrb_classification.sh
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
# Facilitates the classification on CGRB
# This is done by transferring files to machine scratch, and making
# sure to set up any necessary environment variables.

while getopts b:c: flag
do
    case "${flag}" in
        b  ) drive_base=${OPTARG};; # full path to the drive /<path>/<to>/<dir>/<drive>
        c  ) config=${OPTARG};;
        # \? ) echo "Unkown option: -$OPTARG" > &2; exit 1;;
    esac
done

function rsync_redo {
    for i in 1 2 3
    do
        rsync -avuzr $1 $2
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

# Get arguments from the config file
python3=$(awk 'BEGIN{IGNORECASE = 1}/^PYTHON =/ {print $3}' $config)
instances=$(awk 'BEGIN{IGNORECASE = 1}/^SCNN_INSTANCES =/ {print $3}' $config)
scnn_dir=$(awk 'BEGIN{IGNORECASE = 1}/^ISIIS_SCNN_DIR =/ {print $3}' $config)
epoch=$(awk 'BEGIN{IGNORECASE = 1}/^EPOCH =/ {print $3}' $config)
pipeline_repo=$(awk 'BEGIN{IGNORECASE = 1}/^PIPELINE_REPO =/ {print $3}' $config)

drive=$(basename $drive_base)
scratch=/data/${drive}$$ # NOTE: this the fast machine storage, transfer the data here before interacting with it.
segmentation_scratch=$scratch/segmentation
classification_scratch=$scratch/classification
mkdir -p $segmentation_scratch $classification_scratch

scnn_scratch=$scratch/$(basename $scnn_dir)
rsync -a $scnn_dir/ $scnn_scratch # copy executable and the weights to local scratch 
rsync -a $drive_base/segmentation/* $scratch/segmentation/

# EDITHERE: setup LD_LIBRARY_PATH environment variable for isiis_scnn libraries
PATH=$scnn_dir:$PATH

$python3 $pipeline_repo/classification.py -s $scratch -i $instances -d $scnn_scratch -e $epoch

rsync_redo $classification_scratch/ $drive_base/classification

# clean up the classification and segmentation folders on the scratch space
rm -rf $scratch
