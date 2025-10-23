const BIO_TEXT =
    '* für die ökologische Produktion / Landwirtschaft zugelassen EU-ÖkoVO (EG-VO Nr.: 2018/848)';
const FAKTII_TEXT =
    '** Die Saatgutmischung entspricht hinsichtlich Arten und Mischungsanteilen den Anforderungen der FAKT II-Maßnahme E1.2 "Begrünungsmischungen im Acker-/Gartenbau".';

const CHILD_TABLE_MAP = {
    "Quotation": "Quotation Item",
    "Sales Order": "Sales Order Item",
    "Sales Invoice": "Sales Invoice Item"
};

frappe.ui.form.on(cur_frm.doctype, {
    onload(frm) {
        const parent = frm.doctype;
        const child = CHILD_TABLE_MAP[parent];
        if (!child) return;

        attach_bio_faktii_behavior(parent, child);
    },
    
    tc_name(frm) {
        const current_terms = frm.doc.terms || "";
        const has_bio = current_terms.includes(BIO_TEXT);
        const has_faktii = current_terms.includes(FAKTII_TEXT);

        setTimeout(async () => {
            const { message: tc } = await frappe.db.get_value(
                "Terms and Conditions",
                frm.doc.tc_name,
                ["terms"]
            );
            if (!tc?.terms) return;

            let new_terms = tc.terms.trim();
            if (has_bio) new_terms += `<br>${BIO_TEXT}`;
            if (has_faktii) new_terms += `<br>${FAKTII_TEXT}`;

            await frm.set_value("terms", new_terms);
            frm.refresh_field("terms");
        }, 100);
    },
});


function attach_bio_faktii_behavior(parentDoctype, childDoctype) {
    frappe.ui.form.on(childDoctype, {
        async item_code(frm, cdt, cdn) {
            const row = locals[cdt][cdn];
            if (!row?.item_code) return;

            setTimeout(async () => {
                const { message: item } = await frappe.db.get_value(
                    'Item',
                    row.item_code,
                    ['custom_is_bio', 'custom_is_faktii_e12', 'item_name']
                );
                if (!item) return;

                setTimeout(() => {
                    const clean_name = item.item_name.replace(/\*+$/, '').trim();
                    const new_name = item.custom_is_bio ? `${clean_name} *` : item.custom_is_faktii_e12 ? `${clean_name} **` : clean_name;

                    frappe.model.set_value(cdt, cdn, 'item_name', new_name);
                    frm.fields_dict.items.grid.refresh_row(cdn);

                    update_terms_field(frm);
                }, 250);
            }, 100);
        },

        items_remove(frm) {
            setTimeout(() => update_terms_field(frm), 100);
        }
    });
}

async function update_terms_field(frm) {
    const items = frm.doc.items || [];
    if (!items.length) {
        return await clear_terms_lines(frm, [BIO_TEXT, FAKTII_TEXT]);
    }

    const item_codes = items.map(i => i.item_code);
    const item_data = await frappe.db.get_list('Item', {
        filters: { name: ['in', item_codes] },
        fields: ['custom_is_bio', 'custom_is_faktii_e12']
    });

    const has_bio = item_data.some(i => i.custom_is_bio);
    const has_faktii = item_data.some(i => i.custom_is_faktii_e12);

    let terms = frm.doc.terms || '';
    const split_lines = terms.split(/<br\s*\/?>/i).map(t => t.trim()).filter(Boolean);

    const add_line = line => { if (!split_lines.includes(line)) split_lines.push(line); };
    const remove_line = line => {
        const idx = split_lines.indexOf(line);
        if (idx !== -1) split_lines.splice(idx, 1);
    };

    if (has_bio) add_line(BIO_TEXT); else remove_line(BIO_TEXT);
    if (has_faktii) add_line(FAKTII_TEXT); else remove_line(FAKTII_TEXT);

    terms = split_lines.join('<br>');
    await frm.set_value('terms', terms);
    frm.refresh_field('terms');
}

async function clear_terms_lines(frm, lines) {
    let terms = frm.doc.terms || '';
    let split_lines = terms.split(/<br\s*\/?>/i).map(t => t.trim()).filter(Boolean);
    split_lines = split_lines.filter(line => !lines.includes(line));

    terms = split_lines.join('<br>');
    await frm.set_value('terms', terms);
    frm.refresh_field('terms');
}
