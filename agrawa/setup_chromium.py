import frappe


def setup_print_designer_chromium():
	if "print_designer" not in frappe.get_installed_apps():
		return
	from print_designer.install import setup_chromium

	setup_chromium()
