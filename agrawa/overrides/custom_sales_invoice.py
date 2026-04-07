import frappe
from frappe import _
from frappe.query_builder import DocType

def update_purchase_invoice_status_on_billing(si, method):
	pi_name = si.get("custom_purchase_invoice")
	if not pi_name:
		return
	pi = frappe.get_doc("Purchase Invoice", pi_name)
	pi.set_status(update=True)


@frappe.whitelist()
def unset_sales_invoice_on_sales_order_item_allocation(doc, method):
	sales_order_allocations = frappe.db.get_all(
		"Collective Order Allocation",
		filters={"sales_invoice": doc.name},
		fields=["name", "parent"],
	)

	for allocation in sales_order_allocations:
		frappe.db.delete(
			"Collective Order Allocation",
			{"name": allocation.name, "parent": allocation.parent},
		)


def auto_add_sales_invoice_to_collective_order(doc, method):
	# Get all sales orders from the sales invoice items
	sales_orders_in_invoice = [item.sales_order for item in doc.items if item.sales_order]
	
	if not sales_orders_in_invoice:
		return
	
	# Find collective sales orders that contain any of these sales orders
	OrderBatchItem = DocType('Order Batch Item')
	CollectiveSalesOrder = DocType('Collective Sales Order')
	
	relevant_cso = (
		frappe.qb.from_(OrderBatchItem)
		.inner_join(CollectiveSalesOrder).on(OrderBatchItem.parent == CollectiveSalesOrder.name)
		.select(OrderBatchItem.parent, OrderBatchItem.sales_order)
		.where(OrderBatchItem.sales_order.isin(sales_orders_in_invoice))
	).run(as_dict=True)
	
	if not relevant_cso:
		return
	
	# Group by collective sales order
	cso_dict = {}
	for row in relevant_cso:
		if row.parent not in cso_dict:
			cso_dict[row.parent] = []
		cso_dict[row.parent].append(row.sales_order)
	
	# Add sales invoice to each relevant collective sales order
	for cso_name, matching_orders in cso_dict.items():
		try:
			cso_doc = frappe.get_doc("Collective Sales Order", cso_name)
			
			# Check if this sales invoice is already added
			existing_invoice = any(
				item.sales_invoice == doc.name for item in (cso_doc.invoice_items or [])
			)
			
			if not existing_invoice:
				# Add invoice items for each matching sales order
				for sales_order in matching_orders:
					cso_doc.append("invoice_items", {
						"sales_order": sales_order,
						"sales_invoice": doc.name
					})
				
				cso_doc.save(ignore_permissions=True)
				frappe.msgprint(_("Sales Invoice {0} automatically added to Collective Sales Order {1}").format(doc.name, cso_name), alert=True)

		except Exception as e:
			frappe.log_error(_("Failed to add Sales Invoice {0} to Collective Sales Order {1}: {2}").format(doc.name, cso_name, str(e)), "Auto Add Sales Invoice Error")
			frappe.msgprint(_("Failed to automatically add Sales Invoice to Collective Sales Order {0}. Please check error logs.").format(cso_name), alert=True, indicator="red")
