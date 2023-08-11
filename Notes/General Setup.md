This is an _actively_ developed set of documentation for the setup and use of the UAF version of the planktline processing pipeline developed by OSU. Please contact Thomas Kelly <tbkelly@alaska.edu> for more information.

Updated 2023-08-11



# Software Setup
## Recommended Installs
These are common utilities and/or prerequisites for one or more of the steps recommended by this setup document.

    sudo apt-get install r-base net-tools cifs-utils ethtool apt-get libopencv-dev libgdal-dev
    sudo apt-get install nvidia-cuda-toolkit timeshift nvtop samba samba-client

__Python Related:__ We are using python3 throughout the plankline processing scripts, and need to install some additional pacakges/libraries for image processing.

    sudo apt-get install python3 python3-devpython3-pip python3-skimage python3-opencv
    pip3 install gpustat

__Misc:__

    sudo apt-get install perl libnet-ssleay-perl openssl libauthen-pam-perl libpam-runtime libio-pty-perl apt-show-versions unzip 
    sudo apt-get install baobab ncdu htop mc bpytop
    sudo apt-get install libreoffice openssh-server

__NVIDIA Requirements for GPGPUs:__ With these commands we first install the app key used to authenticate the nvidia package that we download using wget. The following commands then install the pacakge _cuda keyring_, which allows us to download and install nvidia drivers directly. Finally we install the development tools needed to compile CUDA applications ourselves.

    sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/3bf863cc.pub &&
    wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.0-1_all.deb

    sudo dpkg -i cuda-keyring_1.0-1_all.deb
    sudo apt-get update
    sudo apt-get install libsparsehash-dev cuda-nvcc-11-8 libcublas-11-8 libcublas-dev-11-8


## Setup Plankline
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

These scripts require the segmentation executable and SCNN executable to be available (see below).    

## Setup SCNN

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

### Training a Neural Network
Copy the training dataset into /opt/UAF-SCNN/Data/plankton/train so that images are in subfolders by category, e.g.: /opt/UAF-SCNN/Data/plankton/train/detritus/iamge.jpg

Run classList.sh

    cd /opt/UAF-SCNN/Data/plankton
    ./classList.sh

You may wish to change the minimum sample size required for a taxa to be included by modifying the _minN_ value within classList.sh. Taxa folders with fewer than _minN_ images will not be included in the training.

_TODO: Complete this section_


## Setup Segmentation

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



## Optional Software
### Install RStudio Server

Rstudio Server is a useful tool for running R processing scripts directly on the plankline computers using your local computer's browser. 

    sudo apt-get install gdebi-core;
    wget https://download2.rstudio.org/server/jammy/amd64/rstudio-server-2022.07.1-554-amd64.deb;
    sudo gdebi rstudio-server-2022.07.1-554-amd64.deb;
    sudo nano /etc/rstudio/rserver.conf;

Add "www-port=80", then restart the service:

    sudo systemctrl restart rstudio-server

The Rstudio Server should now be available at http://<computer name>/. For example, http://plankline-2/. Please see the section below about setting the computer name is it has not already been set.


__To install the plankline processing scripts:__ Note, that the default "home" directory for rstudio will be the home directory of the user that you are log in as.

    cd ~
    git clone https://github.com/tbrycekelly/Plankline-Processing-Scripts.git

From an Rstudio Server instance (i.e. in the browser), open the Plnkline-Processing-Scripts project, and nvigate to the Workflows subdirectory. This is the folder that contains all the basic workflow scripts for processing and analyzing the plankline image and sensor data. Run the _one time setup_ script to install and verify functionality. This only needs to be done once per install, but it is an easy cehck that everything is working as it should.

### Install Netdata

