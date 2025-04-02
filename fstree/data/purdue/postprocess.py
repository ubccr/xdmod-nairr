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
            fdate = datetime.datetime.strptime(filename, '%Y%m%d')
            if now - fdate > datetime.timedelta(days=600):
                logging.debug('Skip %s due to time range', filename)
                continue
        except ValueError:
            logging.warning('Unrecognized filename %s. Processing anyway', filename)

        fullpath = os.path.join(datasource, filename)
        if os.path.isfile(fullpath):
            yield (fullpath, filename)

def main():

    delimiter = "|"

    srcdir = "/filetransfer/pcparchives/purdue/anvil/sacct"
    outdir = "/data/purdue/anvil"

    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%dT%H:%M:%S', level=logging.WARNING)
    logging.captureWarnings(True)

    for fullpath, filename in fileiterator(srcdir):
        tmpfiles = {}

        with open(fullpath, "r", encoding='utf-8', errors='ignore') as filep:
            reader = csv.reader(filep, delimiter=delimiter)

            for line in reader:
                if not line[5].startswith('ai'):
                    continue

                queue = line[3]
                if queue.lower().startswith('gpu'):
                    resource = 'Purdue-Anvil-GPU'
                else:
                    resource = 'Purdue-Anvil-CPU'

                if len(line) > 26:
                    line[25] = "!".join(line[25:])

                line[5] = 'NAIRR' + line[5][2:8]

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
