const MERGE_CHECK_INTERVAL = 700;
const STABILITY_THRESHOLD = 2; 

frappe.ui.form.on("Material Request", {
	refresh(frm) {
		if (frm.doc.docstatus === 0) {
			frm.add_custom_button(
				__("Sales Order"),
				() => frm.events.get_items_from_sales_order(frm),
				__("Get Items From")
			);
		}
	},
	get_items_from_sales_order(frm) {
		frm.__merge_watch = {
			last_len: 0,
			unchanged_count: 0
		};

		// Show loading indicator
		frappe.show_alert({
			message: __('Loading items from Sales Order...'),
			indicator: 'blue'
		});

		erpnext.utils.map_current_doc({
			method: "erpnext.selling.doctype.sales_order.sales_order.make_material_request",
			source_doctype: "Sales Order",
			target: frm,
			setters: {
				customer: frm.doc.customer || undefined,
				delivery_date: undefined,
			},
			get_query_filters: {
				docstatus: 1,
				status: ["not in", ["Closed", "On Hold"]],
				per_delivered: ["<", 99.99],
				company: frm.doc.company,
			},
		});

		frm.events.wait_and_merge(frm);
	},

	wait_and_merge(frm) {
		setTimeout(() => {
			if (!frm || frm.is_dirty === undefined) {
				if (frm && frm.__merge_watch) {
					frm.__merge_watch = null;
				}
				return;
			}

			if (!frm.__merge_watch) return;

			let current_len = (frm.doc.items || []).length;

			if (current_len === frm.__merge_watch.last_len && current_len > 1) {
				frm.__merge_watch.unchanged_count += 1;
			} else {
				frm.__merge_watch.unchanged_count = 0;
			}

			frm.__merge_watch.last_len = current_len;

			if (frm.__merge_watch.unchanged_count >= STABILITY_THRESHOLD) {
				frm.__merge_watch = null;
				frm.events.merge_material_request_items(frm);
				return;
			}

			frm.events.wait_and_merge(frm);
		}, MERGE_CHECK_INTERVAL);
	},


	merge_material_request_items(frm) {
		if (!frm.doc.items || frm.doc.items.length < 2) {
			return;
		}

		const original_count = frm.doc.items.length;
		let merged_map = {};
		let new_items = [];
		let skipped_items = 0;

		frm.doc.items.forEach(row => {
			if (!row.item_code || !row.uom) {
				console.warn('Skipping row with missing item_code or uom:', row);
				skipped_items++;
				return;
			}

			let key = `${row.item_code}||${row.uom}`;

			if (merged_map[key]) {
				merged_map[key].qty += row.qty || 0;
			} else {
				merged_map[key] = frappe.model.copy_doc(row);
				new_items.push(merged_map[key]);
			}
		});

		frm.clear_table("items");

		new_items.forEach(row => {
			let d = frm.add_child("items");
			Object.assign(d, row);
		});

		frm.refresh_field("items");

		const merged_count = original_count - new_items.length;
		if (merged_count > 0) {
			frappe.show_alert({
				message: __('Merged {0} duplicate items', [merged_count]),
				indicator: 'green'
			}, 5);
		}

		if (skipped_items > 0) {
			frappe.show_alert({
				message: __('Warning: {0} items skipped due to missing data', [skipped_items]),
				indicator: 'orange'
			}, 5);
		}
	},

	make_purchase_order(frm) {
		frappe.prompt(
			{
				label: __("Supplier"),
				fieldname: "supplier",
				fieldtype: "Link",
				options: "Supplier",
				reqd: 1,
				get_query: () => ({
					query: "agrawa.overrides.custom_material_request.get_suppliers_from_item_supplier",
					filters: { doc: frm.doc.name }
				})
			},
			(values) => {
				frappe.model.open_mapped_doc({
					method: "agrawa.overrides.custom_material_request.make_purchase_order_item_supplier",
					frm: frm,
					args: {
						supplier: values.supplier
					}
				});
			},
			__("Create Purchase Order"),
			__("Create")
		);
	}
});