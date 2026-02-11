frappe.ui.form.on("Material Request", {
    make_purchase_order(frm) {
        frappe.prompt(
            {
                label: __("Supplier"),
                fieldname: "supplier",
                fieldtype: "Link",
                options: "Supplier",
                reqd: 1,
                get_query: () => ({
                    query: "agrawa.overrides.custom_material_request.get_suppliers_from_item_supplier",
                    filters: { doc: frm.doc.name }
                })
            },
            (values) => {
                frappe.model.open_mapped_doc({
                    method: "agrawa.overrides.custom_material_request.make_purchase_order_item_supplier",
                    frm: frm,
                    args: {
                        supplier: values.supplier
                    }
                });
            },
            __("Create Purchase Order"),
            __("Create")
        );
    }
});