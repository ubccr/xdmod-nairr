<?php
namespace DataWarehouse\Query\ResourceActions;

use \DataWarehouse\Query\Model\Table;
use \DataWarehouse\Query\Model\TableField;
use \DataWarehouse\Query\Model\FormulaField;
use \DataWarehouse\Query\Model\WhereCondition;
use \DataWarehouse\Query\Model\Schema;
use Psr\Log\LoggerInterface;

/**
 * The RawData class is reponsible for generating a query that returns
 * the set of fact table rows given the where conditions on the aggregate
 * table.
 */
class RawData extends \DataWarehouse\Query\Query implements \DataWarehouse\Query\iQuery
{
    public function __construct(
        $realmId,
        $aggregationUnitName,
        $startDate,
        $endDate,
        $groupById = null,
        $statisticId = null,
        array $parameters = array(),
        LoggerInterface $logger = null
    ) {
        $realmId = 'ResourceActions';
        $schema = 'modw_resourceactions';
        $dataTablePrefix = 'resource_actions_fact_by_';

        parent::__construct(
            $realmId,
            $aggregationUnitName,
            $startDate,
            $endDate,
            $groupById,
            null,
            $parameters
        );

        // The same fact table row may correspond to multiple rows in the
        // aggregate table (e.g. a job that runs over two days).
        $this->setDistinct(true);

        // Override values set in Query::__construct() to use the fact table rather than the
        // aggregation table prefix from the Realm configuration.

        $this->setDataTable($schema, sprintf("%s%s", $dataTablePrefix, $aggregationUnitName));
        $this->_aggregation_unit = \DataWarehouse\Query\TimeAggregationUnit::factory(
            $aggregationUnitName,
            $startDate,
            $endDate,
            sprintf("%s.%s", $schema, $dataTablePrefix)
        );

        $dataTable = $this->getDataTable();
        $joblistTable = new Table($dataTable->getSchema(), $dataTable->getName() . "_joblist", "jl");
        $factTable = new Table(new Schema('modw_resourceactions'), "resource_actions_staging", "jt");

        $resourcefactTable = new Table(new Schema('modw'), 'resourcefact', 'rf');
        $this->addTable($resourcefactTable);

        $this->addWhereCondition(new WhereCondition(
            new TableField($dataTable, "resource_id"),
            '=',
            new TableField($resourcefactTable, "id")
        ));

        $personTable = new Table(new Schema('modw_resourceactions'), 'xras_people', 'p');

        $this->addTable($personTable);
        $this->addWhereCondition(new WhereCondition(
            new TableField($dataTable, "pi_person_id"),
            '=',
            new TableField($personTable, "xras_person_id")
        ));

        $this->addField(new TableField($resourcefactTable, "code", 'resource'));
        $this->addField(new TableField($personTable, "long_name", "name"));

        $this->addField(new FormulaField('-1', 'jobid'));
        $this->addField(new FormulaField('-1', 'local_job_id'));
        $this->addField(new FormulaField('-1', 'start_time_ts'));
        $this->addField(new FormulaField('-1', 'end_time_ts'));
        $this->addField(new FormulaField('-1', 'cpu_user'));
        $this->addField(new FormulaField('-1', 'walltime_accuracy'));

        $this->addTable($joblistTable);
        $this->addTable($factTable);

        $this->addWhereCondition(new WhereCondition(
            new TableField($joblistTable, "agg_id"),
            "=",
            new TableField($dataTable, "id")
        ));
        $this->addWhereCondition(new WhereCondition(
            new TableField($joblistTable, "action_resource_id"),
            "=",
            new TableField($factTable, "action_resource_id")
        ));
    }

    public function getQueryType(){
        return 'timeseries';
    }
}
