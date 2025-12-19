import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt
import json

@frappe.whitelist()
def make_purchase_order(source_name, selected_items=None, target_doc=None):
	if not selected_items:
		return

	if isinstance(selected_items, str):
		selected_items = json.loads(selected_items)

	items_to_map = [
		item.get("item_code") for item in selected_items if item.get("item_code")
	]
	items_to_map = list(set(items_to_map))

	def is_drop_ship_order(target):
		for item in target.items:
			if not item.delivered_by_supplier:
				return False
		return True

	def set_missing_values(source, target):
		# Reset unnecessary fields
		target.supplier = ""
		target.apply_discount_on = ""
		target.additional_discount_percentage = 0.0
		target.discount_amount = 0.0
		target.inter_company_order_reference = ""
		target.shipping_rule = ""
		target.tc_name = ""
		target.terms = ""
		target.payment_terms_template = ""
		target.payment_schedule = []

		if is_drop_ship_order(target):
			# ✅ Auto set supplier from first item (or from your logic)
			selected_suppliers = [item.get("supplier") for item in source.items if item.get("item_code") in items_to_map and item.get("supplier")]
			if selected_suppliers:
				target.supplier = selected_suppliers[0]

			# set shipping & customer info
			if source.shipping_address_name:
				target.shipping_address = source.shipping_address_name
				target.shipping_address_display = source.shipping_address
			else:
				target.shipping_address = source.customer_address
				target.shipping_address_display = source.address_display

			target.customer_contact_person = source.contact_person
			target.customer_contact_display = source.contact_display
			target.customer_contact_mobile = source.contact_mobile
			target.customer_contact_email = source.contact_email
		else:
			target.customer = target.customer_name = target.shipping_address = None

		target.run_method("set_missing_values")

		default_ptct = frappe.db.get_value(
			"Purchase Taxes and Charges Template",
			{
				"company": target.company,
				"is_default": 1,
				"disabled": 0,
			},
			"name",
    	)
		
		if default_ptct:
			target.taxes_and_charges = default_ptct
			target.set("taxes", [])

			ptct = frappe.get_doc("Purchase Taxes and Charges Template", default_ptct)

			for t in ptct.taxes:
				target.append("taxes", {
					"charge_type": t.charge_type,
					"account_head": t.account_head,
					"description": t.description,
					"rate": t.rate,
					"tax_amount": 0,
					"tax_amount_after_discount_amount": 0,
					"cost_center": t.cost_center,
					"included_in_print_rate": t.included_in_print_rate,
					"included_in_paid_amount": t.included_in_paid_amount,
					"add_deduct_tax": t.add_deduct_tax,
					"category": t.category,
					"row_id": t.row_id,
				})

		if not target.taxes:
			# target.append_taxes_from_item_tax_template()
			pass
		target.run_method("calculate_taxes_and_totals")

	def update_item(source, target, source_parent):
		target.schedule_date = source.delivery_date
		target.qty = flt(source.qty) - (flt(source.ordered_qty) / flt(source.conversion_factor))
		target.stock_qty = flt(source.stock_qty) - flt(source.ordered_qty)
		target.project = source_parent.project

	def update_item_for_packed_item(source, target, source_parent):
		target.qty = flt(source.qty) - flt(source.ordered_qty)

	doc = get_mapped_doc(
		"Sales Order",
		source_name,
		{
			"Sales Order": {
				"doctype": "Purchase Order",
				"field_no_map": [
					"address_display",
					"contact_display",
					"contact_mobile",
					"contact_email",
					"contact_person",
					"taxes_and_charges",
					"shipping_address",
				],
				"validation": {"docstatus": ["=", 1]},
			},
			"Sales Order Item": {
				"doctype": "Purchase Order Item",
				"field_map": [
					["name", "sales_order_item"],
					["parent", "sales_order"],
					["stock_uom", "stock_uom"],
					["uom", "uom"],
					["conversion_factor", "conversion_factor"],
					["delivery_date", "schedule_date"],
				],
				"field_no_map": [
					"rate",
					"price_list_rate",
					"item_tax_template",
					"discount_percentage",
					"discount_amount",
					"supplier",
					"pricing_rules",
				],
				"postprocess": update_item,
				"condition": lambda doc: doc.ordered_qty < doc.stock_qty
				and doc.item_code in items_to_map
				and not is_product_bundle(doc.item_code),
			},
			"Packed Item": {
				"doctype": "Purchase Order Item",
				"field_map": [
					["name", "sales_order_packed_item"],
					["parent", "sales_order"],
					["uom", "uom"],
					["conversion_factor", "conversion_factor"],
					["parent_item", "product_bundle"],
					["rate", "rate"],
				],
				"field_no_map": [
					"price_list_rate",
					"item_tax_template",
					"discount_percentage",
					"discount_amount",
					"supplier",
					"pricing_rules",
				],
				"postprocess": update_item_for_packed_item,
				"condition": lambda doc: doc.parent_item in items_to_map,
			},
		},
		target_doc,
		set_missing_values,
	)

	set_delivery_date(doc.items, source_name)
	doc.set_onload("load_after_mapping", False)

	return doc


def set_delivery_date(items, sales_order):
	delivery_dates = frappe.get_all(
		"Sales Order Item", filters={"parent": sales_order}, fields=["delivery_date", "item_code"]
	)
	delivery_by_item = frappe._dict()
	for date in delivery_dates:
		delivery_by_item[date.item_code] = date.delivery_date
	for item in items:
		if item.product_bundle:
			item.schedule_date = delivery_by_item[item.product_bundle]


def is_product_bundle(item_code):
	return frappe.db.exists("Product Bundle", {"name": item_code, "disabled": 0})