Netdata is a useful system monitor that is accessible over the network (e.g. http://<computer name>:19999/). It gives detailed statistics about a wide variety of computer resources (except for the GPUs).

    wget -O /tmp/netdata-kickstart.sh https://my-netdata.io/kickstart.sh && sh /tmp/netdata-kickstart.sh

Point a broswer at http://<computer name>:19999/ to verify install.

# Hardware Setup
## Video Cards
### Nvidia Drivers for **Tesla** cards:

    sudo apt-get install libnvidia-compute-470 nvidia-utils-470 nvidia-driver-470-server
    sudo ldconfig


### Nvidia Drivers for **GTX** cards:
    
    sudo apt-get install libnvidia-compute-515 nvidia-utils-515 nvidia-driver-515
    sudo ldconfig


### Monitoring NVIDIA processes

    nvtop

## Compile and Install OpenCV 3.4

    sudo apt-get install build-essential cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev python3-dev python3-numpy libtbb2 libtbb-dev

    sudo apt-get install libjpeg-dev libpng-dev libtiff5-dev jasper libdc1394-dev libeigen3-dev libtheora-dev libvorbis-dev libxvidcore-dev libx264-dev sphinx-common libtbb-dev yasm libfaac-dev libopencore-amrnb-dev libopencore-amrwb-dev libopenexr-dev libgstreamer-plugins-base1.0-dev libavutil-dev libavfilter-dev libtesseract-dev libopenblas-dev libopenblas64-dev ccache
  
    cd /opt
  
    git clone --branch 3.4 --single-branch https://github.com/opencv/opencv.git
    git clone --branch 3.4 --single-branch https://github.com/opencv/opencv_contrib.git
  
    cd opencv
    mkdir release
    cd release
  
    cmake -D BUILD_TIFF=ON -D WITH_CUDA=OFF -D WITH_OPENGL=OFF -D WITH_OPENCL=OFF -D WITH_IPP=OFF -D WITH_TBB=ON -D BUILD_TBB=ON -D WITH_EIGEN=OFF -D WITH_V4L=OFF -D WITH_VTK=OFF -D BUILD_TESTS=OFF -D BUILD_PERF_TESTS=OFF -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D OPENCV_EXTRA_MODULES_PATH=/opt/opencv_contrib/modules /opt/opencv/

    make -j
    sudo make install
  
    sudo ldconfig
    pkg-config --modversion opencv

## 10G Fiber
### Install intel 10G driver ==

Download from Intel X520 IXGBE driver from a trusted source. _TODO: include a copy of the driver on a shared networked location._

    tar xzf ./ixgbe-5.16.5.tar.gz
    cd ./ixgbe-5.16.5/src/
    sudo make install
    sudo nano /etc/default/grub

Add "ixgbe.allow_unsupported_sfp=1" to GRUB_CMDLINE_LINUX="" line

    sudo grub-mkconfig -o /boot/grub/grub.cfg
    sudo rmmod ixgbe && sudo modprobe ixgbe allow_unsupported_dfp=1
    sudo update-initramfs -u

Check to see if network interface is present, e.g. eno1

    ip a

Additional network inspection can be performed by ethtool:

    ethtool <interface>
    ethtool eno1

## Morphocluster
Generally just follow the outline provided here: [https://github.com/morphocluster/morphocluster]

    sudo apt-get install docker docker-compose npm dos2unix
    mkdir -p /media/plankline/Data/morphocluster/postgres
    mkdir -p /media/plankline/Data/morphocluster/data

Copy morphoclsuter directory

    sudo nano /etc/environment

Add lines: 
    COMPOSE_DOCKER_CLI_BUILD=1
    DOCKER_BUILDKIT=1

Save. Ctrl + x  y

    sudo docker-compose up --build


# System Setep
## Setup Automounting ==

On Ubuntu, automounting is configured by the fstab file and is automatically run during system startup. 

    lsblk
    sudo nano /etc/fstab

"/dev/sdX	/media/plankline/Data	ext4	defaults,rw,user	0	0"

    mkdir -p /media/plankline/data
    sudo chmod -R 777 /media/plankline
    sudo mount -a

## Scratch Filesystem
To setup a very fast scratch drive, add the following mount configuration to `/etc/fstab`

    tmpfs /tmp tmpfs defaults,noatime,nosuid,nodev,mode=777,size=60G 0 0


## Setup NFS (Linux and Windows networking shares) _work in progress_

_On a windows computer, you need to install the NFS support as an optional windows add-on. In the start menu > Turn Windows Features On and Off > NFS Support. Install NFS client. 

    sudo apt install nfs-kernel-server
    sudo systemctl start nfs-kernel-server.service

    nano /etc/exports

Add the following lines:

    /media/plankline/ingest    *(rw,sync,subtree_check)



## Setup Samba (Windows SMB)

    sudo apt-get install samba
    sudo nano /etc/samba/smb.conf


Inside the smb.conf file, go to the bottom of the file and add the following (or something similar). This will setup a share named _ingest_ which will be writable by everyone (no security) on the network.

    [ingest]
        comment = Plankline data drive.
        path = /media/plankline/ingest
        browsable = yes
        guest ok = yes
        read only = no
        create mask = 0777

Can do the same for an output directory share.

    [output]
        comment = Plankline output drive.
        path = /media/plankline/data
        browsable = yes
        guest ok = yes
        read only = no
        create mask = 0777


Create the directory given above:

    sudo mkdir -p /media/plankline/ingest
    sudo chown nobody:nogroup /media/plankline/ingest

Restart samba to apply the edits.

    sudo systemctl restart smbd.service

The folder /media/plankline/ingest should now be available as \\plankline-X\ingest from any file manager or as http://plankline-x/ingest from the browser.


## Setup Firewall
To check the status of the firewall:

    sudo ufw status

To allow connections on particular ports (e.g. 80 for *Shiny* and 19999 for *netdata*):

    sudo ufw allow 8000:8100/tcp
    sudo ufw allow 19999	
    sudo ufw allow 9993
    sudo ufw allow http
    sudo ufw limit ssh
    sudo ufw allow "CUPS"
    sudo ufw allow "Samba"
    sudo ufw allow 4000/tcp
    sudo ufw allow 4080
    sudo ufw allow 4443
    sudo ufw allow 4011:4999/udp

To turn off the firewall:

    sudo ufw disable

To View Rules and Delete them:

    sudo ufw status numbered
    sudo ufw delete XX


## Misc Linux Tasks
### Set password == 

    sudo passwd plankline

### Set hostname ==

This is how you set the computer name. Our current convention is to use lowercase plankline followed by a number: e.g. __plankline-7__

    hostnamectl set-hostname plankline-1

### Add users ==

    sudo adduser XXXX
    sudo usermod -aG sudo XXXXX
    sudo usermod -aG plankline XXXXX

### Mount Shuttle on Plankline ==

    sudo apt-get install cifs-utils
    sudo mkdir /mnt/shuttle
    sudo chmod 777 /mnt/shuttle
    sudo chown nobody:nogroup /mnt/shuttle
    sudo mount -t cifs -o user=tbkelly //10.25.187.104/shuttle /mnt/shuttle
    sudo nano /etc/fstab

Add line: "//10.25.187.104/shuttle	/mnt/shuttle	cifs	user=<user>,pass=<password>	0	0"

### Set swapiness

This is a minor performance tweak to diswade the computer from ever trying to use hard drive swap space over system memory. These computer generally have plenty of memory and have no need for offloading to physical media.

    sudo nano /etc/sysctl.conf

add "vm.swappiness=1" to the file.


## Setup Backups

Timeshift is a useful tool for maintaining backups of linux directories. Only needs to be done once per computer.

    sudo apt-get install timeshift
    sudo timeshift --create

Using NoMachine (or local monitor), open timshift and setup automatic scheduled backups. I'd recommend keeping 5 daily, 4 weekly, and 12 monthly backups. Or, using the terminal:

    sudo nano /etc/timeshift/timeshift.json


## Install NoMachine

https://www.nomachine.com/download


## RAID-based data drive

After setting up the disk stucture in the BIOS, open *disks* to create a new partition on the array. Choose XFS file system (or EXT4).

# Performance Testing
## Disk speed
To test disk IO, here's a one liner that will write a file of all zero's to a target location.

    dd if=/dev/zero of=<testing dir>/tmp.data bs=10G count=1 oflag=dsync

Example Results for *Plankline-2*:

    plankline-2:/media/plankline/Data/Data		654 MB/s
    plankline-2:/tmp				            1100 MB/s
    plankline-2:/home/tbkelly			        928 MB/s

**Recommended test set:**

    dd if=/dev/zero of=/media/plankline/Data/Data/tmp.data bs=10G count=1 oflag=dsync
    dd if=/dev/zero of=/tmp/tmp.data bs=10G count=1 oflag=dsync
    dd if=/dev/zero of=/home/tbkelly/tmp.data bs=10G count=1 oflag=dsync
