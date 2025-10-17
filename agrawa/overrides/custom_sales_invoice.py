import frappe

def update_purchase_invoice_status_on_billing(si, method):
	pi_name = si.get("custom_purchase_invoice")
	if not pi_name:
		return
	pi = frappe.get_doc("Purchase Invoice", pi_name)
	pi.set_status(update=True)