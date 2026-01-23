frappe.provide("agrawa.sales_utils");

frappe.ui.form.on("Sales Invoice", {
  refresh(frm) {
    if (frm.is_new() || frm.doc.docstatus === 0) {
      add_purchase_invoice_to_get_items_from(frm);
    }
  },
});

function add_purchase_invoice_to_get_items_from(frm) {
  frm.add_custom_button(
    __("Purchase Invoice"),
    () => {
      	agrawa.erpnext_utils.map_current_doc({
					method: "agrawa.overrides.custom_purchase_invoice.make_sales_invoice_from_purchase_invoice",
					source_doctype: "Purchase Invoice",
					target: frm,
					setters: {
						supplier: undefined,
					},
					get_query_filters: {
						docstatus: 1,
						// status: ["not in", ["Closed", "On Hold"]],
						is_return: 0,
						company: frm.doc.company,
					},
					allow_child_item_selection: true,
					child_fieldname: "items",
					child_columns: ["item_code", "item_name", "qty", "rate", "amount"],
					callback: async function() {
						(frm.doc.items || []).forEach(row => {
							if (!row.item_code) return;
							agrawa.bio_faktii.apply_bio_faktii_marker_to_row(frm, row.doctype, row.name);
						});
						agrawa.bio_faktii.update_terms_field(frm);
					},
				});
			},
	__("Get Items From")
  );
}

frappe.ui.form.on('Sales Invoice Item', {
	item_code: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		
		if (!row.item_code || !frm.doc.customer) return;
		
		agrawa.sales_utils.show_qualification_dialog(frm, cdn, row.item_code, frm.doc.customer);
	}	
});
