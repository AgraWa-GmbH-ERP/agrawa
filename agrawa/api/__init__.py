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
def create_split_invoice(sales_order):	
	so_doc = frappe.get_doc("Sales Order", sales_order)
	
	# Check if Sales Order is submitted
	if so_doc.docstatus != 1:
		frappe.throw("Sales Order must be submitted to create invoices")
	
	customer_items = {}
	for item in so_doc.items:
		if not item.custom_individual_sales_invoice:
			customer = item.custom_customer
			if customer not in customer_items:
				customer_items[customer] = []
			customer_items[customer].append(item)

	created_invoices = []
	for customer, items in customer_items.items():
		si = frappe.new_doc("Sales Invoice")
		si.customer = customer
		si.posting_date = frappe.utils.today()
		si.set_posting_time = 0
		
		si.company = so_doc.company
		si.currency = so_doc.currency
		si.conversion_rate = so_doc.conversion_rate
		si.selling_price_list = so_doc.selling_price_list
		si.price_list_currency = so_doc.price_list_currency
		si.plc_conversion_rate = so_doc.plc_conversion_rate
		si.ignore_pricing_rule = so_doc.ignore_pricing_rule
		
		if so_doc.taxes_and_charges:
			si.taxes_and_charges = so_doc.taxes_and_charges
			si.set_taxes()

		if customer == so_doc.customer:
			si.customer_address = so_doc.customer_address
			si.contact_person = so_doc.contact_person
			si.shipping_address_name = so_doc.shipping_address_name
		
		for item in items:
			si.append("items", {
				"item_code": item.item_code,
				"item_name": item.item_name,
				"description": item.description,
				"qty": item.qty,
				"uom": item.uom,
				"stock_uom": item.stock_uom,
				"conversion_factor": item.conversion_factor,
				"rate": item.rate,
				"amount": item.amount,
				"warehouse": item.warehouse,
				"custom_collective_sales_order": so_doc.name,
				"custom_collective_so_detail": item.name,
			})
		
		si.set_missing_values()
		si.calculate_taxes_and_totals()
		
		si.save()
		created_invoices.append(si.name)
	
	return created_invoices
