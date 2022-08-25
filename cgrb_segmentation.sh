#########################################################
#  cgrb_segmentation.sh
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
# This will setup the libraries needed to run segmentation on the
# CGRB HPC infrastructure.
# As mentioned in the segmentation.py script, this includes adding the
# paths to seg_ff, ffprobe and ffmpeg as well as including the necessary
# libraries for them to run.

while getopts b:c: flag
do
    case "${flag}" in
        b  ) drive_base=${OPTARG};; # full path to the drive containing the raw/ directory
        c  ) config=${OPTARG};;
    esac
done

# executable paths
python3=$(awk 'BEGIN{IGNORECASE = 1}/^PYTHON =/ {print $3}' $config)
ffmpeg=$(awk 'BEGIN{IGNORECASE = 1}/^FFMPEG =/ {print $3}' $config)
ffprobe=$(awk 'BEGIN{IGNORECASE = 1}/^FFPROBE =/ {print $3}' $config)
isiis_seg_ff=$(awk 'BEGIN{IGNORECASE = 1}/^ISIIS_SEG_FF =/ {print $3}' $config)
processes=$(awk 'BEGIN{IGNORECASE = 1}/^segment_processes =/ {print $3}' $config)
snr=$(awk 'BEGIN{IGNORECASE = 1}/^signal_to_noise =/ {print $3}' $config)
pipeline_repo=$(awk 'BEGIN{IGNORECASE = 1}/^PIPELINE_REPO =/ {print $3}' $config)

drive=$(basename $drive_base)
job_dir=/data/$$
scratch=$job_dir/$drive
mkdir -p $scratch

# Set up the environment variables.
# NOTE: Make sure that to include all of the libraries necessary for ffmpeg, ffprobe and seg_ff to run.
# Make sure the correct python executable is also included in the path.
PATH="$(dirname $ffmpeg):$(dirname $ffprobe):$(dirname $isiis_seg_ff):$PATH"

$python3 $pipeline_repo/segmentation.py -p $processes -c 1 -S $snr -l $drive_base -s $scratch

# transfer the data off of scratch after the processing has finished
rsync -az $scratch/segmentation $drive_base
rsync -az $scratch/measurements $drive_base

# clear out scratch
rm -rf $job_dir
