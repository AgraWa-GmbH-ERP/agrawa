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
    },
    refresh(frm) {
        frm.trigger("render_custom_items_summary");
    },
    render_custom_items_summary(frm) {
        if (!frm.doc.items || frm.doc.items.length == 0) {
            if (frm.fields_dict["custom_items_summary"]) {
                $(frm.fields_dict["custom_items_summary"].wrapper).html("");
            }
            return;
        }

        frappe.call({
            method: "agrawa.utils.get_merged_so_items_from_po",
            args: {
                items: JSON.stringify(frm.doc.items)
            },
            callback: function(r) {
                if (r.message && r.message.length !== frm.doc.items.length) {
                    let processed_items = r.message;
                    
                    let summary_html = `
                        <table class="table table-bordered">
                            <thead>
                                <tr>
                                    <th>${__("Item Code")}</th>
                                    <th>${__("Quantity")}</th>
                                    <th>${__("UOM")}</th>
                                    <th>${__("Rate")}</th>
                                    <th>${__("Amount")}</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${processed_items.map(item => `
                                    <tr>
                                        <td><a href="/app/item/${item.item_code}"><b>${item.item_code}: ${item.item_name}</b></a></td>
                                        <td style="text-align: right;">${item.qty}</td>
                                        <td>${item.uom}</td>
                                        <td style="text-align: right;">€ ${item.rate}</td>
                                        <td style="text-align: right;">€ ${item.amount}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    `;

                    if (frm.fields_dict["custom_items_summary"]) {
                        $(frm.fields_dict["custom_items_summary"].wrapper).html(summary_html);
                    }
                } else {
                    if (frm.fields_dict["custom_items_summary"]) {
                        $(frm.fields_dict["custom_items_summary"].wrapper).html("");
                    }
                }
            }
        });
    }
});