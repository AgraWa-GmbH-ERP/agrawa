import frappe

def update_purchase_invoice_status_on_billing(si, method):
	pi_name = si.get("custom_purchase_invoice")
	if not pi_name:
		return
	pi = frappe.get_doc("Purchase Invoice", pi_name)
	pi.set_status(update=True)


@frappe.whitelist()
def unset_sales_invoice_on_sales_order_item_allocation(doc, method):
	# write an sql using frappe quiery to get all sales order "Collective Order Allocation" items linked to this sales invoice
	sales_order_allocations = frappe.db.get_all(
		"Collective Order Allocation",
		filters={"sales_invoice": doc.name},
		fields=["name", "parent"],
	)

	# now delete these allocations from sales order, delete using sales order doc.save()
	for allocation in sales_order_allocations:
		frappe.db.delete(
			"Collective Order Allocation",
			{"name": allocation.name, "parent": allocation.parent},
		)
		so_doc = frappe.get_doc("Sales Order", allocation.parent)
		so_doc.save()