import frappe


def execute():
	if frappe.db.exists("Country", "Deutschland") and frappe.db.exists("Country", "Germany"):
		try:
			frappe.rename_doc("Country", "Deutschland", "Germany", merge=True, force=True)
			frappe.db.commit()
		except Exception as e:
			frappe.log_error(f"Error merging Deutschland into Germany: {str(e)}")
			frappe.db.rollback()
			raise
