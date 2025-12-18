import frappe

def update_purchase_invoice_status_on_billing(si, method):
	pi_name = si.get("custom_purchase_invoice")
	if not pi_name:
		return
	pi = frappe.get_doc("Purchase Invoice", pi_name)
	pi.set_status(update=True)


def set_sales_invoice_on_collective_sales_order(doc, method):
	for item in doc.items:
		# Check if this item references a collective sales order
		if not item.get("custom_collective_sales_order") or not item.get("custom_collective_so_detail"):
			continue
		
		# so_item = frappe.get_doc("Sales Order Item", item.custom_collective_so_detail)
				
		# if so_item.parent == item.custom_collective_sales_order and so_item.name == item.custom_collective_so_detail:
		# 	# Update the custom_individual_sales_invoice field
		# 	frappe.db.set_value(
		# 		"Sales Order Item",
		# 		item.custom_collective_so_detail,
		# 		"custom_individual_sales_invoice",
		# 		doc.name,
		# 		update_modified=False
		# 	)


@frappe.whitelist()
def unset_sales_invoice_on_collective_sales_order(doc, method):
	for item in doc.items:
		# Check if this item references a collective sales order
		if not item.get("custom_collective_sales_order") or not item.get("custom_collective_so_detail"):
			continue
		
		so_item = frappe.get_doc("Sales Order Item", item.custom_collective_so_detail)
				
		if so_item.parent == item.custom_collective_sales_order and so_item.name == item.custom_collective_so_detail:
			# Clear the custom_individual_sales_invoice field
			frappe.db.set_value(
				"Sales Order Item",
				item.custom_collective_so_detail,
				"custom_individual_sales_invoice",
				None,
				update_modified=False
			)