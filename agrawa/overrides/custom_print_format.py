import frappe
from frappe.modules.utils import get_doc_path

@frappe.whitelist()
def duplicate_standard_print_format(print_format):
    pf = frappe.get_doc("Print Format", print_format)

    if not pf.standard == "Yes":
        frappe.throw("Only standard print formats can be duplicated.")

    html = ""
    try:
        doc_path = get_doc_path(pf.module, "Print Format", pf.name)
        html_file = f"{doc_path}/{frappe.scrub(pf.name)}.html"
        html_file = frappe.read_file(html_file)
        html = html_file if html_file else ""
    except Exception:
        frappe.msgprint("No module file found or unable to read HTML content.")

    new_pf = frappe.copy_doc(pf)
    new_pf.standard = "No"
    new_pf.custom_format = 1
    new_pf.print_format_type = "Jinja"
    new_pf.html = html or pf.html
    new_pf.name = None

    return new_pf
    