#!/bin/bash

# Sync Data From projects
rsync -a vortex:/projects/ccr/xmsdata/xms-frontera/xms-accounting/2025* /data/tacc-frontera/accounting/
rsync -a vortex:/projects/ccr/xmsdata/xms-frontera/ls6-accounting/2025* /data/tacc-lonestar6/accounting/

for cres in nairr-jetstream2 nairr-jetstream2-gpu  nairr-jetstream2-lm
do
    rsync -a --min-size=4 vortex:/projects/xdtas/ccstar/iu/$cres /data/jetstream/
done

# Run pre-processors
/data/psc-bridges2/postprocess.py
/data/tacc-frontera/scripts/postprocess.py
/data/tacc-lonestar6/scripts/postprocess.py
/data/ncsa/deltaai/postprocess.py

# load into XDMoD
xdmod-shredder -r Indiana-Jetstream2-GPU -f openstack -d /data/jetstream/nairr-jetstream2
xdmod-shredder -r Indiana-Jetstream2-GPU -f openstack -d /data/jetstream/nairr-jetstream2-lm/
xdmod-shredder -r Indiana-Jetstream2-GPU -f openstack -d /data/jetstream/nairr-jetstream2-gpu/
xdmod-shredder -r PSC-Bridges-2-Regular-Memory- -f slurm -d /data/psc-bridges2/postprocessed/PSC-Bridges-2-Regular-Memory -q
xdmod-shredder -r PSC-Bridges-2-GPU- -f slurm -d /data/psc-bridges2/postprocessed/PSC-Bridges-2-GPU -q
xdmod-shredder -r TACC-Frontera -f frontera -d /data/tacc-frontera/post-processed/TACC\ Frontera -q
xdmod-shredder -r TACC-Frontera-GPU -f frontera -d /data/tacc-frontera/post-processed/TACC\ Frontera\ GPU -q
xdmod-shredder -r TACC-Lonestar6 -f slurm -d /data/tacc-lonestar6/post-processed/TACC-Lonestar6 -q
xdmod-shredder -r TACC-Lonestar6-GPU -f slurm -d /data/tacc-lonestar6/post-processed/TACC-Lonestar6-GPU -q
xdmod-shredder -r NCSA-DeltaAI -f slurmjson -d /data/ncsa/deltaai/postprocessed -q
xdmod-shredder -r NCSA-Delta-GPU- -f slurmjson -d /data/ncsa/delta-gpu -q
xdmod-shredder -r Purdue-Anvil-GPU -f slurm -d /data/purdue/anvil/Purdue-Anvil-GPU -q
xdmod-shredder -r TAMU-ACES -f slurmjson -d /data/tamu/aces/postprocessed/ -q
xdmod-shredder -r PSC-Neocortex- -f slurmjson -d /data/psc/postprocessed/ -q

/usr/share/xdmod/tools/etl/etl_overseer.php -p nairr.resource-actions -m 2000-01-01
/usr/bin/xdmod-build-filter-lists --realm ResourceActions --quiet

xdmod-ingestor -q
