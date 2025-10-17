frappe.provide("agrawa.sales_utils");

frappe.ui.form.on('Sales Order Item', {
    item_code: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        frappe.model.set_value(cdt, cdn, 'delivered_by_supplier', 1);

        if (row.item_code) {
            frappe.db.get_doc('Item', row.item_code).then(doc => {
                if (doc.supplier_items && doc.supplier_items.length > 0) {
                    let first_supplier = doc.supplier_items[0].supplier;
                    frappe.model.set_value(cdt, cdn, 'supplier', first_supplier);
                } else {
                    frappe.msgprint(__('No supplier found in Item Supplier table for this item'));
                }
            });
        }

        if (!row.item_code || !frm.doc.customer) return;
        agrawa.sales_utils.show_qualification_dialog(frm, cdn, row.item_code, frm.doc.customer);
    }
});
