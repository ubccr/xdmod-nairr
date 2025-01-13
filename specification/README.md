# NAIRR Metrics Data Interchange format

Metrics reporting for NAIRR allocated HPC resources requires three
datasets:

1. Resource Manager Logs
1. username mapping
1. project name mapping


## Resource Manager Logs

Resource manager log files should be reported in the same format as supported
by [Open XDMoD](https://open.xdmod.org/). Log files should be gnerated once
per day. It is not necessary to filter out the NAIRR jobs - Metrics will do this
and only load NAIRR job data into XDMoD.

## Username mappings

Metrics require the mapping between the identifier for a person and their system username
on a NAIRR allocated resource. Where system username is the username that appears in
the resource manager logs. For example, for the slurm resource manager this will be the `User`
field from the `sacct` command.

Mapping information must be UTF-8 encoded in JSON format. All timestamps must be in UTC. We support both JSON 
or JSON lines format.

[Example Username Mapping \(JSON format\)](examples/person_map.json)

[Example Username Mapping \(JSON Lines format\)](examples/person_map.jsonl)

## Project name mapping

Metrics require the mapping between the identifier for a NAIRR project and the corresponding
identifier in the resource manager logs. For example, if a compute resource is using
slurm and using slurm accounts to manage access then Metrics need the mapping
between the NAIRR project `NAIRRxxxxxx` the `Account` field form the `sacct` command.

Mapping information must be UTF-8 encoded in JSON format. All timestamps must be in UTC. We support both JSON 
or JSON lines format.

[Example Project Mapping \(JSON format\)](examples/project_map.json)

[Example Project Mapping \(JSON Lines format\)](examples/project_map.jsonl)

# Sending Data to Metrics

Data should be sent to via the Metrics data API REST endpoint. Following the 
instructions on the [ACCESS Roadmap](https://readthedocs.access-ci.org/projects/integration-roadmaps/en/latest/tasks/NonACCESSUtilizationReporting_v1.html)

|  Data  | endpoint | update frequency |
| ------ | -------- | ---------------- |
| Resource Manager Logs | https://data.ccr.xdmod.org/resource-manager-logs | daily |
| Person Mapping        | https://data.ccr.xdmod.org/person-map |  When new users are added. Ok to resend complete list. |
| Project Mapping        | https://data.ccr.xdmod.org/project-map |  When new projects are added. Ok to resend complete list. |
