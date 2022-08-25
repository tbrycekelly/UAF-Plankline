#########################################################
#  split_xsede_classification.sh
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
# This script splits up the quantity of images into partitions that can be
# submitted to different jobs simultaneously. Due to the 48 hour 
# processing limit on Xsede, this was required to assure classification of a
# drive of data would be able to complete in time

# Default values
port=22

while getopts c:l:g:e:b:d:h:P: flag
do
    case "${flag}" in
        c  ) cgrb_base=${OPTARG};; # full path to the drive at the cgrb /<path>/<to>/<dir>/<drive>
        g  ) gpuTarget=${OPTARG};; # GPU type
        e  ) classifyEpoch=${OPTARG};;
        b  ) XSEDE_BASE=${OPTARG};; # Where to put files after the segmentation process, under /oasis/scratch is recommended
        h  ) transfer_host=${OPTARG};; # Complete login information for the file transfer host. user@host
        P  ) port=${OPTARG};; # Login port for transfer_host
        d  ) scnn_dir=${OPTARG};; # Directory containing isiis_scnn binary
    esac
done

# setup needed directories
drive=$(basename $cgrb_base)
segmentation=$XSEDE_BASE/segmentation
mkdir -p $segmentation

# make sure the gpu type is either k80 or p100, set the apropriate cores and concurrent jobs for the configuration
tasks=24
scnn_instances=2
if [ $gpuTarget == 'k80' ]; then
    tasks=24 # this is for 6 * 4 = 24, 6 for the number of cores, and 4 for the number of GPU's in this case.
    scnn_instances=2 # two instances of isiis_scnn runing on a k80 gpu
elif [ $gpuTarget == 'p100' ]; then
    tasks=28 # this is for 7 * 4 = 28, 7 for the number of cores, and 4 for the number of GPU's in this case.
    scnn_instances=4 # four instances of isiis_scnn runing on a p100 gpu
else
    echo "The GPU $gpuTarget is not one of the options"
    exit
fi

gpuOptions="--gres=gpu:${gpuTarget}:4 --ntasks-per-node=${tasks}"

# the file path on oasis is slightly different
# "/oasis/scratch/comet/" needs to be replaced with "/oasis/scratch-comet/"
if [[ $segmentation == *"/oasis/scratch/comet/"* ]]
then
    sub=$(echo $segmentation | cut -c22-) # cut to the end of the string
    segmentation=/oasis/scratch-comet/$sub
fi

# Login using this once to add it to the list of known hosts
ssh $USER@oasis-dm-interactive.sdsc.edu "rsync -azv -e \"ssh -p $port\" $transfer_host:${cgrb_base}/segmentation/*.tar.gz ${segmentation}/"
if [ $? -eq 0 ]; then
    echo Transfer success
else
    echo "ERROR: Transfer failure, login to the host oasis-dm-interactive.sdsc.edu to add to the list of know hosts"
    exit
fi

# clear out all the files from previous runs so that this can run properly
cd $XSEDE_BASE

segSize=`du ${XSEDE_BASE}/segmentation | cut -f1` 

maxDriveSize=35000000 # around 37 Gibibytes in Kibibytes

if [ $segSize -gt $maxDriveSize ]; then # check if the file should be split
	numSplits=$(( $segSize / $maxDriveSize ))
	sp=$(( $numSplits + 1 ))
	echo "Spliting drive $drive into $sp groups of tars so that local scratch is not overfilled."
	
	mkdir -p $XSEDE_BASE/split # directory for all of the split tar.gzs
	for i in $(seq 0 $numSplits); do 
		touch $XSEDE_BASE/split/${i}.txt # the rsync of each of the jobs uses this to get the files to the right local scratch. 
	done	
	
	splitDir=0	
	ls --sort=size -1 $XSEDE_BASE/segmentation/*.tar.gz | while read file;
	do
		file=`basename $file`
		
		echo $file >> $XSEDE_BASE/split/${splitDir}.txt # writes out all of the tars to the right file	
		
		splitDir=$(( $splitDir + 1 )) 
		if [ $splitDir -gt $numSplits ]; then
			splitDir=0
		fi	
	done
else # if does not need to be split just right all of the tar.gz filenames to a file
	numSplits=0
	mkdir -p $XSEDE_BASE/split
	touch $XSEDE_BASE/split/0.txt
	ls --sort=size -1 $XSEDE_BASE/segmentation/*.tar.gz | while read file;
    do
        file=`basename $file`
        echo $file >> $XSEDE_BASE/split/0.txt # writes out all of the tars to the right file      
    done
fi


cd $XSEDE_BASE
for i in $(seq 0 $numSplits); do # loop through and start sbatch jobs for each split
	sbatch $gpuOptions $XSEDE_BASE/xsede_classification.sh -t $XSEDE_BASE/split/${i}.txt -c $cgrb_base -b $XSEDE_BASE -i $scnn_instances -e $classifyEpoch -s $i -h $transfer_host -P $port -d $scnn_dir
done
echo "Job(s) have been started"
squeue -u $USER
