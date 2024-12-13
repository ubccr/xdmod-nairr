#!/usr/bin/env python3

import logging
import os
import datetime

def fileiterator(datasource):
    filenames = [x for x in os.listdir(datasource)]
    filenames.sort()

    now = datetime.datetime.now()

    for filename in filenames:
        try:
            fdate = datetime.datetime.strptime(filename, '%Y-%m-%d.log')
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

    srcdir = "/data/tacc-frontera/accounting"
    outdir = "/data/tacc-frontera/post-processed"

    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%dT%H:%M:%S', level=logging.INFO)
    logging.captureWarnings(True)

    for fullpath, filename in fileiterator(srcdir):
        with open(fullpath, "r", encoding='utf-8', errors='ignore') as filep:

            outdata = { 'TACC Frontera': [], 'TACC Frontera GPU': [] }

            for line in filep:
                tokens = line.split(delimiter)

                if tokens[5].startswith('nairr'):
                    if tokens[3] in ['rtx', 'rtx-dev']:
                        outdata['TACC Frontera GPU'].append(line)
                    else:
                        outdata['TACC Frontera'].append(line)

            for res, data in outdata.items():
                if len(data) > 0:
                    with open(f"{outdir}/{res}/{filename}", "w") as outf:
                        for record in data:
                            outf.write(record)
            
if __name__ == "__main__":
    main()
