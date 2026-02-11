
import frappe
from frappe.model.mapper import get_mapped_doc


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_suppliers_from_item_supplier(doctype, txt, searchfield, start, page_len, filters):
	doc = frappe.get_doc("Material Request", filters.get("doc"))

	item_codes = [d.item_code for d in doc.items if d.item_code]

	return frappe.db.sql("""
		SELECT DISTINCT supplier
		FROM `tabItem Supplier`
		WHERE parent IN %(items)s
		AND supplier LIKE %(txt)s
		LIMIT %(start)s, %(page_len)s
	""", {
		"items": tuple(item_codes) or ("",),
		"txt": f"%{txt}%",
		"start": start,
		"page_len": page_len
	})

@frappe.whitelist()
def make_purchase_order_item_supplier(source_name, target_doc=None):

	def postprocess(source, target):
		args = frappe.flags.args or {}
		supplier = args.get("supplier")

		if not supplier:
			frappe.throw("❌ Supplier not Available")

		target.supplier = supplier

		valid_items = []
		for d in target.items:
			item_supplier = frappe.db.get_value(
				"Item Supplier",
				{"parent": d.item_code},
				"supplier"
			)
			if item_supplier == supplier:
				valid_items.append(d)

		if not valid_items:
			frappe.throw(f"No items found for supplier {supplier}")

		target.items = valid_items

	return get_mapped_doc(
		"Material Request",
		source_name,
		{
			"Material Request": {
				"doctype": "Purchase Order",
			},
			"Material Request Item": {
				"doctype": "Purchase Order Item",
				"field_map": {
					"name": "material_request_item",
					"parent": "material_request",
				},
			},
		},
		target_doc,
		postprocess,
	)

