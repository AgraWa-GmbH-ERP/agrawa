import json
from frappe.model.mapper import get_mapped_doc
from erpnext.buying.doctype.purchase_order.purchase_order import set_missing_values
from erpnext.accounts.party import get_party_account
from erpnext.setup.doctype.item_group.item_group import get_item_group_defaults
from erpnext.stock.doctype.item.item import get_item_defaults
from frappe import flt
import frappe
from frappe.model.naming import make_autoname
from datetime import datetime
from erpnext.buying.doctype.purchase_order.purchase_order import PurchaseOrder

class CustomPurchaseOrder(PurchaseOrder):
    def autoname(self):
        # Get first 4 letters of supplier name (uppercase)
        prefix = (self.supplier_name[:4].upper() if self.supplier_name else "SUPP")
        year = datetime.now().year

        # Naming pattern e.g. SUPP-2025-.#####
        naming_pattern = f"{prefix}-{year}-.####"

        # Generate name
        self.name = make_autoname(naming_pattern)


@frappe.whitelist()
def make_purchase_invoice(source_name, target_doc=None, args=None):
	return get_mapped_purchase_invoice(source_name, target_doc, args=args)


def get_mapped_purchase_invoice(source_name, target_doc=None, ignore_permissions=False, args=None):
	if args is None:
		args = {}
	if isinstance(args, str):
		args = json.loads(args)

	def postprocess(source, target):
		target.flags.ignore_permissions = ignore_permissions
		set_missing_values(source, target)

		# set tax_withholding_category from Purchase Order
		if source.apply_tds and source.tax_withholding_category and target.apply_tds:
			target.tax_withholding_category = source.tax_withholding_category

		# Get the advance paid Journal Entries in Purchase Invoice Advance
		if target.get("allocate_advances_automatically"):
			target.set_advances()

		target.set_payment_schedule()
		target.credit_to = get_party_account("Supplier", source.supplier, source.company)

	def update_item(obj, target, source_parent):
		def get_billed_qty(po_item_name):
			from frappe.query_builder.functions import Sum

			table = frappe.qb.DocType("Purchase Invoice Item")
			query = (
				frappe.qb.from_(table)
				.select(Sum(table.qty).as_("qty"))
				.where((table.docstatus == 1) & (table.po_detail == po_item_name))
			)
			return query.run(pluck="qty")[0] or 0

		billed_qty = flt(get_billed_qty(obj.name))
		target.qty = flt(obj.qty) - billed_qty

		item = get_item_defaults(target.item_code, source_parent.company)
		item_group = get_item_group_defaults(target.item_code, source_parent.company)
		target.cost_center = (
			obj.cost_center
			or frappe.db.get_value("Project", obj.project, "cost_center")
			or item.get("buying_cost_center")
			or item_group.get("buying_cost_center")
		)

	def select_item(d):
		filtered_items = args.get("filtered_children", [])
		child_filter = d.name in filtered_items if filtered_items else True
		return child_filter

	fields = {
		"Purchase Order": {
			"doctype": "Purchase Invoice",
			"field_map": {
				"party_account_currency": "party_account_currency",
				"supplier_warehouse": "supplier_warehouse",
			},
			"field_no_map": ["payment_terms_template"],
			"validation": {
				"docstatus": ["=", 1],
			},
		},
		"Purchase Order Item": {
			"doctype": "Purchase Invoice Item",
			"field_map": {
				"name": "po_detail",
				"parent": "purchase_order",
				"sales_order": "custom_sales_order", # this line is modified 
				"material_request": "material_request",
				"material_request_item": "material_request_item",
				"wip_composite_asset": "wip_composite_asset",
			},
			"postprocess": update_item,
			"condition": lambda doc: (doc.base_amount == 0 or abs(doc.billed_amt) < abs(doc.amount))
			and select_item(doc),
		},
		"Purchase Taxes and Charges": {"doctype": "Purchase Taxes and Charges", "reset_value": True},
	}

	doc = get_mapped_doc(
		"Purchase Order",
		source_name,
		fields,
		target_doc,
		postprocess,
		ignore_permissions=ignore_permissions,
	)

	return doc
