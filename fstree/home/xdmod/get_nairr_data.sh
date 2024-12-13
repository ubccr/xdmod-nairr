#!/bin/bash

set -e 

printf -v today '%(%Y-%m-%d)T' -1

# Retrieve todays data from CloudBank ( which will be stored in /tmp/cloudbank/$today
#echo "Retrieving Data ..."
xdmod-cloudbank-data-retriever

#echo "Filtering Data ..."
# Filter the data so that it only contains nairr data
python3 $HOME/nairr_filter.py -i "/data/cloudbank/${today}" -o "/data/cloudbank/${today}"

#echo "Ingesting Data ..."
# Ingest the CloudBank data into XDMoD
xdmod-cloudbank-ingestor -d "/data/cloudbank/${today}" -q
