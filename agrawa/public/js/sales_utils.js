frappe.provide("agrawa.sales_utils");

agrawa.sales_utils = {
	show_qualification_dialog(frm, cdn, item_code, customer) {
		frappe.call({
			method: 'agrawa.api.check_qualification_card_required',
			args: {
				item_code: item_code,
				customer: customer
			},
			callback: function(r) {
				if (r.message) {
					let d = new frappe.ui.Dialog({
						title: 'Qualification Card Required',
						indicator: 'red',
						fields: [{
							fieldtype: 'HTML',
							options: '<p class="text-muted">This product requires a qualification card. The customer currently has no qualification card registered. Please verify before continuing.</p>'
						}],
						primary_action_label: 'Proceed Anyway',
						primary_action: () => {
							d.hide();
							frappe.show_alert({
								message: __('Proceeding without qualification card verification'),
								indicator: 'orange'
							}, 3);
						},
						secondary_action_label: 'Cancel',
						secondary_action: () => {
							frm.get_field('items').grid.grid_rows_by_docname[cdn].remove();
							d.hide();
						}
					});
					d.show();
				}
			}
		});
	},
};