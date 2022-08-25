#########################################################
#  cgrb_train_scnn.sh
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
# This script will take a directory containing the isiis_scnn binary for 
# x86 or ppc64le architecture and perform training with the specified training
# data and the stopping epoch.

# Default values
stop_epoch=400
batch_size=40
validation_percent=0
initial_learning_rate=0.003
learning_rate_decay=0.01

usage() {
    echo "Usage: $0 [ -c SparseConvNet ] [ -t TRAINING_DATA_DIR ] [ -e EPOCH ] [ -b BATCH_SIZE ] [ -d DEVICE ] [ OPTIONAL ARGS ]" 1>&2
}

while getopts c:t:u:e:b:v:i:l:d: flag
do
    case "${flag}" in
        c  ) SparseConvNet=${OPTARG};;  # path to scnn directory
        t  ) training_data=${OPTARG};; # path to training data 
        u  ) testing_data=${OPTARG};; # unlabeled data for testing
        e  ) stop_epoch=${OPTARG};;
        b  ) batch_size=${OPTARG};;
        v  ) validation_percent=${OPTARG};; # percentage of validation data
        i  ) initial_learning_rate=${OPTARG};;
        l  ) learning_rate_decay=${OPTARG};;
        d  ) device=${OPTARG} ;; # cuda device
    esac
done

# validation of key arguments that are required
if [ ! -d "$SparseConvNet" ]  
then
    echo "Error: SparseConvNet directory $SparseConvNet does not exist."
    usage
    exit 1
else
    SparseConvNet=$(realpath $SparseConvNet)
fi

if [ ! -d "$training_data" ] 
then
    echo "Error: Training data directory $training_data does not exist."
    usage
    exit 1 
else
    training_data=$(realpath $training_data)
fi

if [ ! -d "$testing_data" ] 
then
    echo "Error: Testing data directory $testing_data does not exist."
    usage
    exit 1 
else
    testing_data=$(realpath $testing_data)
fi

re_isanum='^[0-9]+$'
if ! [[ "$device" =~ $re_isanum ]]
then
    echo "Error: Device needs to be a positve whole number coresponding to the CUDA device"
    usage
    exit 1
fi

# Training Configuration information
# validation_percent reserves a portion of the training set for monitoring 
# training. For best results, first run with a 20% validation set, and then 
# when happy with the other settings, re-train with no validation data.
# i.e. retrain with validation_percent = 0
# During each epoch, new learning rate is calculated by
# learning_rate = initial_learning_rate * exp(-learning_rate_decay * epoch)

# Check if the directories are valid

echo Sparse Directory: $SparseConvNet
echo Training Data: $training_data
echo Unlabeled Data: $testing_data
echo Stop Epoch: $stop_epoch
echo Batch Size: $batch_size
echo Validation Percentage: $validation_percent
echo Learning Rate: $initial_learning_rate
echo Learning Decay: $learning_rate_decay
echo Device: $device

Sparse_dir_name=$(basename "$SparseConvNet")
scratch=/data/$$ # fast ssd storage to move the training data to
mkdir $scratch

scratch_sparse=$scratch/$Sparse_dir_name

# copy the training isiis_scnn on to the scratch
rsync -a $SparseConvNet $scratch

# tar -xzf $scratch/train_data
rsync -ra $training_data/* $scratch/train_data
rsync -ra $testing_data/* $scratch/test_data

# remove old links
data=$scratch_sparse/Data/plankton
cd $data
rm -f train
rm -f test
rm -f classList

# set up symbolic links
# NOTE: Testing data is not necessary for training however, after all of the 
# classification epochs testing data will be tested and if it is not there,
# there will be a seg fault. Just point to one of the subdirectories of the
# train_data if there is a need to get around this.
ln -s $scratch/train_data train
ln -s $scratch/test_data test
bash classList.sh

classes1=$(ls -1 $data/train | wc -l)
classes2=$(wc -l $data/classList | cut -d ' ' -f1)

if [ "$classes1" -ne "$classes2" ]; then
    echo "Something went wrong, the classList file and number of classes in the training directory are not equal"
    echo "Check that none of the directories have spaces in their names"
    exit
fi

# NOTE: setup LD_LIBRARY_PATH to the libraries required for isiis_scnn

mkdir -p $scratch_sparse/weights/plankton
cd $scratch_sparse
# FIXME: isiis_scnn change based on name consensus
./isiis_scnn -start 0 -stop $stop_epoch -bs $batch_size -ilr $initial_learning_rate -lrd $learning_rate_decay -vsp $validation_percent -cD $device

# move the training output off the nodes scratch space
mv $SparseConvNet/weights $SparseConvNet/weights_backup_$$
mkdir -p $SparseConvNet/weights/plankton
mv -f $data/Data/plankton/test_plankton_predictions.csv $SparseConvNet/weights/plankton/ # move testing_data file, if there
rsync -a $scratch_sparse/weights/* $SparseConvNet/weights/
rm -rf $scratch 

