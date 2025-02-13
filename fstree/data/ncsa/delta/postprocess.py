#!/usr/bin/env python3

import os
import logging
import json
import datetime
import tempfile
import stat
import shutil
import pandas as pd

def fileiterator(datasource):
    filenames = [x for x in os.listdir(datasource)]
    filenames.sort()

    now = datetime.datetime.now()

    for filename in filenames:
        try:
            fdate = datetime.datetime.strptime(filename, '%Y-%m-%d.json')
            if now - fdate > datetime.timedelta(days=10000):
                logging.debug('Skip %s due to time range', filename)
                continue
        except ValueError:
            logging.warning('Unrecognized filename %s. Skipping', filename)
            continue

        fullpath = os.path.join(datasource, filename)
        if os.path.isfile(fullpath):
            yield (fullpath, filename)

def main():

    srcdir = "/projects/xdtas/ccstar/ncsa/delta/slurm_logs/"
    outdir = "/user/jpwhite4/xdmod-nairr/fstree/data/ncsa/delta"

    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%dT%H:%M:%S', level=logging.WARNING)
    logging.captureWarnings(True)

    mapping_data = pd.read_excel('/user/jpwhite4/NAIRR Jan-2025 Usage.xlsx', sheet_name='NCSA')


    mapping = {}
    for row in mapping_data.iterrows():
        mapping[row[1]['subgrantnumber']] = row[1]['nairr_grant_number'].lower()

    for fullpath, filename in fileiterator(srcdir):

        with open(fullpath, "r", encoding='utf-8', errors='ignore') as filep:
            
            try:
                slurm_log = json.load(filep)
            except json.decoder.JSONDecodeError:
                logging.warning("Unable to JSON decode " + fullpath)
                continue

            outdata = {}

            for job in slurm_log['jobs']:
                charge_id = job['account'][0:4]
                resource = job['account'][5:]

                if charge_id in mapping:
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
