#########################################################
#  local_classification.sh
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
# This will perform classification on a local machine. This is useful 
# for running the pipeline on a workstation where the data 
# is already on fast ssd storage

while getopts b:c: flag
do
    case "${flag}" in
        b  ) drive_base=${OPTARG};; # full path to the drive /<path>/<to>/<dir>/<drive>
        c  ) config=${OPTARG};;
    esac
done

# Read the config file.
#
python3=$(awk '/^python =/ {print $3}' $config)
instances=$(awk '/^scnn_instances =/ {print $3}' $config)
scnn_dir=$(awk '/^isiis_scnn_dir =/ {print $3}' $config)
epoch=$(awk '/^epoch =/ {print $3}' $config)
pipeline_repo=$(awk '/^pipeline_repo =/ {print $3}' $config)

scnn_scratch=$drive_base/$(basename $scnn_dir)

#--------------------------------------------------------
# echo $python3
# echo $instances
# echo $scnn_dir
# echo $epoch
# echo $pipeline_repo
# echo $scnn_scratch
#--------------------------------------------------------

# Copy isiis_scnn weights and data folder to local scratch.
#
rsync -a $scnn_dir/ $scnn_scratch 

# EDITHERE: setup LD_LIBRARY_PATH environment variable for isiis_scnn libraries
PATH=$scnn_dir:$PATH

# Perform classification.
#
$python3 $pipeline_repo/classification.py -s $drive_base -i $instances -d $scnn_dir -e $epoch

rm -rf $scnn_scratch


