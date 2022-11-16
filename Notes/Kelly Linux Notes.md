
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

# Server Setup
## Recommended Installs
These are common utilitie and prerequisites for one or more of the steps recommended by this setup document.

    sudo apt-get install r-base net-tools cifs-utils ethtool aptitude libopencv-dev libgdal-dev

## Setup /opt

    sudo mkdir /opt/Threshold-MSER & sudo mkdir /opt/SCNN
    sudo chown nobody:nogroup /opt/Threshold-MSER & sudo chown nobody:nogroup /opt/SCNN
    sudo chmod 777 -R /opt

Copy files from NAS.

To build the segmentation executable:

    cd /opt/Threshold-MSER/build
    cmake ../
    make


## Scratch Filesystem
To setup a very fast scratch drive, add the following mount configuration to `/etc/fstab`

    tmpfs /tmp tmpfs defaults,noatime,nosuid,nodev,mode=1777,size=60G 0 0

## networking
### Firewall
To check the status of the firewall:

    sudo ufw status

To allow connections on particular ports (e.g. 80 for *Shiny* and 19999 for *netdata*):

    sudo ufw allow :80
    sudo ufw allow: :19999

To turn off the firewall:

    sudo ufw disable


### Set swapiness

    sudo nano /etc/sysctl.conf

add "vm.swappiness=1" to the file.



## Install RStudio Server

    sudo apt-get install gdebi-core
    wget https://download2.rstudio.org/server/jammy/amd64/rstudio-server-2022.07.1-554-amd64.deb
    sudo gdebi rstudio-server-2022.07.1-554-amd64.deb
    sudo nano /etc/rstudio/rserver.conf

Add "www-port=80", then restart the service:

    sudo systemctrl restart rstudio-server


### Install Netdata

    wget -O /tmp/netdata-kickstart.sh https://my-netdata.io/kickstart.sh && sh /tmp/netdata-kickstart.sh


== Set password == 
```
    sudo passwd plankline
```

== Set hostname ==
```
    hostnamectl set-hostname plankline-1
```

== Add users ==

    sudo adduser XXXX
    sudo usermod -aG sudo XXXXX
    sudo usermod -aG plankline XXXXX


== Mount Shuttle on Plankline ==

    sudo apt-get install cifs-utils
    sudo mkdir /mnt/shuttle
    sudo chmod 777 /mnt/shuttle
    sudo chown nobody:nogroup /mnt/shuttle
    sudo mount -t cifs -o user=tbkelly //10.25.187.104/shuttle /mnt/shuttle
    sudo nano /etc/fstab

Add line: "//10.25.187.104/shuttle	/mnt/shuttle	cifs	user=tbkelly,pass=HelloTom22	0	0"



== Setup Automounting ==

    lsblk
    sudo nano /etc/fstab

"/dev/sdX	/media/plankline/Data	ext4	defaults	0	0"

    mkdir /media/plankline
    mkdir /media/plankline/data
    sudo chmod -R 777 /media/plankline
    sudo mount -a



== Nvidia Drivers for tesla cards:
> sudo aptitude install libnvidia-compute-470 nvidia-utils-470 nvidia-driver-470

== Nvidia Drivers for GTX cards:
> sudo aptitude install libnvidia-compute-515 nvidia-utils-515 nvidia-driver-515

= Monitoring NVIDIA processes
> watch -d -n 0.5 nvidia-smi



== Install intel 10G driver ==
> sudo apt-get install ethtool

Download from Intel X520 IXGBE driver
> tar xzf ./ixgbe-5.16.5.tar.gz
> cd ./ixgbe-5.16.5/src/
> sudo make install
> sudo nano /etc/default/grub
Add "ixgbe.allow_unsupported_sfp=1" to GRUB_CMDLINE_LINUX="" line
> sudo grub-mkconfig -o /boot/grub/grub.cfg
> sudo rmmod ixgbe && sudo modprobe ixgbe allow_unsupported_dfp=1
> sudo update-initramfs -u

> ip a
Check to see if network interface is present, e.g. eno1
Can check speed and details with:
> ethtool eno1


=== For SCNN  ===
> sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/3bf863cc.pub
> sudo aptitude install libsparsehash-dev cuda-nvcc-11-8 libcublas-11-8 libcublas-dev-11-8


=== Morphocluster ===
> sudo aptitude install docker docker-compose npm dos2unix
> mkdir -p /media/plankline/Data/morphocluster
> mkdir -p /media/plankline/Data/morphocluster/postgres
> mkdir -p /media/plankline/Data/morphocluster/data
Copy morphoclsuter directory
> sudo nano /etc/environment
Add lines: 
COMPOSE_DOCKER_CLI_BUILD=1
DOCKER_BUILDKIT=1
Save. Ctrl + x  y
> sudo docker-compose up --build

