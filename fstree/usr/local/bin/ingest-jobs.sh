#!/bin/bash

# Sync Data From projects
for cres in nairr-jetstream2 nairr-jetstream2-gpu  nairr-jetstream2-lm
do
    sudo -u xdmod rsync -a --min-size=4 vortex:/projects/xdtas/ccstar/iu/$cres /data/jetstream/
done

sudo -u jpwhite4 rsync -av rainbarrel-data-copy:/data/resource-manager-logs/neocortex /data/psc
sudo -u jpwhite4 rsync -av rainbarrel-data-copy:/data/resource-manager-logs/aces/* /data/tamu/json
sudo -u jpwhite4 rsync -av rainbarrel-data-copy:/data/resource-manager-logs/nvidia-dgx-cloud/* /data/dgx/logs

# Run pre-processors
sudo -u xdmod /data/psc-bridges2/postprocess.py
sudo -u xdmod /data/tacc-frontera/scripts/postprocess.py
sudo -u xdmod /data/tacc-lonestar6/scripts/postprocess.py
sudo -u xdmod /data/ncsa/deltaai/postprocess.py
sudo -u xdmod /data/psc/postprocess.py
sudo -u xdmod /data/tamu/postprocess.py
sudo -u xdmod /data/dgx/postprocess.py
sudo -u xdmod /data/purdue/postprocess.py

# Still waiting for SDSC data /data/sdsc/postprocess.py


# load into XDMoD
sudo -u xdmod xdmod-shredder -r Indiana-Jetstream2-GPU -f openstack -d /data/jetstream/nairr-jetstream2
sudo -u xdmod xdmod-shredder -r Indiana-Jetstream2-GPU -f openstack -d /data/jetstream/nairr-jetstream2-lm/
sudo -u xdmod xdmod-shredder -r Indiana-Jetstream2-GPU -f openstack -d /data/jetstream/nairr-jetstream2-gpu/
sudo -u xdmod xdmod-shredder -r PSC-Bridges-2-Regular-Memory- -f slurm -d /data/psc-bridges2/postprocessed/PSC-Bridges-2-Regular-Memory -q
sudo -u xdmod xdmod-shredder -r PSC-Bridges-2-GPU- -f slurm -d /data/psc-bridges2/postprocessed/PSC-Bridges-2-GPU -q
sudo -u xdmod xdmod-shredder -r TACC-Frontera -f frontera -d /data/tacc-frontera/post-processed/TACC\ Frontera -q
sudo -u xdmod xdmod-shredder -r TACC-Frontera-GPU -f frontera -d /data/tacc-frontera/post-processed/TACC\ Frontera\ GPU -q
sudo -u xdmod xdmod-shredder -r TACC-Lonestar6 -f slurm -d /data/tacc-lonestar6/post-processed/TACC-Lonestar6 -q
sudo -u xdmod xdmod-shredder -r TACC-Lonestar6-GPU -f slurm -d /data/tacc-lonestar6/post-processed/TACC-Lonestar6-GPU -q
sudo -u xdmod xdmod-shredder -r NCSA-DeltaAI -f slurmjson -d /data/ncsa/deltaai/postprocessed -q
sudo -u xdmod xdmod-shredder -r NCSA-Delta-GPU- -f slurmjson -d /data/ncsa/delta-gpu -q
sudo -u xdmod xdmod-shredder -r Purdue-Anvil-GPU -f slurm -d /data/purdue/anvil/Purdue-Anvil-GPU -q
sudo -u xdmod xdmod-shredder -r Purdue-Anvil-CPU -f slurm -d /data/purdue/anvil/Purdue-Anvil-CPU -q
sudo -u xdmod xdmod-shredder -r TAMU-ACES -f slurmjson -d /data/tamu/aces/postprocessed/ -q
sudo -u xdmod xdmod-shredder -r PSC-Neocortex- -f slurmjson -d /data/psc/postprocessed/ -q
sudo -u xdmod xdmod-shredder -r NVIDIA-DGX-Cloud -f slurmjson -d /data/dgx/postprocessed/ -q

sudo -u xdmod /usr/share/xdmod/tools/etl/etl_overseer.php -p nairr.resource-actions -m 2000-01-01
sudo -u xdmod /usr/bin/xdmod-build-filter-lists --realm ResourceActions --quiet

sudo -u xdmod xdmod-ingestor -q
