(() => {
  // ../agrawa/agrawa/public/js/sales_utils.js
  frappe.provide("agrawa.sales_utils");
  agrawa.sales_utils = {
    show_qualification_dialog(frm, cdn, item_code, customer) {
      frappe.call({
        method: "agrawa.api.check_qualification_card_required",
        args: {
          item_code,
          customer
        },
        callback: function(r) {
          if (r.message) {
            let d = new frappe.ui.Dialog({
              title: __("Qualification Card Required"),
              indicator: "red",
              fields: [{
                fieldtype: "HTML",
                options: __("This product requires a qualification card. The customer currently has no qualification card registered. Please verify before continuing.")
              }],
              primary_action_label: __("Proceed Anyway"),
              primary_action: () => {
                d.hide();
                frappe.show_alert({
                  message: __("Proceeding without qualification card verification"),
                  indicator: "orange"
                }, 3);
              },
              secondary_action_label: __("Cancel"),
              secondary_action: () => {
                frm.get_field("items").grid.grid_rows_by_docname[cdn].remove();
                d.hide();
              }
            });
            d.show();
          }
        }
      });
    }
  };
})();
//# sourceMappingURL=agrawa.bundle.DMSVKXCL.js.map
