import json
import frappe


@frappe.whitelist()
def check_qualification_card_required(item_code, customer):
	if not item_code or not customer:
		return False

	item_data = frappe.db.get_value('Item', item_code, 'custom_is_qualification_card_required', as_dict=True)
	if item_data and item_data.custom_is_qualification_card_required:
		customer_data = frappe.db.get_value('Customer', customer, 'custom_is_qualification_card_available', as_dict=True)
		if customer_data and not customer_data.custom_is_qualification_card_available:
			return True

	return False


@frappe.whitelist()
def distance_range_code_query(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql("""
        SELECT 
            code as name, distance_range as value
        FROM `tabDistance Range Code`
		WHERE name LIKE %(txt)s
            OR code LIKE %(txt)s
        ORDER BY 
            CAST(code AS UNSIGNED) ASC
        LIMIT %(start)s, %(page_len)s
    """, {
        "txt": f"%{txt}%",
        "start": start,
        "page_len": page_len
    })


@frappe.whitelist()
def add_alocations_and_create_invoice(sales_order, allocations):	
	if isinstance(allocations, str):
		allocations = json.loads(allocations)


	for allocation in allocations:
		del allocation["name"]
		frappe.msgprint(frappe.utils.cstr(allocation))
	
	so_doc = frappe.get_doc('Sales Order', sales_order)

	for allocation in allocations:
		so_doc.append('custom_item_allocation', allocation)
	# frappe.db.commit()
	so_doc.save()

	return {"sales_order": sales_order, "allocations_added": len(allocations)}