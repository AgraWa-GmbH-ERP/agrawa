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
		allocations = [frappe._dict(allocation) for allocation in allocations]


	for allocation in allocations:
		del allocation["name"]
	
	so_doc = frappe.get_doc('Sales Order', sales_order)	
	so_doc.custom_item_allocation = []

	for allocation in allocations:
		si = frappe.new_doc("Sales Invoice")
		si.customer = allocation["customer"]
		si.posting_date = frappe.utils.today()
		si.set_posting_time = 0
		
		si.company = so_doc.company
		si.currency = so_doc.currency
		si.conversion_rate = so_doc.conversion_rate
		si.selling_price_list = so_doc.selling_price_list
		si.price_list_currency = so_doc.price_list_currency
		si.plc_conversion_rate = so_doc.plc_conversion_rate
		si.ignore_pricing_rule = so_doc.ignore_pricing_rule

		if allocation["customer"] == so_doc.customer:
			si.customer_address = so_doc.customer_address
			si.contact_person = so_doc.contact_person
			si.shipping_address_name = so_doc.shipping_address_name
		si.append("items", {
			"item_code": allocation.item_code,
			"item_name": allocation.item_name,
			"description": allocation.description,
			"qty": allocation.allocated_qty,
			"uom": allocation.uom,
			"stock_uom": allocation.stock_uom,
			"conversion_factor": allocation.conversion_factor,
			"rate": allocation.rate,
			"amount": allocation.amount,
			"warehouse": allocation.warehouse
		})

		si.save()
		si.submit()

		allocation["sales_invoice"] = si.name
		
		so_doc.append('custom_item_allocation', allocation)

	so_doc.save()

	return {"sales_order": sales_order, "allocations_added": len(allocations)}