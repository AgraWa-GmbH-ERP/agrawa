// Copyright (c) 2026, Agrawa and contributors
// For license information, please see license.txt

frappe.ui.form.on('Collective Sales Order', {
	refresh: function(frm) {
		erpnext.hide_company(frm);
		
		if (frm.is_new() || !frm.doc.purchase_order) {
			frm.add_custom_button(__('Fetch Sales Orders'), function() {
				show_fetch_sales_orders_dialog(frm);
			}).addClass('btn-primary');
		}
		
		if (!frm.is_new() && !frm.doc.purchase_order) {
			frm.add_custom_button(__('Create Purchase Order'), function() {
				let customers = [];
				if (frm.doc.sales_orders && frm.doc.sales_orders.length > 0) {
					let customer_map = {};
					frm.doc.sales_orders.forEach(function(row) {
						if (row.customer) {
							customer_map[row.customer] = row.customer_name || row.customer;
						}
					});
					customers = Object.keys(customer_map);
					
					if (customers.length > 1) {
						let dialog = new frappe.ui.Dialog({
							title: __('Select Customer'),
							fields: [
								{
									fieldname: 'customer',
									fieldtype: 'Link',
									label: __('Customer'),
									options: 'Customer',
									reqd: 1,
									get_query: function() {
										return {
											filters: {
												'name': ['in', customers]
											}
										};
									}
								}
							],
							primary_action_label: __('Create Purchase Order'),
							primary_action: function() {
								let selected_customer = dialog.get_value('customer');
								dialog.hide();
								create_purchase_order_with_customer(frm, selected_customer);
							}
						});
						dialog.show();
					} else if (customers.length === 1) {
						// If only one customer, directly create purchase order
						create_purchase_order_with_customer(frm, customers[0]);
					} else {
						frappe.msgprint(__('No customers found in sales orders'));
					}
				} else {
					frappe.msgprint(__('No sales orders found'));
				}
			});
		}

		if (!frm.is_new() && frm.doc.sales_orders && frm.doc.sales_orders.length > 0) {
			frm.add_custom_button(__('Add Pending Invoices'), function() {
				frappe.call({
					method: 'agrawa.agrawa.doctype.collective_sales_order.collective_sales_order.add_pending_invoices',
					args: {
						cso_name: frm.doc.name
					},
					callback: function(r) {
						frm.reload_doc();
					}
				});
			});
		}
	},
});

function show_fetch_sales_orders_dialog(frm) {
	const dialog = new frappe.ui.Dialog({
		title: __('Fetch Sales Orders'),
		size: "large",
		fields: [
			{
				fieldname: 'customer',
				fieldtype: 'Link',
				label: __('Customer'),
				options: 'Customer',
				reqd: 0
			},
			{
				// columns break
				fieldname: 'column_break11',
				fieldtype: 'Column Break'
			},
			{
				fieldname: 'section_break',
				fieldtype: 'Section Break'
			},
			{
				fieldname: 'fetch_orders',
				fieldtype: 'Button',
				label: __('Fetch Orders'),
				click: function() {
					const customer = dialog.get_value('customer');
					frappe.call({
						method: 'agrawa.agrawa.doctype.collective_sales_order.collective_sales_order.get_sales_orders_for_cso',
						args: {
							customer: customer
						},
						callback: function(r) {
							if (r.message) {
								const sales_orders_table = dialog.fields_dict.sales_orders_table;
								sales_orders_table.df.data = r.message;
								sales_orders_table.grid.refresh();
								
								if (r.message.length === 0) {
									frappe.msgprint(__('No Sales Orders found with status "To Deliver"' + (customer ? ' for the selected customer' : '')));
								}
							}
						}
					});
				}
			},
			{
				fieldname: 'sales_orders_table',
				fieldtype: 'Table',
				label: __('Sales Orders'),
				cannot_add_rows: true,
				cannot_delete_rows: true,
				fields: [
					{
						fieldname: 'sales_order',
						fieldtype: 'Link',
						label: __('Sales Order'),
						options: 'Sales Order',
						in_list_view: 1,
						read_only: 1
					},
					{
						fieldname: 'customer',
						fieldtype: 'Link',
						label: __('Customer'),
						options: 'Customer',
						in_list_view: 1,
						read_only: 1
					},
					{
						fieldname: 'customer_name',
						fieldtype: 'Data',
						label: __('Customer Name'),
						in_list_view: 1,
						read_only: 1
					},
					{
						fieldname: 'grand_total',
						fieldtype: 'Currency',
						label: __('Grand Total'),
						in_list_view: 1,
						read_only: 1
					}
				]
			}
		],
		primary_action_label: __('Add Selected Orders'),
		primary_action: function() {
			const table_data = dialog.get_value('sales_orders_table');
			const selected_orders = table_data.filter(row => row?.__checked == 1 );
			if (selected_orders.length === 0) {
				frappe.msgprint(__('Please select at least one Sales Order'));
				return;
			}
			frm.doc.sales_orders = [];
			selected_orders.forEach(function(order) {
				const child_row = frm.add_child('sales_orders');
				child_row.sales_order = order.sales_order;
				child_row.customer = order.customer;
				child_row.customer_name = order.customer_name;
				child_row.grand_total = order.grand_total;
			});
			frm.refresh_field('sales_orders');
			dialog.hide();
			frappe.msgprint(__(`Added ${selected_orders.length} Sales Orders to Collective Sales Order`));
		}
	});
	
	dialog.show();
}

function create_purchase_order_with_customer(frm, customer) {
	frappe.call({
		method: 'agrawa.agrawa.doctype.collective_sales_order.collective_sales_order.create_purchase_order',
		args: {
			cso_name: frm.doc.name,
			customer: customer
		},
		callback: function(r) {
			if (r.message) {
				frm.reload_doc();
				frappe.set_route('Form', 'Purchase Order', r.message);
			}
		}
	});
}
