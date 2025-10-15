app_name = "agrawa"
app_title = "Agrawa"
app_publisher = "Phamos GmbH"
app_description = "Agrawa Customization"
app_email = "support@phamos.eu"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "agrawa",
# 		"logo": "/assets/agrawa/logo.png",
# 		"title": "Agrawa",
# 		"route": "/agrawa",
# 		"has_permission": "agrawa.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/agrawa/css/agrawa.css"
# app_include_js = "/assets/agrawa/js/agrawa.js"

# include js, css files in header of web template
# web_include_css = "/assets/agrawa/css/agrawa.css"
# web_include_js = "/assets/agrawa/js/agrawa.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "agrawa/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}
doctype_js = {
    "Customer": "public/js/customer.js",
    "Sales Order": "public/js/sales_order.js"

}
# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "agrawa/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "agrawa.utils.jinja_methods",
# 	"filters": "agrawa.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "agrawa.install.before_install"
# after_install = "agrawa.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "agrawa.uninstall.before_uninstall"
# after_uninstall = "agrawa.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "agrawa.utils.before_app_install"
# after_app_install = "agrawa.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "agrawa.utils.before_app_uninstall"
# after_app_uninstall = "agrawa.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "agrawa.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }
override_doctype_class = {
    "Purchase Order": "agrawa.overrides.purchase_order_autoname.CustomPurchaseOrder"
}


# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"agrawa.tasks.all"
# 	],
# 	"daily": [
# 		"agrawa.tasks.daily"
# 	],
# 	"hourly": [
# 		"agrawa.tasks.hourly"
# 	],
# 	"weekly": [
# 		"agrawa.tasks.weekly"
# 	],
# 	"monthly": [
# 		"agrawa.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "agrawa.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "agrawa.event.get_events"
# }

override_whitelisted_methods = {
	"erpnext.selling.doctype.sales_order.sales_order.make_purchase_order": "agrawa.overrides.sales_order_to_purchase_order.make_purchase_order"
}

#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "agrawa.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["agrawa.utils.before_request"]
# after_request = ["agrawa.utils.after_request"]

# Job Events
# ----------
# before_job = ["agrawa.utils.before_job"]
# after_job = ["agrawa.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"agrawa.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

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