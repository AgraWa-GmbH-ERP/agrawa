import frappe
from frappe.model.mapper import get_mapped_doc

@frappe.whitelist()
def create_sales_invoice_from_purchase_invoice(source_name, target_doc=None):
	def postprocess(source, target):
		target.posting_date = source.posting_date
		target.due_date = source.due_date
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