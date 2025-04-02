#!/usr/bin/env python3

import logging
import os
import datetime
import csv
import argparse
from collections import defaultdict

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
            logging.warning('Unrecognized filename %s. Processing anyway', filename)

        fullpath = os.path.join(datasource, filename)
        if os.path.isfile(fullpath):
            yield (fullpath, filename)

OUTFIELDS = [ "jobid", "jobidraw", "cluster", "partition", "qos", "account", "group", "gid", "user", "uid", "submit", "eligible", "start", "end", "elapsed", "exitcode", "state", "nnodes", "ncpus", "reqcpus", "reqmem", "reqtres", "alloctres", "timelimit", "nodelist", "jobname"] 

CONSTMAP = {
    "cluster": "N/A",
    "qos": "N/A",
    "group": "N/A",
    "gid": "0",
    "uid": "0",
    "exitcode": "0",
    "reqcpus": "0",
    "reqmem": "0"
}

MAPPING = {
    "jobid": "JobID",
    "jobidraw": "JobID",
    "user": "User",
    "account": "Account",
    "start": "Start",
    "end": "End",
    "eligible": "Start",
    "submit": "Submit",
    "partition": "Partition",
    "timelimit": "Timelimit",
    "jobname": "JobName",
    "state": "State",
    "nnodes": "NNodes",
    "reqcpus": "ReqCPUS",
    "nodelist": "NodeList"
}

def getresource(row):
    partition = row['Partition']
    if partition in ['development', 'normal', 'large', 'vm-small']:
        return 'TACC-Lonestar6'
    elif partition in ['gpu-a100', 'gpu-a100-dev', 'gpu-a100-small', 'gpu-h100']:
        return 'TACC-Lonestar6-GPU'
    else:
        raise Exception("Unknown queue", partition)
    
def getcores(row):
    partition = row['Partition']
    nodes = int(row['NNodes'])

    if partition in ['development', 'normal', 'large']:
        return 128 * nodes
    elif partition in ['gpu-a100', 'gpu-a100-dev']:
        return 128 * nodes
    elif partition in ['gpu-a100-small']:
        return 32 * nodes
    elif partition in ['vm-small']:
        return 16 * nodes
    elif partition in ['gpu-h100']:
        return 96 * nodes
    else:
        raise Exception("Unknown queue", partition)

def getgres(row):
    partition = row['Partition']
    nodes = int(row['NNodes'])

    if partition in ['development', 'normal', 'large']:
        return ""
    elif partition in ['gpu-a100', 'gpu-a100-dev']:
        return "gres/gpu=3"
    elif partition in ['gpu-a100-small']:
        return "gres/gpu=1"
    elif partition in ['vm-small']:
        return ""
    elif partition in ['gpu-h100']:
        return "gres/gpu=2"
    else:
        raise Exception("Unknown queue", partition)


def getelapsed(row):
    if row['Start'] == 'None':
        return ''
    
    start = datetime.datetime.strptime(row['Start'], "%Y-%m-%dT%H:%M:%S")
    end = datetime.datetime.strptime(row['End'], "%Y-%m-%dT%H:%M:%S")
    duration = (end - start).seconds
    minutes = duration // 60
    seconds = duration % 60
    return f'{minutes}:{seconds}'
              
def main():

    parser = argparse.ArgumentParser(
                    prog='ProgramName',
                    description='What the program does',
                    epilog='Text at the bottom of help')

    parser.add_argument('-i', '--indir', default="/filetransfer/tacc/ls6/accounting")
    parser.add_argument('-o', '--outdir', default="/data/tacc-lonestar6/post-processed")
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-q', '--quiet', action='store_true')

    args = parser.parse_args()

    delimiter = "|"

    loglevel = logging.INFO
    if args.verbose:
        loglevel = logging.DEBUG
    if args.quiet:
        loglevel = logging.WARN

    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%dT%H:%M:%S', level=logging.INFO)
    logging.captureWarnings(True)

    for fullpath, filename in fileiterator(args.indir):
        with open(fullpath, "r", encoding='utf-8', errors='ignore') as filep:

            acct = csv.DictReader(filep, delimiter=delimiter)
            outdata = defaultdict(list)
            for row in acct:
                if row['Account'].startswith('nairr'):
                    outrow = []
                    for field in OUTFIELDS:
                        if field in MAPPING:
                            outrow.append(row[MAPPING[field]])
                        elif field in CONSTMAP:
                            outrow.append(CONSTMAP[field])
                        elif field == 'elapsed':
                            outrow.append(getelapsed(row))
                        elif field in ['alloctres', 'reqtres']:
                            outrow.append(getgres(row))
                        elif field == 'ncpus':
                            outrow.append(getcores(row))
                        else:
                            raise Exception("Unknown field: " + field)
                    outdata[getresource(row)].append(outrow)

            for resource, logdata in outdata.items():
                outfilename = filename[:-3] + "log"
                with open(f"{args.outdir}/{resource}/{outfilename}", "w") as outf:
                    outwriter = csv.writer(outf, delimiter=delimiter, quoting=csv.QUOTE_MINIMAL)
                    for record in logdata:
                        outwriter.writerow(record)
            
if __name__ == "__main__":
    main()
