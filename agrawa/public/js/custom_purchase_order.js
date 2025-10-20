frappe.ui.form.on("Purchase Order", {
    onload(frm) {
        if (frm.doc.items && frm.doc.items.length > 0) {
            let has_sales_order = frm.doc.items.some(row => row.sales_order);
            if (has_sales_order) {
                let allowed_tax_accounts = [
                    "1406 - Abziehbare Vorsteuer 19 % - AW",
                    "1401 - Abziehbare Vorsteuer 7 % - AW"
                ];

                frm.clear_table("taxes");

                if (frm.doc.__last_taxes) {
                    frm.doc.__last_taxes.forEach(tax => {
                        if (allowed_tax_accounts.includes(tax.account_head)) {
                            frm.add_child("taxes", {
                                account_head: tax.account_head,
                                rate: tax.rate,
                                description: tax.description,
                                included_in_print_rate: tax.included_in_print_rate,
                            });
                        }
                    });
                }

                frm.refresh_field("taxes");
            }
        }
    },
    before_save(frm) {
        if (!frm.doc.__last_taxes) {
            frm.doc.__last_taxes = frm.doc.taxes.map(t => ({...t}));
        }
    }
});
