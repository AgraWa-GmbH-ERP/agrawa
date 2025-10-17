frappe.provide("agrawa.sales_utils");

frappe.ui.form.on('Quotation Item', {
	item_code: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (frm.doc.quotation_to !== "Customer") return;
		if (!row.item_code || !frm.doc.party_name) return;
		
		agrawa.sales_utils.show_qualification_dialog(frm, cdn, row.item_code, frm.doc.party_name);
	}	
});
