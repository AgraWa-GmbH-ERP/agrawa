import frappe
from collections import defaultdict


@frappe.whitelist()
def get_merged_so_items_from_po(items):
    """
    Merges items from a Purchase Order based on item_code, rate, and uom.
    """
    if not items:
        return []

    merged_items = defaultdict(lambda: {"qty": 0, "amount": 0, "original_item": None})

    for item in items:
        item = item.as_dict()
        key = (item.item_code, item.rate, item.uom)
        merged_items[key]["qty"] += item.qty
        merged_items[key]["amount"] += item.amount
        if not merged_items[key]["original_item"]:
            merged_items[key]["original_item"] = item

    processed_items = []
    for key, values in merged_items.items():
        new_item = values["original_item"].copy()
        new_item.qty = values["qty"]
        new_item.amount = values["amount"]
        processed_items.append(new_item)

    return processed_items
