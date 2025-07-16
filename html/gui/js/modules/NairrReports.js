/**
 * NAIRR Reports Module for XDMoD Portal
 * @author Alex Tovar
 * @date 2025-07-14

 *
 * This module displays NAIRR reports fetched from the `/custom_reports/reports` endpoint.
 * - It creates a main panel area containing thumbnails and metadata for each report.
 * - Each report displays its title, version, description, and a download link.
 * - The module is integrated into XDMoD's main tab panel and can be activated programmatically.
 *
 * Usage and Setup:
 * - The module ID is "nairr_reports". To display this tab, activate it via the main_tab_panel.
 * - The reports list is loaded from the `/custom_reports/reports` endpoint using a JsonStore.
 * - Each report's thumbnail and download link are constructed based on the report's name.
 * - Toolbar options include: duration selector, print button, and report checkbox (export menu is disabled).
 *
 * Public API:
 * - setConfig(config, name): Activates the "nairr_reports" tab in the main_tab_panel.
 * - initComponent(): Initializes the UI and data fetching logic for the module.
 *
 */
// ===========================================================================
XDMoD.Module.NairrReports = function (config) {
  XDMoD.Module.NairrReports.superclass.constructor.call(this, config);
};

Ext.apply(XDMoD.Module.NairrReports, {
  setConfig: function (config, name) {
    var tabPanel = Ext.getCmp("main_tab_panel");

    tabPanel.setActiveTab("nairr_reports");
  }, // setConfig()
}); //

Ext.extend(XDMoD.Module.NairrReports, XDMoD.PortalModule, {
  module_id: "nairr_reports", // <-- rename this (see the section on REPORT CHECKBOX for how to name this)

  charStore: false,

  initComponent: function () {
    // ------------------------------------------------------------------

    var mainArea = new Ext.Panel({
      title: "NAIRR Reports",
      region: "center",
      items: [
        new Ext.DataView({
          store: new Ext.data.JsonStore({
            autoDestroy: true,
            autoLoad: true,
            url: XDMoD.REST.prependPathBase("/custom_reports/reports"),
            storeId: "customReportStore",
            root: "report_list",
            idProperty: "name",
            fields: ["name", "version", "title", "description"],
          }),
          tpl: new Ext.XTemplate(
            '<tpl for=".">',
            '<div class="custom-report-thumb-wrap" id="{name}">',
            '  <div class="custom-report-thumb"><img src="' +
              XDMoD.REST.prependPathBase("/custom_reports/thumbnail/") +
              '{name}" title="{name}"></div>',
            '  <div class="custom-report-thumb-desc"><h2 class="custom-report-thumb-title">{title}</h2><p>Version: {version}</p><p>{description}</p>',
            '   <div style="text-align: center;"><p><a href="' +
              XDMoD.REST.prependPathBase("/custom_reports/report/") +
              '{name}" name="{name}">Download</a></div>',
            "  </div>",
            "</div>",
            "</tpl>",
            '<div class="x-clear"></div>',
          ),
          emptyText: "No reports available.",
        }),
      ],
    }); //mainArea

    Ext.apply(this, {
      items: [mainArea],
    });

    XDMoD.Module.NairrReports.superclass.initComponent.apply(this, arguments);
  }, //initComponent
}); //XDMoD.Module.NewModule
