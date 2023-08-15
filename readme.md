# Plankline Scripts
Scripts were originally from the Plankline project controlled by OSU (citation's to be included). I have heavily modified and repurposed the code to suit our architecture and to improve logging and performance. These scripts are available as is and I make no claim to ownership or control of any potentially sensitive code. These are intended for in-house use at UAF.


# Setup and Documentation

Follow the links below for documentation of each of these subjects:

1. [General Setup](Notes/General%20Setup.md)
2. [Plankline](Notes/Plankline.md)
3. [Morphocluster](Notes/Morphocluster.md)



## Getting started


To run plankline with a specific configuration file (required):

    python3 segmentation.py -c <ini> -d <dir>
    python3 classification.py -c <ini> -d <dir>

So for example:

    python3 segmentation.py -c osu_test_config.ini -d /media/plankline/data/test_data

