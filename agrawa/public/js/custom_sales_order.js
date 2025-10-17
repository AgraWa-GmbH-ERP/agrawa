frappe.provide("agrawa.sales_utils");

frappe.ui.form.on('Sales Order', {
    onload: function(frm) {
        set_suppliers_for_all_items(frm);
    },
    refresh: function(frm) {
        set_suppliers_for_all_items(frm);
    }
});
frappe.ui.form.on('Sales Order Item', {
    item_code(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.item_code && !row.supplier) {
            frappe.db.get_doc('Item', row.item_code).then(doc => {
                if (doc.supplier_items && doc.supplier_items.length > 0) {
                    let first_supplier = doc.supplier_items[0].supplier;
                    frappe.model.set_value(cdt, cdn, 'supplier', first_supplier);
                    frappe.model.set_value(cdt, cdn, 'delivered_by_supplier', 1);
                }
            });
        }
        if (!row.item_code || !frm.doc.customer) return;
            agrawa.sales_utils.show_qualification_dialog(frm, cdn, row.item_code, frm.doc.customer);
    }
});

function set_suppliers_for_all_items(frm) {
    if (frm.doc.items && frm.doc.items.length > 0) {
        frm.doc.items.forEach(row => {
            if (row.item_code && !row.supplier) {
                frappe.db.get_doc('Item', row.item_code).then(doc => {
                    if (doc.supplier_items && doc.supplier_items.length > 0) {
                        let first_supplier = doc.supplier_items[0].supplier;
                        frappe.model.set_value(row.doctype, row.name, 'supplier', first_supplier);
                        frappe.model.set_value(row.doctype, row.name, 'delivered_by_supplier', 1);
                    }
                });
            }
        });
    }
}

