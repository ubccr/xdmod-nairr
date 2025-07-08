/*
 * Template / Skeleton for XDMoD Portal Modules
 *
 * To Use:
 *
 * 1) Copy this file and name it to 'xxxx.js', where 'xxxx' is a meaningful (and valid, ProperCased) name which describes this module
 *
 * 2) Replace occurrences of 'XDMoD.Module.NewModule' with 'XDMoD.Module.xxxx' (using the name you decided on above).
 *
 * 3) Update the value of 'title'
 *
 * 4) Update the value of module_id (see the section on REPORT CHECKBOX for how to name this)
 *
 * 5) Reference this module in the necessary web document as follows:
 *
 *       <script type="text/javascript" src="gui/js/modules/xxxx.js"></script>
 *
 *     NOTE: if your portal module requires the reportCheckbox, you will need the following references (the order IS important):
 *
 *        <script type="text/javascript" src="gui/js/report_builder/ChartDateEditor.js"></script>
 *        <script type="text/javascript" src="gui/js/report_builder/Reporting.js"></script>
 *        <script type="text/javascript" src="gui/js/modules/xxxx.js"></script>
 *
 *
 * 6) The module can now be referenced as follows:
 *       var myModule = new XDMoD.Module.xxxx();
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

  usesToolbar: true,

  toolbarItems: {
    durationSelector: true,
    exportMenu: false,
    printButton: true,
    reportCheckbox: true,
  }, //
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
