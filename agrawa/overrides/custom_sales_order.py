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
	allocations_by_so_detail = {}
	
	for allocation in doc.custom_item_allocation:
		so_detail = allocation.so_detail
		if so_detail not in allocations_by_so_detail:
			allocations_by_so_detail[so_detail] = 0
		allocations_by_so_detail[so_detail] += allocation.allocated_qty
	
	# Check each sales order item
	for item in doc.items:
		if item.name in allocations_by_so_detail:
			total_allocated = allocations_by_so_detail[item.name]
			if total_allocated > item.qty:
				frappe.throw("Total allocated quantity is {} for {} exceeds the ordered quantity {} on row {} in Items table".format(frappe.bold(total_allocated), frappe.get_desk_link("Item", item.item_code), frappe.bold(item.qty), item.idx))