# Copyright (c) 2026, Agrawa and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint
from frappe.model.document import Document
from frappe.utils import flt, get_link_to_form
from frappe.query_builder import DocType
from frappe.query_builder.functions import Sum


class CollectiveSalesOrder(Document):
	def validate(self):
		"""Validate the Collective Sales Order before saving."""
		self.validate_sales_orders()
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
				SalesOrderItem = DocType('Sales Order Item')
				total_qty_result = (
					frappe.qb.from_(SalesOrderItem)
					.select(Sum(SalesOrderItem.qty).as_('total_qty'))
					.where(SalesOrderItem.parent.isin(so_list))
				).run(as_dict=True)
				
				if total_qty_result and total_qty_result[0]['total_qty']:
					self.total_qty = flt(total_qty_result[0]['total_qty'])


def get_pending_invoices_for_sales_orders(cso_doc):
	"""Get sales invoices that are created from the sales orders in this batch but not yet added to invoice_items."""
	if not cso_doc.sales_orders:
		return []
	
	so_list = [d.sales_order for d in cso_doc.sales_orders if d.sales_order]
	if not so_list:
		return []
		
	# Get existing invoice items to avoid duplicates
	existing_invoices = [d.sales_invoice for d in cso_doc.invoice_items if d.sales_invoice] if cso_doc.invoice_items else []
	
	# Build query using query builder
	SalesInvoice = DocType('Sales Invoice')
	SalesInvoiceItem = DocType('Sales Invoice Item')
	
	query = (
		frappe.qb.from_(SalesInvoice)
		.inner_join(SalesInvoiceItem).on(SalesInvoice.name == SalesInvoiceItem.parent)
		.select(
			SalesInvoice.name.as_('sales_invoice'),
			SalesInvoice.customer,
			SalesInvoice.customer_name,
			SalesInvoice.posting_date,
			SalesInvoice.status,
			SalesInvoice.grand_total,
			SalesInvoice.outstanding_amount,
			SalesInvoiceItem.sales_order
		)
		.where(SalesInvoiceItem.sales_order.isin(so_list))
		.where(SalesInvoice.docstatus == 1)
		.distinct()
		.orderby(SalesInvoice.posting_date, order=frappe.qb.desc)
	)
	
	# Add filter for existing invoices if any
	if existing_invoices:
		query = query.where(SalesInvoice.name.notin(existing_invoices))
		
	return query.run(as_dict=True)


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
def create_purchase_order(cso_name, customer=None):

	cso_doc = frappe.get_doc("Collective Sales Order", cso_name)
	
	# Save customer if provided
	if customer:
		cso_doc.customer = customer
		cso_doc.save(ignore_permissions=True)
	
	# Create Purchase Order
	po_doc = frappe.new_doc("Purchase Order")
	po_doc.supplier = cso_doc.supplier
	po_doc.company = cso_doc.company
	po_doc.transaction_date = cso_doc.batch_date
	po_doc.schedule_date = cso_doc.batch_date

	# Add all items from all sales orders
	has_drop_ship_items = False
	for so_row in cso_doc.sales_orders:
		so_items = frappe.get_all(
			"Sales Order Item",
			filters={"parent": so_row.sales_order, "docstatus": 1},
			fields=["item_code", "item_name", "description", "qty", "uom", "rate", "warehouse", "name", "delivered_by_supplier"]
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
				"sales_order_item": item.name,
				"delivered_by_supplier": item.delivered_by_supplier
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
		"status": ["in", ["To Deliver", "To Deliver and Bill"]]
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
