const MERGE_CHECK_INTERVAL = 700;
const STABILITY_THRESHOLD = 2;

frappe.ui.form.on("Material Request", {
	refresh(frm) {
		if (frm.doc.docstatus !== 0) return;

		frm.add_custom_button(
			__("Sales Order"),
			() => frm.events.get_items_from_sales_order(frm),
			__("Get Items From")
		);
	},

	// Get items from Sales Order
	get_items_from_sales_order(frm) {
		frm.events.init_merge_watch(frm);
		frm.events.show_loading_alert();

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

	// Helpers
	init_merge_watch(frm) {
		frm.__merge_watch = {
			last_len: 0,
			unchanged_count: 0
		};
	},

	show_loading_alert() {
		frappe.show_alert({
			message: __("Loading items from Sales Order..."),
			indicator: "blue"
		});
	},

	// Wait until items stabilize
	wait_and_merge(frm) {
		setTimeout(() => {
			if (!frm ||!frm.__merge_watch) {
				frm.__merge_watch = null;
				return;
			}

			const items_len = (frm.doc.items || []).length;
			const watch = frm.__merge_watch;

			if (items_len === watch.last_len && items_len > 1) {
				watch.unchanged_count++;
			} else {
				watch.unchanged_count = 0;
			}

			watch.last_len = items_len;

			if (watch.unchanged_count >= STABILITY_THRESHOLD) {
				frm.__merge_watch = null;
				frm.events.merge_material_request_items(frm);
				return;
			}

			frm.events.wait_and_merge(frm);
		}, MERGE_CHECK_INTERVAL);
	},

	// Merge duplicate items
	merge_material_request_items(frm) {
		if (!frm.doc.items || frm.doc.items.length < 2) return;

		const merged = {};
		const final_items = [];
		let skipped = 0;

		frm.doc.items.forEach(row => {
			if (!row.item_code || !row.uom) {
				skipped++;
				return;
			}

			const key = `${row.item_code}||${row.uom}`;

			if (merged[key]) {
				merged[key].qty += row.qty || 0;
			} else {
				merged[key] = frappe.model.copy_doc(row);
				final_items.push(merged[key]);
			}
		});

		frm.clear_table("items");

		final_items.forEach(row => {
			const d = frm.add_child("items");
			Object.assign(d, row);
		});

		frm.refresh_field("items");

		const merged_count = frm.doc.items.length - final_items.length;

		if (merged_count > 0) {
			frappe.show_alert(
				{ message: __("Merged {0} duplicate items", [merged_count]), indicator: "green" },
				5
			);
		}

		if (skipped > 0) {
			frappe.show_alert(
				{ message: __("Warning: {0} items skipped due to missing data", [skipped]), indicator: "orange" },
				5
			);
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