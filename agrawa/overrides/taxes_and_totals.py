from erpnext.controllers.taxes_and_totals import calculate_taxes_and_totals
from frappe.utils import flt
import frappe


# Helpers

def parse_multiselect(value, field_name):
    """
    Parse Table MultiSelect field which returns a list of child records.
    
    Args:
        value: List of child table records
        field_name: Name of the field to extract ('item_group' or 'items')
    """
    if not value:
        return set()
    
    # Table MultiSelect returns a list of child records
    if isinstance(value, list):
        result = set()
        for row in value:
            # Extract the specific field value
            if hasattr(row, field_name) and row.get(field_name):
                result.add(row.get(field_name))
        return result
    
    return set()


def get_discount_exclusion_settings():
    settings = frappe.get_single("Agrawa Settings")

    if not settings.enable_exclusion:
        return None

    return {
        "excluded_items": parse_multiselect(settings.excluded_items, "items"),
        "excluded_item_groups": parse_multiselect(settings.excluded_item_groups, "item_group"),
    }


def is_item_discount_eligible(item, settings):
	if not settings:
		return True

	if item.item_code in settings["excluded_items"]:
		return False

	item_group = frappe.db.get_value("Item", item.item_code, "item_group")

	if item_group in settings["excluded_item_groups"]:
		return False

	return True


# Override Controller

class AgrawaTaxesAndTotals(calculate_taxes_and_totals):
    """
    Custom calculation class that excludes specific items/item groups
    from additional discount based on Agrawa Settings.
    """

    def set_discount_amount(self):
        """
        Override to handle discount percentage -> amount conversion
        with exclusion logic.
        """
        if not self.doc.additional_discount_percentage:
            # No percentage discount, use standard behavior
            return super().set_discount_amount()

        settings = get_discount_exclusion_settings()

        # If exclusion disabled, use standard ERPNext behavior
        if not settings:
            return super().set_discount_amount()

        # Calculate discount only on eligible items
        eligible_net_total = sum(
            item.net_amount
            for item in self._items
            if is_item_discount_eligible(item, settings)
        )

        if eligible_net_total:
            discount_amount = flt(
                eligible_net_total * self.doc.additional_discount_percentage / 100,
                self.doc.precision("discount_amount"),
            )

            self.doc.discount_amount = discount_amount
            self.doc.base_discount_amount = flt(
                discount_amount * self.doc.conversion_rate,
                self.doc.precision("base_discount_amount"),
            )

    def apply_discount_amount(self):
        """
        Override to distribute discount only to eligible items.
        """
        if not self.doc.discount_amount:
            self.doc.base_discount_amount = 0
            return

        settings = get_discount_exclusion_settings()

        # If exclusion disabled, use standard ERPNext behavior
        if not settings:
            return super().apply_discount_amount()

        # Calculate total only from eligible items
        total_for_discount_amount = sum(
            item.net_amount
            for item in self._items
            if is_item_discount_eligible(item, settings)
        )

        if not total_for_discount_amount:
            return

        # Distribute discount only to eligible items
        for item in self._items:
            if not is_item_discount_eligible(item, settings):
                item.distributed_discount_amount = 0
                continue

            distributed_amount = (
                flt(self.doc.discount_amount)
                * item.net_amount
                / total_for_discount_amount
            )

            item.net_amount = flt(
                item.net_amount - distributed_amount,
                item.precision("net_amount"),
            )

            item.distributed_discount_amount = flt(
                distributed_amount,
                item.precision("distributed_discount_amount"),
            )

            item.net_rate = (
                flt(item.net_amount / item.qty, item.precision("net_rate"))
                if item.qty else 0
            )

            # Set base currency values
            item.base_net_rate = flt(
                item.net_rate * self.doc.conversion_rate,
                item.precision("base_net_rate")
            )
            item.base_net_amount = flt(
                item.net_amount * self.doc.conversion_rate,
                item.precision("base_net_amount")
            )

        self.discount_amount_applied = True
        self._calculate()