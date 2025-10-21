import frappe
from frappe.model.mapper import get_mapped_doc

@frappe.whitelist()
def create_sales_invoice_from_purchase_invoice(source_name, target_doc=None):
	def postprocess(source, target):
		target.posting_date = source.posting_date
		target.due_date = source.due_date
		target.custom_delivery_date = source.custom_supplier_delivery_date
		target.custom_purchase_invoice = source.name
		target.taxes_and_charges = None
		target.taxes = []

		customer = None
		for item in source.items:
			if item.purchase_order:
				customer = frappe.db.get_value("Purchase Order", item.purchase_order, "customer")
				if customer:
					break

		target.customer = customer

		if target.customer:
			target.customer_address = frappe.db.get_value(
				"Dynamic Link",
				{"parenttype": "Address", "link_doctype": "Customer", "link_name": target.customer},
				"parent"
			)

			target.contact_person = frappe.db.get_value(
				"Dynamic Link",
				{"parenttype": "Contact", "link_doctype": "Customer", "link_name": target.customer},
				"parent"
			)

	field_map = {
		"Purchase Invoice": {
			"doctype": "Sales Invoice",
			"field_map": {
				"posting_date": "posting_date",
				"remarks": "remarks"
			}
		},
		"Purchase Invoice Item": {
			"doctype": "Sales Invoice Item",
			"field_map": {
				"purchase_order": "purchase_order",
				"po_detail": "purchase_order_item",
			}
		}
	}

	doc = get_mapped_doc(
		"Purchase Invoice",
		source_name,
		field_map,
		target_doc,
		postprocess
	)

	doc.set_missing_values()

	return doc


# @frappe.whitelist()
# def check_qualification_card_required(item_code, customer):
# 	if not item_code or not customer:
# 		return False

# 	item_data = frappe.db.get_value('Item', item_code, 'custom_is_qualification_card_required', as_dict=True)
# 	if item_data and item_data.custom_is_qualification_card_required:
# 		customer_data = frappe.db.get_value('Customer', customer, 'custom_is_qualification_card_available', as_dict=True)
# 		if customer_data and not customer_data.custom_is_qualification_card_available:
# 			return True

# 	return False
