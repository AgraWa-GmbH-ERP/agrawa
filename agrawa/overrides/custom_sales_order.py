import frappe

def set_dropshipping_data(doc, method):
    for item in doc.items:
        item_doc = frappe.get_doc("Item", item.item_code)
        if not item.supplier and item_doc.delivered_by_supplier:
            item.update({
                "delivered_by_supplier": item_doc.delivered_by_supplier,
                "supplier": item_doc.supplier_items[0].supplier if len(item_doc.supplier_items) > 0 else None
            })



def validate_allocation_quantities(doc, method=None):
	allocations_by_item = {}
	
	for allocation in doc.custom_item_allocation:
		so_detail = allocation.so_detail
		if so_detail not in allocations_by_item:
			allocations_by_item[so_detail] = 0
		allocations_by_item[so_detail] += allocation.allocated_qty
	
	# Check each sales order item
	for item in doc.items:
		if item.name in allocations_by_item:
			total_allocated = allocations_by_item[item.name]
			if total_allocated > item.qty:
				frappe.throw(
					f"Total allocated quantity ({total_allocated}) for item '{item.item_code}' "
					f"exceeds the ordered quantity ({item.qty}) in Sales Order Item {item.item_code} on row {item.idx}."
				)