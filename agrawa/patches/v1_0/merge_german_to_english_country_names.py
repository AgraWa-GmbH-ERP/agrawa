import frappe


def execute():
	country_mappings = [
		("Deutschland", "Germany"),
		("Österreich", "Austria"),
		("Frankreich", "France"),
	]
	
	for old_country, new_country in country_mappings:
		if frappe.db.exists("Country", old_country) and frappe.db.exists("Country", new_country):
			try:
				frappe.rename_doc("Country", old_country, new_country, merge=True, force=True)
				frappe.db.commit()
			except Exception as e:
				frappe.log_error(f"Error merging {old_country} into {new_country}: {str(e)}")
				frappe.db.rollback()
				raise