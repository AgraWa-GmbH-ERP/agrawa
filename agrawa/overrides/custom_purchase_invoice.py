import json
import frappe
from frappe.utils import flt, cint
from frappe.model.mapper import get_mapped_doc

@frappe.whitelist()
def make_sales_invoice_from_purchase_invoice(
	source_name,
	target_doc=None,
	ignore_permissions=False,
	args=None
):
	if args is None:
		args = {}
	if isinstance(args, str):
		args = json.loads(args)

	def postprocess(source, target):
		set_missing_values(source, target)

	def set_missing_values(source, target):

		target.flags.ignore_permissions = True
		target.run_method("set_missing_values")

		target.run_method("calculate_taxes_and_totals")
		target.run_method("set_use_serial_batch_fields")


	def update_item(source_row, target_row, source_parent):
		target_row.qty = flt(source_row.qty)
		target_row.custom_purchase_invoice = source_parent.name
		target_row.custom_purchase_invoice_item = source_row.name

	def select_item(d):
		filtered_items = args.get("filtered_children", [])
		return (d.name in filtered_items) if filtered_items else True

	doc = get_mapped_doc(
		"Purchase Invoice",
		source_name,
		{
			"Purchase Invoice": {
				"doctype": "Sales Invoice",
				"validation": {"docstatus": ["=", 1]},
				"field_no_map": [
					"purchase_invoice",
					"taxes_and_charges"
					"address_display",
					"contact_person",
					"contact_display",
					"contact_mobile",
					"contact_email"],
			},
			"Purchase Invoice Item": {
				"doctype": "Sales Invoice Item",
				"field_no_map": [
					"uom",
					"rate",
					"base_rate",
					"price_list_rate",
					"base_price_list_rate",
					"amount",
					"base_amount",
					"net_rate",
					"net_amount",
					"base_net_rate",
					"base_net_amount",
					"discount_percentage",
					"discount_amount",
					"margin_rate_or_amount",
					"margin_type",
    			],
				"postprocess": update_item,
				"condition": lambda doc: (flt(doc.qty) != 0) and select_item(doc),
			},
		},
		target_doc,
		postprocess,
		ignore_permissions=ignore_permissions,
	)

	return doc

