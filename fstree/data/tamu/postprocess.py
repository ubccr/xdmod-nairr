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
            fdate = datetime.datetime.strptime(filename[-15:], '%Y-%m-%d.json')
            if now - fdate > datetime.timedelta(days=365):
                logging.debug('Skip %s due to time range', filename)
                continue
        except ValueError:
            logging.warning('Unrecognized filename %s. Skipping', filename)
            continue

        fullpath = os.path.join(datasource, filename)
        if os.path.isfile(fullpath):
            yield (fullpath, filename)

def main():

    srcdir = "/data/tamu/json"
    outdir = "/data/tamu/aces/postprocessed"

    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%dT%H:%M:%S', level=logging.WARNING)
    logging.captureWarnings(True)

    mapping_data = pd.read_excel('/data/mapping/NAIRR usage reported as of 12-09-2024.xlsx', sheet_name='TAMU')


    mapping = {}
    for row in mapping_data.iterrows():
        mapping[str(row[1]['ACES slurm account'])] = row[1]['NAIRR_grant_number'].lower()

    for fullpath, filename in fileiterator(srcdir):

        with open(fullpath, "r", encoding='utf-8', errors='ignore') as filep:
            
            slurm_log = json.load(filep)

            out_jobs = []

            for job in slurm_log['jobs']:
                charge_id = job['account']
                if charge_id in mapping:
                    print(charge_id, job['account'], mapping[charge_id])
                    job['account'] = mapping[charge_id]
                    if job['user'] is None:
                        job['user'] = job['group']
                    out_jobs.append(job)

            if out_jobs:
                slurm_log['jobs'] = out_jobs
                target = os.path.join(outdir, filename)
                with open(target, 'w', encoding="utf=8") as outfp:
                    json.dump(slurm_log, outfp)
                os.chmod(target, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)

if __name__ == "__main__":
    main()
