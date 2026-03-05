import frappe
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice
import erpnext.controllers.taxes_and_totals


class CustomSalesInvoice(SalesInvoice):
    """
    Custom Sales Invoice controller to exclude specific items/item groups
    from additional discount based on Agrawa Settings.
    """

    def calculate_taxes_and_totals(self):
        """
        Override to use custom taxes_and_totals calculation class
        that respects exclusion settings from Agrawa Settings.
        """
        # Import the custom calculation class
        from agrawa.overrides.taxes_and_totals import AgrawaTaxesAndTotals
        
        # Store the original class
        original_class = erpnext.controllers.taxes_and_totals.calculate_taxes_and_totals
        
        try:
            # Temporarily replace with custom class (monkey-patching)
            erpnext.controllers.taxes_and_totals.calculate_taxes_and_totals = AgrawaTaxesAndTotals
            
            # Call parent method - it will now use our custom class
            super().calculate_taxes_and_totals()
            
        finally:
            # Always restore the original class
            erpnext.controllers.taxes_and_totals.calculate_taxes_and_totals = original_class