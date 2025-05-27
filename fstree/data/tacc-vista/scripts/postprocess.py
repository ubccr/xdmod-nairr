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
            fdate = datetime.datetime.strptime(filename, '%Y-%m-%d.txt')
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

    delimiter = "|"

    srcdir = "/filetransfer/tacc/vista/accounting"
    outdir = "/data/tacc-vista/post-processed"

    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%dT%H:%M:%S', level=logging.INFO)
    logging.captureWarnings(True)

    for fullpath, filename in fileiterator(srcdir):
        with open(fullpath, "r", encoding='utf-8', errors='ignore') as filep:

            outdata = []

            for line in filep:
                tokens = line.split(delimiter)

                if tokens[5].startswith('nairr'):
                    outdata.append(line)

            if len(outdata) > 0:
                with open(f"{outdir}/{filename}", "w") as outf:
                    for record in outdata:
                        outf.write(record)
            
if __name__ == "__main__":
    main()
