# Copyright (c) 2026, Agrawa and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint
from frappe.model.document import Document
from frappe.utils import flt, get_link_to_form


class CollectiveSalesOrder(Document):
	def validate(self):
		"""Validate the Collective Sales Order before saving."""
		self.validate_sales_orders()
		# self.validate_duplicate_sales_orders()
		self.calculate_totals()
		self.validate_invoice_items()

	def validate_invoice_items(self):
		"""Validate invoice items to ensure they belong to the sales orders in this batch."""
		if self.invoice_items:
			so_list = [d.sales_order for d in self.sales_orders if d.sales_order]
			for row in self.invoice_items:
				if row.sales_order and row.sales_order not in so_list:
					frappe.throw(
						_("Row #{0}: Sales Order {1} in invoice items is not part of this collective order").format(
							row.idx, frappe.bold(row.sales_order)
						)
					)

	def validate_sales_orders(self):
		"""Validate that sales orders exist and are in valid state."""
		if not self.sales_orders:
			frappe.throw(_("Please add at least one Sales Order"))

		for row in self.sales_orders:
			if not row.sales_order:
				frappe.throw(_("Row #{0}: Sales Order is mandatory").format(row.idx))

			# Check if Sales Order exists and is submitted
			so_status = frappe.db.get_value(
				"Sales Order",
				row.sales_order,
				["docstatus", "status"],
				as_dict=True
			)

			if not so_status:
				frappe.throw(
					_("Row #{0}: Sales Order {1} does not exist").format(
						row.idx, frappe.bold(row.sales_order)
					)
				)

			if so_status.docstatus != 1:
				frappe.throw(
					_("Row #{0}: Sales Order {1} must be submitted").format(
						row.idx, frappe.bold(row.sales_order)
					)
				)

			if so_status.status in ["Closed", "Cancelled"]:
				frappe.throw(
					_("Row #{0}: Sales Order {1} is {2}").format(
						row.idx, frappe.bold(row.sales_order), so_status.status
					)
				)

			# sales order should not be linked to another collective sales order
			existing_cso = frappe.db.get_value(
				"Order Batch Item",
				{"sales_order": row.sales_order, "parent": ["!=", self.name]},
				"parent"
			)

			if existing_cso:
				frappe.throw(
					_("Row #{0}: Sales Order {1} is already linked to Collective Sales Order {2}").format(
						row.idx,
						frappe.bold(row.sales_order),
						get_link_to_form("Collective Sales Order", existing_cso)
					)
				)
			
	def validate_duplicate_sales_orders(self):
		"""Check for duplicate sales orders in the table."""
		sales_orders = []
		for row in self.sales_orders:
			if row.sales_order in sales_orders:
				frappe.throw(
					_("Row #{0}: Sales Order {1} is already added").format(
						row.idx, frappe.bold(row.sales_order)
					)
				)
			sales_orders.append(row.sales_order)

		# Check if any sales order is already linked to another Collective Sales Order
		if self.docstatus < 2:  # Only check for non-cancelled documents
			for row in self.sales_orders:
				existing_cso = frappe.db.get_value(
					"Sales Order",
					row.sales_order,
					"custom_collective_sales_order"
				)

				if existing_cso and existing_cso != self.name:
					frappe.throw(
						_("Row #{0}: Sales Order {1} is already linked to Collective Sales Order {2}").format(
							row.idx,
							frappe.bold(row.sales_order),
							get_link_to_form("Collective Sales Order", existing_cso)
						)
					)

	def calculate_totals(self):
		"""Calculate total quantity and amount from all sales orders."""
		self.total_qty = 0
		self.total_amount = 0

		for row in self.sales_orders:
			if row.grand_total:
				self.total_amount += flt(row.grand_total)

		# Get total qty from all SO items
		if self.sales_orders:
			so_list = [d.sales_order for d in self.sales_orders if d.sales_order]
			if so_list:
				total_qty = frappe.db.sql(
					"""
					SELECT SUM(qty) as total_qty
					FROM `tabSales Order Item`
					WHERE parent IN ({})
					""".format(", ".join(["%s"] * len(so_list))),
					tuple(so_list)
				)
				if total_qty and total_qty[0][0]:
					self.total_qty = flt(total_qty[0][0])


def get_pending_invoices_for_sales_orders(cso_doc):
	"""Get sales invoices that are created from the sales orders in this batch but not yet added to invoice_items."""
	if not cso_doc.sales_orders:
		return []
	
	so_list = [d.sales_order for d in cso_doc.sales_orders if d.sales_order]
	if not so_list:
		return []
		
	# Get existing invoice items to avoid duplicates
	existing_invoices = [d.sales_invoice for d in cso_doc.invoice_items if d.sales_invoice] if cso_doc.invoice_items else []
	
	# Query for sales invoices linked to our sales orders
	query = """
		SELECT DISTINCT si.name as sales_invoice, si.customer, si.customer_name, 
			   si.posting_date, si.status, si.grand_total, si.outstanding_amount,
			   sii.sales_order
		FROM `tabSales Invoice` si
		INNER JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
		WHERE sii.sales_order IN ({placeholders})
		AND si.docstatus = 1
		{existing_filter}
		ORDER BY si.posting_date DESC
	""".format(
		placeholders=", ".join(["%s"] * len(so_list)),
		existing_filter="AND si.name NOT IN ({})".format(", ".join(["%s"] * len(existing_invoices))) if existing_invoices else ""
	)
	
	params = so_list
	if existing_invoices:
		params.extend(existing_invoices)
		
	return frappe.db.sql(query, params, as_dict=True)


@frappe.whitelist()
def add_pending_invoices(cso_name):
	"""Add all pending invoices for sales orders in this batch."""
	cso_doc = frappe.get_doc("Collective Sales Order", cso_name)
	pending_invoices = get_pending_invoices_for_sales_orders(cso_doc)
	
	for invoice in pending_invoices:
		cso_doc.append("invoice_items", {
			"sales_order": invoice.sales_order,
			"sales_invoice": invoice.sales_invoice
		})
	
	cso_doc.save()
	
	if pending_invoices:
		frappe.msgprint(
			_("Added {0} pending invoice(s) to the batch").format(len(pending_invoices)),
			alert=True
		)
	else:
		frappe.msgprint(_("No pending invoices found"), alert=True)


@frappe.whitelist()
def create_purchase_order(cso_name):

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

	# Update the current Collective Sales Order with the Purchase Order reference
	cso_doc.purchase_order = po_doc.name
	cso_doc.save(ignore_permissions=True)

	msgprint(
		_("Purchase Order {0} created successfully").format(
			get_link_to_form("Purchase Order", po_doc.name)
		),
		alert=True
	)

	return po_doc.name


@frappe.whitelist()
def get_sales_orders_for_cso(customer=None):
	filters = {
		"docstatus": 1,
		"status": "To Deliver"
	}
	
	if customer:
		filters["customer"] = customer
	
	sales_orders = frappe.get_all(
		"Sales Order",
		filters=filters,
		fields=[
			"name", 
			"customer", 
			"customer_name", 
			"grand_total",
			"transaction_date"
		],
		order_by="transaction_date desc"
	)
	
	result = []
	for so in sales_orders:
		result.append({
			"sales_order": so.name,
			"customer": so.customer,
			"customer_name": so.customer_name,
			"grand_total": so.grand_total
		})
	
	return result
