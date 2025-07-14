<?php

namespace Rest\Controllers;

use CCR\DB;
use CCR\Log;
use Exception;
use Psr\Log\LoggerInterface;

use Silex\Application;
use Silex\ControllerCollection;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpKernel\Exception\NotFoundHttpException;

class CustomReportControllerProvider extends BaseControllerProvider
{
     const LOG_MODULE = 'custom-report-controller';

    /**
     * @var LoggerInterface
     */
    private $logger;

    public function __construct(array $params = [])
    {
        parent::__construct($params);
        $this->logger = Log::factory(
            self::LOG_MODULE,
            [
                'console' => false,
                'file' => false,
                'mail' => false
            ]
        );
    }

    /**
     * Set up data warehouse export routes.
     *
     * @param Application $app
     * @param ControllerCollection $controller
     */
    public function setupRoutes(
        Application $app,
        ControllerCollection $controller
    ) {
        $root = $this->prefix;
        $current = get_class($this);

        $controller->get("$root/reports", "$current::getReports");

        $controller->get("$root/thumbnail/{report_id}", "$current::getReportThumbnail")
            ->assert('report_id', '(\w|_|-])+');

        $controller->get("$root/report/{report_id}", "$current::getReport")
            ->assert('report_id', '(\w|_|-])+');
    }

    /**
     * Get all the reports available for exporting for the current user.
     *
     * @param Request $request
     * @param Application $app
     * @return \Symfony\Component\HttpFoundation\JsonResponse
     */
    public function getReports(Request $request, Application $app)
    {

        list($_, $report_config) = $this->getConfiguration();

        $report_list = array();

        foreach ($report_config as $report_id => $report_meta) {
            array_push($report_list, array(
                'name' => $report_id,
                'version' => $report_meta['version'] ,
                'title' => $report_meta['title'] ,
                'description' => $report_meta['description']
            ));
        }

        return $app->json(array(
            'success' => true,
            'report_list' => $report_list,
            'total' => count($report_list)
        ));
    }

    /**
     * Get the report thumbnail image.
     *
     * @param Request $request
     * @param Application $app
     * @param string $report_id
     * @return \Symfony\Component\HttpFoundation\BinaryFileResponse
     * @throws NotFoundHttpException if no report exists with the given ID.
     */
    public function getReport(Request $request, Application $app, $report_id)
    {

        list($base_path, $report_config) = $this->getConfiguration();

        if (isset($report_config[$report_id])) {
            return $app->sendFile(
                $base_path . '/' . $report_config[$report_id]['filename'],
                200,
                [
                    'Content-type' => 'text/html',
                    'Content-Disposition' => sprintf(
                        'attachment; filename="%s"',
                        $report_config[$report_id]['filename']
                    )
                ]
            );
        }

        throw new NotFoundHttpException('Report does not exist');
    }
    /**
     * Get the requested data.
     *
     * @param Request $request
     * @param Application $app
     * @param string $report_id
     * @return \Symfony\Component\HttpFoundation\BinaryFileResponse
     * @throws NotFoundHttpException if no report exists with the given ID.
     */
    public function getReportThumbnail(Request $request, Application $app, $report_id)
    {

        list($base_path, $report_config) = $this->getConfiguration();

        if (isset($report_config[$report_id])) {
            return $app->sendFile($base_path . '/' . $report_config[$report_id]['thumbnail']);
        }

        throw new NotFoundHttpException('Report does not exist');
    }

    /**
     * Get the Custom Report configuration file.
     */
    private function getConfiguration()
    {
      $base_path = \xd_utilities\getConfiguration('custom_reports', 'base_path');


        $report_config_str = file_get_contents($base_path . '/custom_reports.json');
        $report_config = json_decode($report_config_str, true);

        return array($base_path, $report_config);
    }
}
