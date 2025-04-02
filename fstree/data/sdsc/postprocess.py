#!/usr/bin/env python3

import os
import logging
import json
import datetime
import tempfile
import stat
import shutil
import gzip
import re
import pandas as pd

def fileiterator(datasource):
    filenames = [x for x in os.listdir(datasource)]
    filenames.sort()

    now = datetime.datetime.now()

    exp = re.compile("^sacct_json_([a-z_]+)_([0-9]{4}-[0-9]{2}-[0-9]{2}).json.gz$")

    for filename in filenames:
        mtch = exp.match(filename)
        if not mtch:
            continue
        #if mtch.group(1) != 'expanse_gpu':
        #    continue

        fdate = datetime.datetime.strptime(mtch.group(2), '%Y-%m-%d')
        if now - fdate > datetime.timedelta(days=30):
            logging.debug('Skip %s due to time range', filename)
            continue

        fullpath = os.path.join(datasource, filename)
        if os.path.isfile(fullpath):
            yield (fullpath, filename)

def main():

    srcdir = "/filetransfer/pcparchives/sdsc/accounting/"
    outdir = "/data/sdsc/postprocessed"

    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%dT%H:%M:%S', level=logging.WARNING)
    logging.captureWarnings(True)

    mapping_data = pd.read_excel('/data/mapping/NAIRR Jan-2025 Usage.xlsx', sheet_name='SDSC')


    mapping = {}
    for row in mapping_data.iterrows():
        mapping[row[1]['SDSC Local Project id'].lower()] = row[1]['NAIRR Grant'].lower()

    for fullpath, filename in fileiterator(srcdir):

        with gzip.open(fullpath, "r") as filep:
            
            try:
                slurm_log = json.load(filep)
            except json.decoder.JSONDecodeError:
                logging.warning("Unable to JSON decode " + fullpath)
                continue

            outdata = {}

            for job in slurm_log['jobs']:
                charge_id = job['account']
                resource = 'todo'

                if charge_id in mapping:
                    print(job)
                    job['account'] = mapping[charge_id]

                    if resource not in outdata:
                        outdata[resource] = []

                    outdata[resource].append(job)

            for resource_name, out_jobs in outdata.items():
                if not os.path.exists(os.path.join(outdir, resource_name)):
                    os.mkdir(os.path.join(outdir, resource_name))

                output = { 'jobs':  out_jobs}
                target = os.path.join(outdir, resource_name, filename)
                with open(target, 'w', encoding="utf=8") as outfp:
                    json.dump(output, outfp)
                os.chmod(target, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)

if __name__ == "__main__":
    main()
