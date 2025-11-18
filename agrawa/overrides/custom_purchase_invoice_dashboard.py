from frappe import _


def get_data(data):	
	data["internal_links"]["Sales Order"] = ["items", "custom_sales_order"]
	data["transactions"][1]["items"].append("Sales Order")
	return data
