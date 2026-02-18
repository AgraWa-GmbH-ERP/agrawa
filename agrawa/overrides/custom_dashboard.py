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
	
	# Add Collective Sales Order link configuration
	data["internal_links"]["Collective Sales Order"] = ["sales_order", "sales_orders"]
	
	for i, d in enumerate(data["transactions"]):
		if d["label"] == _("Purchasing"):
			data["transactions"][i]["items"].append("Purchase Invoice")
			break

	# Add Collective Sales Order to a suitable transaction group
	collective_group_found = False
	for i, d in enumerate(data["transactions"]):
		if d["label"] == _("Fulfillment"):
			data["transactions"][i]["items"].append("Collective Sales Order")
			collective_group_found = True
			break
	
	# If no suitable group found, create a new group
	if not collective_group_found:
		data["transactions"].append({
			"label": _("Collective Sales Order"),
			"items": ["Collective Sales Order"]
		})

	return data


def purchase_order_dashboard(data):
	# Add Collective Sales Order link configuration
	data["internal_links"]["Collective Sales Order"] = ["purchase_order", "Collective Sales Order"]
	
	# Add Collective Sales Order to a suitable transaction group
	collective_group_found = False
	for i, d in enumerate(data["transactions"]):
		if d["label"] == _("Fulfillment"):
			data["transactions"][i]["items"].append("Collective Sales Order")
			collective_group_found = True
			break
	
	# If no suitable group found, create a new group
	if not collective_group_found:
		data["transactions"].append({
			"label": _("Collective Sales Order"),
			"items": ["Collective Sales Order"]
		})

	return data


def sales_invoice_dashboard(data):
	# Add Collective Sales Order link configuration
	data["internal_links"]["Collective Sales Order"] = ["sales_invoice", "Collective Sales Order"]
	
	# Add Collective Sales Order to a suitable transaction group
	collective_group_found = False
	for i, d in enumerate(data["transactions"]):
		if d["label"] == _("Fulfillment"):
			data["transactions"][i]["items"].append("Collective Sales Order")
			collective_group_found = True
			break
	
	# If no suitable group found, create a new group
	if not collective_group_found:
		data["transactions"].append({
			"label": _("Collective Sales Order"),
			"items": ["Collective Sales Order"]
		})

	return data