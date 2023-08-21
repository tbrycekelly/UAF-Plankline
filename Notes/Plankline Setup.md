This is an _actively_ developed set of documentation for the setup and use of the UAF version of the planktline processing pipeline developed by OSU. Please contact Thomas Kelly <tbkelly@alaska.edu> for more information.

Updated 2023-08-11

## 1. Segmentation

On the first install, 

    cd /opt
    sudo git clone https://github.com/tbrycekelly/UAF-Segmentation
    sudo chown -R plankline:plankline /opt/UAF-Segmentation
    sudo chmod 776 -R /opt/UAF-Segmentation

To update the executable with a new version:

    cd /opt/UAF-Segmentation
    git clean -f
    git pull

To build the segmentation executable:

    cd /opt/UAF-Segmentation/build
    cmake ../
    make

Test it and copy it to final directory (if it works):

    ./segment
    cp ./segment ..


## 2. SCNN

For the first install,

    cd /opt
    sudo git clone https://github.com/tbrycekelly/UAF-SCNN.git
    sudo chown -R plankline:plankline /opt/UAF-SCNN
    sudo chmod 776 -R /opt/UAF-SCNN

To update from github,

    cd /opt/UAF-SCNN
    git clean -f
    git pull

May need to run `git config --global --add safe.directory /opt/UAF-SCNN` if permissions are not right.

To build SCNN:

    cd /opt/UAF-SCNN/build
    make clean
    make wp2

If there are undefined refences on the make, check that the LIBS line in ./build/Makefile is the output of `pkg-config opencv --cflags --libs` and inclues `-lcublas`.

Test it and copy it to final directory (if it works):

    ./wp2
    cp ./wp2 ../scnn

### 2.1 Training a Neural Network
Copy the training dataset into /opt/UAF-SCNN/Data/plankton/train so that images are in subfolders by category, e.g.: /opt/UAF-SCNN/Data/plankton/train/detritus/iamge.jpg

Run classList.sh

    cd /opt/UAF-SCNN/Data/plankton
    ./classList.sh

You may wish to change the minimum sample size required for a taxa to be included by modifying the _minN_ value within classList.sh. Taxa folders with fewer than _minN_ images will not be included in the training.

_TODO: Complete this section_




## 3. Plankline Scripts
This can be performed by any/every user on a system and can be placed in any folder. So far we have been placing this folder, /UAF-Plankline/ in Tom's documents folder. Typical locations that make sense include ~ (home directory), ~/Desktop, ~/Documents.

    cd ~
    git clone https://github.com/tbrycekelly/UAF-Plankline.git

To update an existing folder (will remove the config files present):

    cd ~/UAF-Plankline
    git clean -f
    git pull

To run plankline with a specific configuration file (required):

    python3 segmentation.py -c <ini> -d <dir>
    python3 classification.py -c <ini> -d <dir>

So for example:

    python3 segmentation.py -c osu_test_config.ini -d /media/plankline/data/test_data

The segmentation.py script will read in a project directory containing a _raw_ subfolder of AVIs and will create a _segmentation_ subfolder if not already existing. Each AVI will be processed, flatfielded, and cropped to a dedicated TAR file inside _segmentation_. If using the optional _compress = True_ flag then the file will be a TAR.GZ file. Simiarly the _classification.py_ script will read in a project directory and for every file in _segmentation_ produce a classification results file in a _classification_ subfolder. Both scripts will place a copy of the configuration file used into their respective subfolders for archival purposes.

These scripts require the segmentation executable and SCNN executable to be available (_see 1 and 2_).


