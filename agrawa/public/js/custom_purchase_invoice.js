frappe.ui.form.on('Purchase Invoice', {
    refresh(frm) {
        if (frm.doc.docstatus === 1) {
            frm.remove_custom_button(__('Sales Invoice'), __('Create'));
            frm.add_custom_button(__('Sales Invoice'), () => {
                frappe.model.open_mapped_doc({
                    method: "agrawa.api.create_sales_invoice_from_purchase_invoice",
                    frm: frm,
                });
            }, __('Create'));
        }
    },
});
