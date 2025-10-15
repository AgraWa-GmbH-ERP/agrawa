frappe.ui.form.on('Customer', {
    custom_country_code: function(frm) {
        if (frm.doc.custom_country_code && frm.doc.custom_country_code != 1) {
            frm.set_value('custom_state_code', '0');
        }
    }
});
