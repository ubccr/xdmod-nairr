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
 * - Toolbar is currently disabled.
 *
 * Public API:
 * - setConfig(config, name): Activates the "nairr_reports" tab in the main_tab_panel.
 * - initComponent(): Initializes the UI and data fetching logic for the module.
 *
 */
// ===========================================================================
//

function getCustomReportQueryString() {
  var params = new URLSearchParams(window.location.search);
  var year = params.get("year");
  var month = params.get("month");
  var out = [];
  if (year) out.push("year=" + encodeURIComponent(year));
  if (month) out.push("month=" + encodeURIComponent(month));
  return out.length ? "?" + out.join("&") : "";
}

function buildReportUrl(year, month) {
  return XDMoD.REST.prependPathBase(
    "/custom_reports/reports?year=" +
      encodeURIComponent(year) +
      "&month=" +
      encodeURIComponent(month),
  );
}

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
  usesToolbar: false,
  reloadReports: function (year, month) {
    var store = Ext.StoreMgr.get("customReportStore");
    if (store) {
      // Dynamically update proxy URL
      store.proxy.conn.url = buildReportUrl(year, month);
      store.load();

      var mainPanel = Ext.getCmp("nairr_reports_main_panel");
      if (mainPanel) {
        mainPanel.setTitle("NAIRR Reports for " + month + " " + year);
      }
    }
  },

  initComponent: function () {
    // ------------------------------------------------------------------

    var now = new Date();
    var params = new URLSearchParams(window.location.search);

    var defaultYear = params.get("year") ?? now.getFullYear();
    var defaultMonth =
      params.get("month") ?? now.toLocaleString("default", { month: "long" });
    var initialUrl = buildReportUrl(defaultYear, defaultMonth);
    var mainArea = new Ext.Panel({
      id: "nairr_reports_main_panel",
      title: "NAIRR Reports for " + defaultMonth + " " + defaultYear,
      region: "center",
      items: [
        new Ext.DataView({
          id: "customReportDataView",
          store: new Ext.data.JsonStore({
            autoDestroy: true,
            autoLoad: true,
            storeId: "customReportStore",
            root: "report_list",
            idProperty: "name",
            fields: ["name", "version", "title", "description", "timestamp"],
            proxy: new Ext.data.HttpProxy({
              url: initialUrl,
              method: "GET",
            }),
          }),
          tpl: new Ext.XTemplate(
            '<tpl for=".">',
            '<div class="custom-report-thumb-wrap" id="{name}">',
            '  <div class="custom-report-thumb"><img src="' +
              XDMoD.REST.prependPathBase("/custom_reports/thumbnail/") +
              '{name}{[this.getQueryString()]}" title="{name}"></div>',
            '  <div class="custom-report-thumb-desc"><h2 class="custom-report-thumb-title">{title}</h2><p>Version: {version}</p><p>{description}</p><p>Created At {timestamp}</p>',
            '   <div style="text-align: center;"><p><a href="' +
              XDMoD.REST.prependPathBase("/custom_reports/report/") +
              '{name}{[this.getQueryString()]}" name="{name}">Download</a></div>',
            "  </div>",
            "</div>",
            "</tpl>",
            '<div class="x-clear"></div>',
            {
              getQueryString: getCustomReportQueryString,
            },
          ),
          emptyText: "No reports available.",
        }),
      ],
    }); //mainArea

    // ------------------------------------------------------------------

    var leftPanel = new Ext.tree.TreePanel({
      region: "west",
      width: 200,
      collapsible: true,
      title: "Report Directory",
      rootVisible: false,
      loader: new Ext.tree.TreeLoader({
        dataUrl: XDMoD.REST.prependPathBase("/custom_reports/report-directory"),
        requestMethod: "GET", // No dynamic loading
      }),
      root: new Ext.tree.AsyncTreeNode({
        text: "Reports",
        expanded: true,
      }),
      listeners: {
        click: function (node, e) {
          if (node.isLeaf()) {
            var year = node.parentNode.text;
            var month = node.text;
            var newUrl = new URL(window.location.href);
            newUrl.searchParams.set("year", year);
            newUrl.searchParams.set("month", month);
            window.history.replaceState({}, "", newUrl.toString());
            XDMoD.Module.NairrReports.prototype.reloadReports(year, month);
          }
        },
      },
    });

    Ext.apply(this, {
      layout: "border",
      items: [leftPanel, mainArea],
    });

    XDMoD.Module.NairrReports.superclass.initComponent.apply(this, arguments);
  }, //initComponent
}); //XDMoD.Module.NewModule
