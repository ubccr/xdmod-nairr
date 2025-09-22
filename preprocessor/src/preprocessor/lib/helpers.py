""" Helper functions """
import os
import re
import json
import datetime
import logging
import configparser
import psycopg

def direct_xras_query(query):
    config = configparser.ConfigParser()
    config.read('/etc/xdmod/portal_settings.ini')
    connectstr = "postgresql://{}:{}@{}/{}".format(
        config['tgcdbmirror']['user'].strip("'"),
        config['tgcdbmirror']['pass'].strip("'"),
        config['tgcdbmirror']['host'].strip("'"),
        config['tgcdbmirror']['database'].strip("'"))

    results = {}

    with psycopg.connect(connectstr) as conn:
        # Open a cursor to perform database operations
        with conn.cursor() as cur:
            cur.execute(query)
            for row in cur:
                results[row[0]] = row[1]

    return results

def config(confpath, resource):

    combined = {}
    with open(confpath, 'r', encoding='utf-8', errors='ignore') as filep:
        conf = json.load(filep)
        for c, v in conf.items():
            if c != 'resources':
                combined[c] = v

        for c, v in conf['resources'][resource].items():
            combined[c] = v

    return combined


def fileiterator(prefix, age_days, fileregex):
    filenames = [x for x in os.listdir(prefix)]
    filenames.sort()

    now = datetime.datetime.now()

    freg = re.compile(fileregex)

    for filename in filenames:
        mtch = freg.match(filename)
        if not mtch:
            logging.debug(f'Skipping file with unrecognized name "{filename}".')
            continue
        try:
            fdate = datetime.datetime.strptime(mtch.group(1) + '-' + mtch.group(2) + '-' + mtch.group(3), '%Y-%m-%d')
            if now - fdate > datetime.timedelta(days=age_days):
                logging.debug('Skip %s due to time range', filename)
                continue
        except ValueError:
            logging.warning(f'Skip due to syntax error in datestamp in file "{filename}"')
            continue

        fullpath = os.path.join(prefix, filename)
        if os.path.isfile(fullpath):
            yield (fullpath, filename)


class DgxTranslator:
    def __init__(self, _):
        pass

    def translate(self, _, filepath):
        filename = os.path.basename(filepath)
        fparts = filename.split(".")
        return (fparts[2], 'dgx')

class TamuTranslator:
    def __init__(self, mapping):
        self.mapping = mapping

    def translate(self, job, _):
        charge_id = job['account']

        if charge_id in self.mapping:
            return (self.mapping[charge_id], 'aces')

        return (None, None)


class NcsaTranslator:
    def __init__(self, mapping):
        self.mapping = mapping

        query = "SELECT site_project_id, LOWER(pro.grant_number) FROM acct.projects_map pm JOIN acct.projects pro ON pro.project_id = pm.project_id WHERE pro.allocations_process_id = 108 AND organization_id = 844"

        for charge_number, project in direct_xras_query(query).items():
            if charge_number not in self.mapping:
                self.mapping[charge_number] = project

    def translate(self, job, _):
        charge_id = job['account'][0:4]
        resource = job['account'][5:]

        if charge_id in self.mapping:
            return (self.mapping[charge_id], resource)

        return (None, None)


class SdscTranslator:
    def __init__(self, mapping):
        self.mapping = mapping
        self.exp = re.compile("^sacct_json_([a-z_]+)_([0-9]{4}-[0-9]{2}-[0-9]{2}).json.gz$")

    def translate(self, job, fullpath):
        charge_id = job['account']

        if charge_id in self.mapping:
            mtch = self.exp.match(os.path.basename(fullpath))
            return (self.mapping[charge_id], mtch.group(1))

        return (None, None)
