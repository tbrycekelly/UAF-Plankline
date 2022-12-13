# Software Setup
## Recommended Installs
These are common utilitie and prerequisites for one or more of the steps recommended by this setup document.

    sudo apt-get install r-base net-tools cifs-utils ethtool aptitude libopencv-dev libgdal-dev
    sudo aptitude install nvidia-cuda-toolkit timeshift nvtop

Python Related

    sudo aptitude install python2 python3 python2-dev python3-devpython3-pip 
    sudo aptitude install python3-skimage python3-opencv
    pip3 install gpustat

Misc

    sudo aptitude install perl libnet-ssleay-perl openssl libauthen-pam-perl libpam-runtime libio-pty-perl apt-show-versions unzip 
    sudo aptitude install nemo baobab ncdu htop mc bpytop
    sudo aptitude install gimp digikam geeqie mplayer smplayer
    sudo aptitude install libreoffice openssh-server
    sudo aptitude install mesa-utils glmark2 trash-cli

NVIDIA Requirements for GPGPUs

    sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/3bf863cc.pub &&
    wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.0-1_all.deb

    sudo dpkg -i cuda-keyring_1.0-1_all.deb
    sudo aptitude update
    sudo aptitude install libsparsehash-dev cuda-nvcc-11-8 libcublas-11-8 libcublas-dev-11-8


## Setup Plankline
This can be performed by any/every user on a system and can be placed in any folder. So far we have been placing this folder, /UAF-Plankline/ in Tom's documents folder. Typical locations that make sense include ~ (home directory), ~/Desktop, ~/Documents.

    cd ~
    git clone https://github.com/tbrycekelly/UAF-Plankline.git

To update an existing folder (will remove the config files present):

    cd ~/UAF-Plankline
    git pull

To run plankline with a specific configuration file (required):

    python3 segmentation.py -c config.ini
    python3 classification.py -c config.ini

These scripts require the segmentation executable and SCNN executable to be available (see below).    

## Setup SCNN

for the first install,

    cd /opt
    sudo git clone https://github.com/tbrycekelly/UAF-SCNN.git
    sudo chown -R plankline:plankline /opt/UAF-SCNN
    sudo chmod 776 -R /opt/UAF-SCNN

To update from github,

    cd /opt/UAF-SCNN
    git pull

To build SCNN:

    cd /opt/UAF-SCNN/build
    make clean
    make wp2

If there are undefined refences on the make, check that the LIBS line in ./build/Makefile is the output of `pkg-config opencv --cflags --libs` and inclues `-lcublas`.

Test it and copy it to final directory (if it works):

    ./wp2
    cp ./wp2 ../scnn


## Setup Segmentation

On the first install, 

    cd /opt
    sudo git clone https://github.com/tbrycekelly/UAF-Segmentation
    sudo chown -R plankline:plankline /opt/UAF-Segmentation
    sudo chmod 776 -R /opt/UAF-Segmentation

To update the executable with a new version:

    cd /opt/UAF-Segmentation
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

    sudo apt-get install gdebi-core;
    wget https://download2.rstudio.org/server/jammy/amd64/rstudio-server-2022.07.1-554-amd64.deb;
    sudo gdebi rstudio-server-2022.07.1-554-amd64.deb;
    sudo nano /etc/rstudio/rserver.conf;

Add "www-port=80", then restart the service:

    sudo systemctrl restart rstudio-server

#### To install the plankline processing scripts
Note, that the default "home" directory for rstudio will be the home directory of the user that you log in as.

    cd ~
    git clone https://github.com/tbrycekelly/Plankline-Processing-Scripts.git


### Install Netdata

    wget -O /tmp/netdata-kickstart.sh https://my-netdata.io/kickstart.sh && sh /tmp/netdata-kickstart.sh


# Hardware Setup
## Video Cards
### Nvidia Drivers for **Tesla** cards:

    sudo aptitude install libnvidia-compute-470 nvidia-utils-470 nvidia-driver-470-server
    sudo ldconfig


### Nvidia Drivers for **GTX** cards:
    
    sudo aptitude install libnvidia-compute-515 nvidia-utils-515 nvidia-driver-515
    sudo ldconfig


### Monitoring NVIDIA processes

    nvtop

## Compile and Install OpenCV 3.4

    sudo aptitude install build-essential cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev
    sudo aptitude install python3-dev python3-numpy libtbb2 libtbb-dev
    sudo aptitude install libjpeg-dev libpng-dev libtiff5-dev jasper libdc1394-dev libeigen3-dev libtheora-dev libvorbis-dev libxvidcore-dev libx264-dev sphinx-common libtbb-dev yasm libfaac-dev libopencore-amrnb-dev libopencore-amrwb-dev libopenexr-dev libgstreamer-plugins-base1.0-dev libavutil-dev libavfilter-dev
    sudo aptitude install libtesseract-dev libopenblas-dev libopenblas64-dev ccache
  
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

Download from Intel X520 IXGBE driver

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


## Morphocluster
Generally just follow the outline provided here: [https://github.com/morphocluster/morphocluster]

    sudo aptitude install docker docker-compose npm dos2unix
    mkdir -p /media/plankline/Data/morphocluster
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

    lsblk
    sudo nano /etc/fstab

"/dev/sdX	/media/plankline/Data	ext4	defaults	0	0"

    mkdir /media/plankline
    mkdir /media/plankline/data
    sudo chmod -R 777 /media/plankline
    sudo mount -a

## Scratch Filesystem
To setup a very fast scratch drive, add the following mount configuration to `/etc/fstab`

    tmpfs /tmp tmpfs defaults,noatime,nosuid,nodev,mode=1777,size=60G 0 0

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

To turn off the firewall:

    sudo ufw disable

To View Rules and Delete them:

    sudo ufw status numbered
    sudo ufw delete XX



## Misc Linux Tasks
### Set password == 

    sudo passwd plankline

### Set hostname ==

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

Add line: "//10.25.187.104/shuttle	/mnt/shuttle	cifs	user=tbkelly,pass=HelloTom22	0	0"

### Set swapiness

    sudo nano /etc/sysctl.conf

add "vm.swappiness=1" to the file.


## Setup Backups

    sudo aptitude install timeshift
    sudo timeshift --create

Using NoMachine (or local monitor), open timshift and setup automatic scheduled backups. I'd recommend keeping 5 daily, 4 weekly, and 12 monthly backups. Or, using teh CLI:

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
    plankline-2:/tmp				1100 MB/s
    plankline-2:/home/tbkelly			928 MB/s

**Recommended test set:**

    dd if=/dev/zero of=/media/plankline/Data/Data/tmp.data bs=10G count=1 oflag=dsync
    dd if=/dev/zero of=/tmp/tmp.data bs=10G count=1 oflag=dsync
    dd if=/dev/zero of=/home/tbkelly/tmp.data bs=10G count=1 oflag=dsync
