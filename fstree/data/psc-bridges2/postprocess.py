#!/usr/bin/env python3

import os
import logging
import csv
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
            fdate = datetime.datetime.strptime(filename, '%Y-%m-%d.jobs')
            if now - fdate > datetime.timedelta(days=365):
                logging.debug('Skip %s due to time range', filename)
                continue
        except ValueError:
            logging.warning('Unrecognized filename %s. Processing anyway', filename)

        fullpath = os.path.join(datasource, filename)
        if os.path.isfile(fullpath):
            yield (fullpath, filename)

def main():

    delimiter = "|"

    srcdir = "/filetransfer/pcparchives/psc/accounting"
    outdir = "/data/psc-bridges2/postprocessed"

    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%dT%H:%M:%S', level=logging.WARNING)
    logging.captureWarnings(True)

    mapping_data = pd.read_excel('/data/psc-bridges2/PSC NAIRR_Users_usage (2).xlsx')

    queue_resmap = {
        "RM": "PSC-Bridges-2-Regular-Memory",
        "EM": "PSC-Bridges-2-Extreme-Memory",
        "GPU": "PSC-Bridges-2-GPU"
    }

    mapping = {}
    for row in mapping_data.iterrows():
        mapping[row[1]['chargeid']] = row[1]['nairr_grant_number'].lower()

    for fullpath, filename in fileiterator(srcdir):
        tmpfiles = {}

        with open(fullpath, "r", encoding='utf-8', errors='ignore') as filep:
            reader = csv.reader(filep, delimiter=delimiter)

            for line in reader:
                if line[4] not in mapping:
                    continue

                if len(line) > 24:
                    line[23] = "!".join(line[23:])

                line.insert(4, 'N/A') # missing QOS field
                line.insert(21, '') # missing tres
                line[5] = mapping[line[5]]

                resource = None
                for qnam, rname in queue_resmap.items():
                    if line[3].startswith(qnam):
                        resource = rname
                        break

                if resource is None:
                    logging.error(f"Unrecognized queue {line[3]}")
                    continue

                if resource not in tmpfiles:
                    tmpfiles[resource] = tempfile.NamedTemporaryFile(mode="w", encoding="utf=8", delete=False)    

                tmpfiles[resource].write('|'.join(line[0:26]) + "\n")

        for hostname, tmpfile in tmpfiles.items():
            if not os.path.exists(os.path.join(outdir, hostname)):
                os.mkdir(os.path.join(outdir, hostname))
            tmpname = tmpfile.name
            tmpfile.close()
            target = os.path.join(outdir, hostname, filename)
            shutil.move(tmpname, target)
            os.chmod(target, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)

if __name__ == "__main__":
    main()
