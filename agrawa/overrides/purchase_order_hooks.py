# Copyright (c) 2026, Agrawa and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def update_collective_sales_order_on_po_submit(doc, method):
    if not doc.custom_collective_sales_order:
        return

    try:
        cso_doc = frappe.get_doc("Collective Sales Order", doc.custom_collective_sales_order)
        if cso_doc.purchase_order and cso_doc.purchase_order != doc.name:
            frappe.throw(
                _("Collective Sales Order {0} is already linked to Purchase Order {1}").format(
                    cso_doc.name, cso_doc.purchase_order
                )
            )
        
        cso_doc.purchase_order = doc.name
        cso_doc.save(ignore_permissions=True)
        
        frappe.msgprint(
            _("Purchase Order {0} has been linked to Collective Sales Order {1}").format(
                doc.name, doc.custom_collective_sales_order
            ),
            alert=True
        )
        
    except frappe.DoesNotExistError:
        frappe.log_error(
            f"Collective Sales Order {doc.custom_collective_sales_order} does not exist",
            "Update Collective Sales Order on PO Submit"
        )
    except Exception as e:
        frappe.log_error(
            f"Error updating Collective Sales Order {doc.custom_collective_sales_order}: {str(e)}",
            "Update Collective Sales Order on PO Submit"
        )