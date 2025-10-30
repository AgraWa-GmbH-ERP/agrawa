frappe.ui.form.on("Print Format", {
	refresh: function (frm) {
		if (frm.doc.standard === "Yes") {
			frm.add_custom_button(__("Duplicate Standard Print Format"), function () {
                frappe.model.open_mapped_doc({
                    method: "agrawa.overrides.custom_print_format.duplicate_standard_print_format",
                    frm: cur_frm,
                });
			});
		}
	},
});