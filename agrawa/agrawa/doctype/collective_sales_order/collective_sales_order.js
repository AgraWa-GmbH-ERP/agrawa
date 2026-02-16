// Copyright (c) 2026, Agrawa and contributors
// For license information, please see license.txt

frappe.ui.form.on('Collective Sales Order', {
	refresh: function(frm) {
		erpnext.hide_company(frm);
		if (!frm.doc.purchase_order) {
			frm.add_custom_button(__('Create Purchase Order'), function() {
				frappe.call({
					method: 'agrawa.agrawa.doctype.collective_sales_order.collective_sales_order.create_purchase_order',
					args: {
						purchase_order: frm.doc.purchase_order,
						cso_name: frm.doc.name
					},
					callback: function(r) {
						if (r.message) {
							frm.reload_doc();
							frappe.set_route('Form', 'Purchase Order', r.message);
						}
					}
				});
			}).addClass('btn-primary');
		}

		// // Color coding for status
		// if (frm.doc.status) {
		// 	const status_colors = {
		// 		'Draft': 'gray',
		// 		'Open': 'blue',
		// 		'PO Created': 'orange',
		// 		'Delivered': 'purple',
		// 		'Partially Invoiced': 'yellow',
		// 		'Completed': 'green',
		// 		'Cancelled': 'red'
		// 	};
		// 	frm.set_indicator_formatter('status', function(doc) {
		// 		return status_colors[doc.status] || 'gray';
		// 	});
		// }
	},
});
