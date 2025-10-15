import frappe
from frappe.model.naming import make_autoname
from datetime import datetime
from erpnext.buying.doctype.purchase_order.purchase_order import PurchaseOrder

class CustomPurchaseOrder(PurchaseOrder):
    def autoname(self):
        # Get first 4 letters of supplier name (uppercase)
        prefix = (self.supplier_name[:4].upper() if self.supplier_name else "SUPP")
        year = datetime.now().year

        # Naming pattern e.g. SUPP-2025-.#####
        naming_pattern = f"{prefix}-{year}-.####"

        # Generate name
        self.name = make_autoname(naming_pattern)
