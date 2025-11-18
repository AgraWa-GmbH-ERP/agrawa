from frappe import _


def purchase_invoice_dashboard(data):	
	data["internal_links"]["Sales Order"] = ["items", "custom_sales_order"]
	for i, d in enumerate(data["transactions"]):
		if d["label"] == _("Reference"):
			data["transactions"][i]["items"].append("Sales Order")
			break
	return data


def sales_order_dashboard(data):
	data["non_standard_fieldnames"]["Purchase Invoice"] = "custom_sales_order"
	for i, d in enumerate(data["transactions"]):
		if d["label"] == _("Purchasing"):
			data["transactions"][i]["items"].append("Purchase Invoice")
			break

	return data