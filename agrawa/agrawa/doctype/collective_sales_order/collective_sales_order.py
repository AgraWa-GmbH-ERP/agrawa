# Copyright (c) 2026, Agrawa and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint
from frappe.model.document import Document
from frappe.utils import flt, get_link_to_form


class CollectiveSalesOrder(Document):
	pass

@frappe.whitelist()
def create_purchase_order(purchase_order, cso_name):
	"""Create a consolidated Purchase Order from all Sales Orders."""
	if purchase_order:
		frappe.throw(
			_("Purchase Order {0} already created").format(
				get_link_to_form("Purchase Order", purchase_order)
			)
		)
	cso_doc = frappe.get_doc("Collective Sales Order", cso_name)
	
	# Create Purchase Order
	po_doc = frappe.new_doc("Purchase Order")
	po_doc.supplier = cso_doc.supplier
	po_doc.company = cso_doc.company
	po_doc.transaction_date = cso_doc.batch_date
	po_doc.schedule_date = cso_doc.batch_date
	po_doc.custom_collective_sales_order = cso_doc.name

	# Add all items from all sales orders
	for so_row in cso_doc.sales_orders:
		so_items = frappe.get_all(
			"Sales Order Item",
			filters={"parent": so_row.sales_order, "docstatus": 1},
			fields=["item_code", "item_name", "description", "qty", "uom", "rate", "warehouse", "name"]
		)

		for item in so_items:
			po_doc.append("items", {
				"item_code": item.item_code,
				"item_name": item.item_name,
				"description": item.description,
				"qty": item.qty,
				"uom": item.uom,
				"rate": item.rate,
				"warehouse": item.warehouse,
				"sales_order": so_row.sales_order,
				"sales_order_item": item.name
			})

	po_doc.insert(ignore_permissions=True)

	# # Link PO back to Collective Sales Order
	# cso_doc.db_set("purchase_order", po_doc.name)
	# cso_doc.db_set("status", "PO Created")

	msgprint(
		_("Purchase Order {0} created successfully").format(
			get_link_to_form("Purchase Order", po_doc.name)
		),
		alert=True
	)

	return po_doc.name
