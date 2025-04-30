sql="""
SELECT username AS orcid,first_name, middle_name,last_name, TRIM(o.organization_name) AS "organization_name"
FROM xras.people p
JOIN xras.organizations o ON o.organization_id = p.organization_id
JOIN xras.allocations_processes ap ON ap.allocations_process_id = o.allocations_process_id
WHERE ap.allocations_process_name_abbr = 'NAIRR'
ORDER BY p.person_id ASC;
"""
nairr_project_sql="""
SELECT DISTINCT
       username AS orcid,
       first_name,
       middle_name,
       last_name,
       TRIM(o.organization_name) AS "organization_name",
       rpr.request_role_type_id,
       r.request_master_id,
       rm.request_number AS "nairr_project_name",
       p.person_id
FROM xras.people p
JOIN xras.organizations o ON o.organization_id = p.organization_id
JOIN xras.request_people_roles rpr ON p.person_id = rpr.person_id
JOIN xras.requests r ON r.request_id = rpr.request_id
JOIN xras.request_masters rm ON r.request_master_id = rm.request_master_id
JOIN xras.request_role_types rtt ON rpr.request_role_type_id = rtt.request_role_type_id
JOIN xras.allocations_processes ap ON ap.allocations_process_id = o.allocations_process_id
WHERE ap.allocations_process_name_abbr = 'NAIRR'
  AND rtt.request_role_type = 'PI'
  AND rm.request_number IS NOT NULL
ORDER BY p.person_id ASC;

"""
import psycopg2
import csv
import configparser

def main():
    XDMOD_CONFIG_PATH='/data/www/xdmod/etc'

    config=configparser.ConfigParser()
    config.read(f'{XDMOD_CONFIG_PATH}/portal_settings.ini')
    names = []
    with psycopg2.connect(database=config['tgcdbmirror']['database'].strip("'"),
                          host=config['tgcdbmirror']['host'].strip("'"),
                          user=config['tgcdbmirror']['user'].strip("'"),
                          password=config['tgcdbmirror']['pass'].strip("'"),
                          port=config['tgcdbmirror']['port'].strip("'")) as conn:

        with conn.cursor() as cur:
            cur.execute(sql)
            for data in cur:
                name = [data[0],data[1],data[3],data[4]]
                if name not in names:
                    names.append(name)
            cur.execute(nairr_project_sql)
            for data in cur:
                name = [data[7],data[1],data[3],data[4]]
                if name not in names:
                    names.append(name)

        with open('names.csv', 'w') as f:
            write = csv.writer(f)
            write.writerows(names)



if __name__ == '__main__':
    main()
