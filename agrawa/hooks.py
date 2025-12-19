app_name = "agrawa"
app_title = "Agrawa"
app_publisher = "Phamos GmbH"
app_description = "Agrawa Customization"
app_email = "support@phamos.eu"
app_license = "mit"


doctype_list_js = {
    "Purchase Invoice": "public/js/purchase_invoice_list.js",
}

app_include_js = "agrawa.bundle.js"

doctype_js = {
    "Customer": "public/js/custom_customer.js",
    "Sales Order": [
        "public/js/sales_order.js",
        "public/js/bio_faktii_common.js"
    ],
    "Purchase Invoice": "public/js/custom_purchase_invoice.js",
    # "Purchase Order": "public/js/custom_purchase_order.js",
    "Quotation": [
        "public/js/quotation.js",
        "public/js/bio_faktii_common.js",
    ],
    "Sales Invoice": [
        "public/js/sales_invoice.js",
        "public/js/bio_faktii_common.js"
    ],
    # "Sales Order": "public/js/sales_order.js",
    "Print Format": "public/js/custom_print_format.js"

}

doc_events = {
    "Sales Invoice": {
        "on_submit": [
            "agrawa.overrides.custom_sales_invoice.update_purchase_invoice_status_on_billing"
        ],
        "on_cancel": "agrawa.overrides.custom_sales_invoice.unset_sales_invoice_on_sales_order_item_allocation"
    },
    "Sales Order": {
        "before_save": "agrawa.overrides.custom_sales_order.set_dropshipping_data"
    }
}

override_doctype_class = {
    "Purchase Order": "agrawa.overrides.purchase_order_autoname.CustomPurchaseOrder",
}

override_whitelisted_methods = {
    "erpnext.selling.doctype.sales_order.sales_order.make_purchase_order": "agrawa.overrides.sales_order_to_purchase_order.make_purchase_order",
    "erpnext.buying.doctype.purchase_order.purchase_order.make_purchase_invoice": "agrawa.overrides.purchase_order_autoname.make_purchase_invoice"
}

fixtures = [

    {"dt": "Custom Field", "filters": [
        [
            "module", "=", "Agrawa"
        ]
    ]},
    {"dt": "Property Setter", "filters": [
        [
            "module", "=", "Agrawa"
        ]
    ]}
]

override_doctype_dashboards = {
    "Purchase Invoice": "agrawa.overrides.custom_dashboard.purchase_invoice_dashboard",
    "Sales Order": "agrawa.overrides.custom_dashboard.sales_order_dashboard"
}