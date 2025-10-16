import frappe
from erpnext.accounts.doctype.purchase_invoice.purchase_invoice import PurchaseInvoice
from frappe.utils import flt, getdate
from erpnext.accounts.doctype.sales_invoice.sales_invoice import (
	get_total_in_party_account_currency,
	is_overdue,
)

class CustomPurchaseInvoice(PurchaseInvoice):
    def set_status(self, update=False, status=None, update_modified=True):
        if self.is_new():
            if self.get("amended_from"):
                self.status = "Draft"
            return

        outstanding_amount = flt(self.outstanding_amount, self.precision("outstanding_amount"))
        total = get_total_in_party_account_currency(self)

        if not status:
            if self.docstatus == 2:
                status = "Cancelled"
            elif self.docstatus == 1:
                if self.is_internal_transfer():
                    self.status = "Internal Transfer"
                elif is_overdue(self, total):
                    self.status = "Overdue"
                elif 0 < outstanding_amount < total:
                    self.status = "Partly Paid"
                elif outstanding_amount > 0 and getdate(self.due_date) >= getdate():
                    self.status = "Unpaid"
                # Check if outstanding amount is 0 due to debit note issued against invoice
                elif self.is_return == 0 and frappe.db.get_value(
                    "Purchase Invoice", {"is_return": 1, "return_against": self.name, "docstatus": 1}
                ):
                    self.status = "Debit Note Issued"
                elif self.is_return == 1:
                    self.status = "Return"
                elif outstanding_amount <= 0:
                    self.status = "Paid"
                else:
                    self.status = "Submitted"
                
                # ----- Custom Billing Logic -----
                linked_si = frappe.db.get_value("Sales Invoice", {"custom_purchase_invoice": self.name})

                if linked_si:
                    if outstanding_amount > 0:
                        self.status = "Billed"
                    elif outstanding_amount <= 0:
                        self.status = "Paid and Billed"
                # -------- End -------------
            else:
                self.status = "Draft"

        if update:
            self.db_set("status", self.status, update_modified=update_modified)
