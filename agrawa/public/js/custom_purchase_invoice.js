frappe.ui.form.on('Purchase Invoice', {
    refresh(frm) {
        frappe.db.get_value("Sales Invoice", {"custom_purchase_invoice": frm.doc.name}, "name")
            .then(r => {
                const si = r.message ? r.message.name : null;
                if (frm.doc.docstatus === 1 && !si) {
                    frm.remove_custom_button(__('Sales Invoice'), __('Create'));
                    frm.add_custom_button(__('Sales Invoice'), () => {
                        frappe.model.open_mapped_doc({
                            method: "agrawa.api.create_sales_invoice_from_purchase_invoice",
                            frm: frm,
                        });
                    }, __('Create'));
                }
            });
    },
});
