import frappe

def set_dropshipping_data(doc, method):
    for item in doc.items:
        item_doc = frappe.get_doc("Item", item.item_code)
        if not item.supplier and item_doc.delivered_by_supplier:
            item.update({
                "delivered_by_supplier": item_doc.delivered_by_supplier,
                "supplier": item_doc.supplier_items[0].supplier if len(item_doc.supplier_items) > 0 else None
            })