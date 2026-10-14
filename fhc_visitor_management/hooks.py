app_name = "fhc_visitor_management"
app_title = "FHC Visitor Management"
app_publisher = "Federal Housing Corporation"
app_description = "A comprehensive visitor management system for Federal Housing Corporation"
app_email = "it@fhc.gov.ng"
app_license = "MIT"
app_version = "1.0.0"

# App icon shown in the Frappe desk
app_icon = "octicon octicon-person"
app_color = "#1B4F72"
app_logo_url = "/assets/fhc_visitor_management/images/fhc_logo.png"

# Included apps
# required_apps = []

# Fixtures — export these records with the app so the app is self-contained
fixtures = [
    {
        "dt": "Role",
        "filters": [["name", "in", ["Receptionist", "Security Officer", "VM Admin Manager"]]]
    },
]

# DocType-level event hooks
doc_events = {
    "Visit": {
        "before_save": "fhc_visitor_management.visitor_management.doctype.visit.visit.before_save",
        "on_submit":   "fhc_visitor_management.visitor_management.doctype.visit.visit.on_submit",
        "on_cancel":   "fhc_visitor_management.visitor_management.doctype.visit.visit.on_cancel",
    },
    "Visitor": {
        "after_insert": "fhc_visitor_management.visitor_management.doctype.visitor.visitor.after_insert",
    },
}

# Scheduled tasks
scheduler_events = {
    "daily": [
        "fhc_visitor_management.visitor_management.utils.auto_checkout_overdue_visits",
    ],
}

# Website route rules (not needed for internal app but kept for future portal)
# website_route_rules = []

# Permission query conditions — restrict non-admin users from seeing other users' visits
permission_query_conditions = {
    "Visit": "fhc_visitor_management.visitor_management.doctype.visit.visit.get_permission_query_conditions",
}

has_permission = {
    "Visit": "fhc_visitor_management.visitor_management.doctype.visit.visit.has_permission",
}

# Jinja environment customizations
# jinja = {}

# Desk notifications
notification_config = "fhc_visitor_management.visitor_management.notifications.get_notification_config"
