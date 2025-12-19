frappe.provide("agrawa.sales_utils");

frappe.ui.form.on('Sales Order', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Split Invoice'), function() {
                agrawa.sales_utils.split_items_by_customer(frm);
            });
            
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

agrawa.sales_utils.split_items_by_customer = function(frm) {

    // Prepare table data for dialog
    const allocation_data = [];
    frm.doc.items.forEach(item => {
        allocation_data.push({
            item_code: item.item_code,
            item_name: item.item_name,
            allocated_qty: item.qty,
            amount: item.amount,
            so_detail: item.name,
            uom: item.uom,
            stock_uom: item.stock_uom,
            conversion_factor: item.conversion_factor,
            warehouse: item.warehouse,
            rate: item.rate
        });
    });

    // Create dialog similar to update_child_items
    const dialog = new frappe.ui.Dialog({
        title: __('Split Items by Customer'),
        size: 'extra-large',
        fields: [
            {
                fieldname: 'allocation_items',
                fieldtype: 'Table',
                label: __('Item Allocation'),
                cannot_add_rows: false,
                in_place_edit: true,
                data: allocation_data,
                get_data: () => {
                    return allocation_data;
                },
                fields: [
                    {
                        fieldtype: 'Link',
                        fieldname: 'item_code',
                        options: 'Item',
                        in_list_view: 1,
                        read_only: 1,
                        label: __('Item Code')
                    },
                    {
                        fieldtype: 'Data',
                        fieldname: 'item_name',
                        in_list_view: 1,
                        read_only: 1,
                        label: __('Item Name')
                    },
                    {
                        fieldtype: 'Link',
                        fieldname: 'customer',
                        options: 'Customer',
                        in_list_view: 1,
                        read_only: 0,
                        reqd: 1,
                        label: __('Customer')
                    },
                    {
                        fieldtype: 'Int',
                        fieldname: 'allocated_qty',
                        in_list_view: 1,
                        read_only: 0,
                        reqd: 1,
                        label: __('Allocated Qty')
                    },
                    {
                        fieldtype: 'Currency',
                        fieldname: 'amount',
                        in_list_view: 1,
                        read_only: 0,
                        reqd: 1,
                        label: __('Amount')
                    },
                    {
                        fieldtype: 'Data',
                        fieldname: 'so_detail',
                        read_only: 1,
                        label: __('SO Detail'),
                        hidden: 1
                    },
                    {
                        fieldtype: 'Link',
                        fieldname: 'sales_invoice',
                        options: 'Sales Invoice',
                        in_list_view: 1,
                        read_only: 0,
                        label: __('Sales Invoice')
                    }
                ]
            }
        ],
        primary_action: function() {
            const allocations = this.get_values()['allocation_items'];
            const selected_allocations = allocations.filter(allocation => allocation?.__checked == 1 );
            frappe.call({
                method: 'agrawa.api.add_alocations_and_create_invoice',
                args: {
                    sales_order: frm.doc.name,
                    allocations: selected_allocations
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.msgprint(__('Invoices created and allocations added to Sales Order.'));
                        frm.reload_doc();
                        dialog.hide();
                    }
                }
            });
        },
        primary_action_label: __('Allocate and Create Invoices')
    });

    dialog.show();
};