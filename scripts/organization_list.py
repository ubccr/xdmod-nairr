sql = """
SELECT organization_id as "id",
       TRIM(organization_name) as "name",
           TRIM(COALESCE(organization_abbr, organization_name)) AS "abbr"
        FROM xras.organizations o
        JOIN xras.allocations_processes ap ON ap.allocations_process_id = o.allocations_process_id
        where ap.allocations_process_name_abbr = 'NAIRR'
        and o.is_reconciled is true
        ORDER BY "name" ASC
"""

import psycopg2
import json
import configparser


def main():
    XDMOD_CONFIG_PATH='/data/www/xdmod/etc'

    config=configparser.ConfigParser()
    config.read(f'{XDMOD_CONFIG_PATH}/portal_settings.ini')

    orgs = []
    with open(f'{XDMOD_CONFIG_PATH}/organization.json','r') as org_file:
        for org in json.load(org_file):
            orgs.append(org)
    with psycopg2.connect(database=config['tgcdbmirror']['database'].strip("'"),
                        host=config['tgcdbmirror']['host'].strip("'"),
                        user=config['tgcdbmirror']['user'].strip("'"),
                        password=config['tgcdbmirror']['pass'].strip("'"),
                        port=config['tgcdbmirror']['port'].strip("'")) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            for data in cur:
                org = {
                    "organization_id": data[0],
                    "name": data[1],
                    "abbrev":data[2]
                }
                if org not in orgs:
                    orgs.append(org)

        with open(f"{XDMOD_CONFIG_PATH}/organization.json","w") as filep:
            json.dump(orgs, filep, indent=4)



if __name__ == '__main__':
    main()