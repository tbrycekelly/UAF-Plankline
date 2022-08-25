#########################################################
#  Makefile
#
#  Copyright 2021
#
#  Dominic W. Daprano
#  Kyler M. Jacobson
#  Christopher M. Sullivan
#  Moritz S. Schmid
#  Robert K. Cowen
#
#  Hatfield Marine Science Center
#  Center for Genome Research and Biocomputing
#  Oregon State University
#  Corvallis, OR 97331
#
#
# This program is not free software; you can not redistribute it and/or
# modify it at all.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# 
# CITE AS:
# 
# Schmid MS, Daprano D, Jacobson KM, Sullivan C, Cowen RK. 2021.
# A Convolutional Neural Network based high-throughput image 
# classification pipeline - code and documentation to process
# plankton underwater imagery using local HPC infrastructure 
# and NSF’s XSEDE. [Software]. Zenodo. 
# http://dx.doi.org/10.5281/zenodo.4641158
#
#########################################################

CWD=`pwd`
CAT        = cat
DEL        = rm
COPY       = cp
ECHO       = echo
MOVE       = mv

PYTHON=/usr/bin/python
pythondir=${PYTHON_PREFIX}/lib/python3.10/site-packages
FFMPEG=/usr/bin/ffmpeg
FFPROBE=/usr/bin/ffprobe
ISIIS_SEG_FF=$(realpath /mnt/67b08d41-1b51-406a-a6f0-2cd683f8aaa5/Git/cfos-isiis/full-plankton-pipe-master/isiis_seg_ff)
ISIIS_SCNN=$(realpath ./SCNNx86/isiis_scnn)
ISIIS_SCNN_DIR=$(shell dirname $(ISIIS_SCNN))

CONFIG=$(CWD)/docs/config.ini
CONFIG_TMP=$(CWD)/plankton_config.ini.tmp
FINAL_CONF=$(CWD)/plankton_config.ini

all: config
	$(PYTHON) plankline.py -c $(FINAL_CONFIG) -d $(DRIVE_DIR)

config:
	@$(CAT) $(CONFIG) | grep -iv 'PIPELINE_REPO' | grep -iv 'PYTHON'| grep -iv 'FFPROBE' | grep -iv 'FFMPEG' | grep -iv 'ISIIS_SCNN_DIR' | grep -iv 'ISIIS_SCNN' | grep -iv 'ISIIS_SEG_FF' | grep -iv '\[general\]' > $(CONFIG_TMP)
	@$(ECHO) "[general]" >> $(CONFIG_TMP)
	@$(ECHO) "PIPELINE_REPO = $(CWD)" >> $(CONFIG_TMP)
	@$(ECHO) "PYTHON = $(PYTHON)" >> $(CONFIG_TMP)
	@$(ECHO) "FFMPEG = $(FFMPEG)" >> $(CONFIG_TMP)
	@$(ECHO) "FFPROBE = $(FFPROBE)" >> $(CONFIG_TMP)
	@$(ECHO) "ISIIS_SEG_FF = $(ISIIS_SEG_FF)" >> $(CONFIG_TMP)
	@$(ECHO) "ISIIS_SCNN = $(ISIIS_SCNN)" >> $(CONFIG_TMP)
	@$(ECHO) "ISIIS_SCNN_DIR = $(ISIIS_SCNN_DIR)" >> $(CONFIG_TMP)
	@$(ECHO) "" >> $(CONFIG_TMP)

	@$(DEL) -f $(FINAL_CONF)
	@$(MOVE) $(CONFIG_TMP) $(FINAL_CONF)

status:
	qstat
	
rm_config:
	rm -f config*.ini*

clean: rm_config
	rm -rf autom4te.cache/ aclocal.m4 config.status config.log core.* 
