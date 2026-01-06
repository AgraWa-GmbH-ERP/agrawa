import json
import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.contacts.doctype.address.address import get_company_address
from frappe.model.utils import get_fetch_values
from erpnext.accounts.party import get_party_account
from agrawa.overrides.custom_sales_order import validate_allocation_quantities


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

	for allocation in allocations:
		# Create Sales Invoice using get_mapped_doc
		si = create_sales_invoice_from_allocation(so_doc, allocation)
		
		allocation["sales_invoice"] = si.name
		so_doc.append('custom_item_allocation', allocation)

	validate_allocation_quantities(so_doc)
	so_doc.save()

	return {"sales_order": sales_order, "allocations_added": len(allocations)}


def create_sales_invoice_from_allocation(so_doc, allocation):
	"""Create Sales Invoice from Sales Order using get_mapped_doc"""
	
	def postprocess(source, target):
		set_missing_values(source, target, allocation)
		
	def set_missing_values(source, target, allocation):
		# Override customer from allocation
		target.customer = allocation["customer"]
		target.posting_date = frappe.utils.today()
		target.set_posting_time = 0
		
		target.flags.ignore_permissions = True
		target.run_method("set_missing_values")
		target.run_method("set_po_nos")
		target.run_method("calculate_taxes_and_totals")
		target.run_method("set_use_serial_batch_fields")

		if allocation["customer"] == source.customer:
			if source.customer_address:
				target.customer_address = source.customer_address
			if source.contact_person:
				target.contact_person = source.contact_person
			if source.shipping_address_name:
				target.shipping_address_name = source.shipping_address_name
		
		if source.company_address:
			target.update({"company_address": source.company_address})
		else:
			target.update(get_company_address(target.company))

		if target.company_address:
			target.update(get_fetch_values("Sales Invoice", "company_address", target.company_address))

		target.debit_to = get_party_account("Customer", target.customer, source.company)

	def update_item(source, target, source_parent):
		# Set item details from allocation
		target.qty = allocation.allocated_qty
		target.rate = allocation.rate
		target.amount = allocation.amount
		target.warehouse = allocation.warehouse
		
		if source_parent.project:
			target.cost_center = frappe.db.get_value("Project", source_parent.project, "cost_center")

	def should_map_item(source_item):
		# Only map the specific item from the allocation
		return source_item.item_code == allocation.item_code

	si = get_mapped_doc(
		"Sales Order",
		so_doc.name,
		{
			"Sales Order": {
				"doctype": "Sales Invoice",
				"field_map": {
					"party_account_currency": "party_account_currency",
					"payment_terms_template": "payment_terms_template",
				},
				"field_no_map": ["payment_terms_template", "customer_address", "shipping_address_name", "address_display", "shipping_address"],
				"validation": {"docstatus": ["=", 1]},
			},
			"Sales Order Item": {
				"doctype": "Sales Invoice Item",
				"postprocess": update_item,
				"condition": lambda doc: should_map_item(doc),
			},
			"Sales Taxes and Charges": {
				"doctype": "Sales Taxes and Charges",
				"reset_value": True,
			},
			"Sales Team": {
				"doctype": "Sales Team", 
				"add_if_empty": True
			},
		},
		None,
		postprocess,
		ignore_permissions=True,
	)
	
	si.save()
	si.submit()
	
	return si
