#!/usr/bin/env python3
import json
import re
import argparse
import configparser

import psycopg2

project_pinames_query = """
SELECT LOWER(RM.REQUEST_NUMBER),
	P.FIRST_NAME,
	P.LAST_NAME
FROM XRAS.REQUESTS R
LEFT JOIN XRAS.REQUEST_MASTERS RM ON RM.REQUEST_MASTER_ID = R.REQUEST_MASTER_ID
LEFT JOIN XRAS.REQUEST_PEOPLE_ROLES RPR ON R.REQUEST_ID = RPR.REQUEST_ID
LEFT JOIN XRAS.PEOPLE P ON P.PERSON_ID = RPR.PERSON_ID
LEFT JOIN XRAS.REQUEST_ROLE_TYPES RRT ON RRT.REQUEST_ROLE_TYPE_ID = RPR.REQUEST_ROLE_TYPE_ID
JOIN "xras"."opportunities" AS O ON O.OPPORTUNITY_ID = R.OPPORTUNITY_ID
JOIN XRAS.ALLOCATIONS_PROCESSES AP ON O.ALLOCATIONS_PROCESS_ID = AP.ALLOCATIONS_PROCESS_ID
WHERE AP.ALLOCATIONS_PROCESS_NAME_ABBR = '{}'
	AND RRT.REQUEST_ROLE_TYPE = 'PI'
	AND RM.REQUEST_NUMBER IS NOT NULL
	AND RPR.END_DATE IS NULL
GROUP BY 1,2,3
"""

def main():

    parser = argparse.ArgumentParser(
        prog='build_heirarchy.py',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Build names.csv and hierarchy.csv files from XRAS data"
    )
    parser.add_argument('--xdmod_config_path', help='Path to the XDMoD configuration directory.', default='/etc/xdmod')
    args = parser.parse_args()
    
    config = configparser.ConfigParser()
    config.read(f'{args.xdmod_config_path}/portal_settings.ini')

    with psycopg2.connect(database=config['tgcdbmirror']['database'].strip("'"),
                        host=config['tgcdbmirror']['host'].strip("'"),
                        user=config['tgcdbmirror']['user'].strip("'"),
                        password=config['tgcdbmirror']['pass'].strip("'"),
                        port=config['tgcdbmirror']['port'].strip("'")) as conn:

        with conn.cursor() as curs:
            curs.execute(project_pinames_query.format(args.allocs_process))

            with open("names.csv", "w") as namesfp:
                writer = csv.writer(namesfp)
                for data in curs:
                    writer.writerow(data)

if __name__ == "__main__":
    main()
