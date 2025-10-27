frappe.ui.form.on('Customer', {
    custom_country_code: function(frm) {
        if (frm.doc.custom_country_code && frm.doc.custom_country_code != 1) {
            frm.set_value('custom_state_code', '0');
        }
    },
    setup(frm) {
        frm.set_query("custom_distance_range_code", () => {
				return {
					query: "agrawa.api.distance_range_code_query"
				};
		});
    }
});
