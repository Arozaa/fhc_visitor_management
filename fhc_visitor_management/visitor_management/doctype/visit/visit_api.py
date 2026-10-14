"""
Whitelisted API endpoints for the Visit DocType.
These are called from the client-side JS via frappe.call().
"""

import frappe
from frappe import _


@frappe.whitelist()
def check_in(visit_name: str):
    """Perform visitor check-in."""
    doc = frappe.get_doc("Visit", visit_name)
    frappe.only_for(["Receptionist", "Security Officer", "VM Admin Manager"])
    doc.do_check_in()
    return {"message": _("Visitor checked in successfully.")}


@frappe.whitelist()
def check_out(visit_name: str):
    """Perform visitor check-out."""
    doc = frappe.get_doc("Visit", visit_name)
    frappe.only_for(["Receptionist", "Security Officer", "VM Admin Manager"])
    doc.do_check_out()
    return {"message": _("Visitor checked out successfully.")}


@frappe.whitelist()
def get_active_visits():
    """Return all visits currently in 'Checked In' state — used for dashboard."""
    visits = frappe.get_all(
        "Visit",
        filters={"workflow_state": "Checked In", "docstatus": 1},
        fields=[
            "name",
            "visitor_name",
            "host_name",
            "host_department",
            "actual_check_in",
            "badge_number",
        ],
        order_by="actual_check_in asc",
    )
    return visits
