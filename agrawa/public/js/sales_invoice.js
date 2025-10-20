frappe.provide("agrawa.sales_utils");

frappe.ui.form.on('Sales Invoice Item', {
	item_code: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		
		if (!row.item_code || !frm.doc.customer) return;
		
		agrawa.sales_utils.show_qualification_dialog(frm, cdn, row.item_code, frm.doc.customer);
	}	
});
