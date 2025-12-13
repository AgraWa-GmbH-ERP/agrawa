frappe.provide("agrawa.sales_utils");

frappe.ui.form.on('Sales Order', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 1) {
            let unique_customers = new Set();
            if (frm.doc.items) {
                frm.doc.items.forEach(item => {
                    if (item.custom_customer) {
                        unique_customers.add(item.custom_customer);
                    }
                });
            }
            if (unique_customers.size > 1) {
                frm.add_custom_button(__('Split Invoice'), function() {
                        frappe.call({
                            method: 'agrawa.api.create_split_invoice',
                            args: {
                                sales_order: frm.doc.name
                            },
                            callback: function(response) {
                                if (response.message && response.message.length > 0) {
                                    let invoices = response.message.map(inv => `<a href="/app/sales-invoice/${inv}">${inv}</a>`).join(', ');
                                    frappe.msgprint(__(`Invoices created: ${invoices}`));
                                } else {
                                    frappe.msgprint(__('No invoices were created.'));
                                }
                            }
                    });
                }, __('Create'));

            }
            
        }

    }
});


frappe.ui.form.on('Sales Order Item', {
    item_code: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.item_code) {
            frappe.db.get_doc('Item', row.item_code).then(doc => {
                if (doc.supplier_items && doc.supplier_items.length > 0) {
                    let first_supplier = doc.supplier_items[0].supplier;
                    frappe.model.set_value(cdt, cdn, 'supplier', first_supplier);
                    frappe.model.set_value(cdt, cdn, 'delivered_by_supplier', 1);
                } else {
                    frappe.msgprint(__('No supplier found in Item Supplier table for this item'));
                }
            });
        }

        if (!row.item_code || !frm.doc.customer) return;
        agrawa.sales_utils.show_qualification_dialog(frm, cdn, row.item_code, frm.doc.customer);
    }
});