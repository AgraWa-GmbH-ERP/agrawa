const base = frappe.listview_settings['Purchase Invoice'] || {};
const original_get_indicator = base.get_indicator;

frappe.listview_settings['Purchase Invoice'] = {
	...base, // preserve all other core behaviors

	get_indicator(doc) {
		// custom colors
		const custom_colors = {
			'Billed': 'orange',
			'Paid and Billed': 'green',
		};

		if (custom_colors[doc.status]) {
			return [__(doc.status), custom_colors[doc.status], `status,=,${doc.status}`];
		}

		if (typeof original_get_indicator === 'function') {
			return original_get_indicator(doc);
		}
	},
};