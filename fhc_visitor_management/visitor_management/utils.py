"""
Utility functions and scheduled tasks for the Visitor Management module.
"""

import frappe
from frappe import _
from frappe.utils import now_datetime, add_hours, get_datetime


def auto_checkout_overdue_visits():
    """
    Scheduled daily task.
    Automatically checks out visits that were checked in more than 12 hours ago
    and were never manually checked out.  Logs the action for audit.
    """
    cutoff = add_hours(now_datetime(), -12)

    overdue_visits = frappe.get_all(
        "Visit",
        filters={
            "workflow_state": "Checked In",
            "actual_check_in": ("<", cutoff),
            "actual_check_out": ("is", "not set"),
            "docstatus": 1,
        },
        fields=["name", "visitor_name", "actual_check_in"],
    )

    for visit_data in overdue_visits:
        try:
            visit = frappe.get_doc("Visit", visit_data.name)
            visit.do_check_out()
            frappe.logger().info(
                f"[VMS] Auto-checkout applied to {visit.name} ({visit.visitor_name})"
            )
        except Exception:
            frappe.log_error(
                frappe.get_traceback(),
                f"Auto-checkout failed for Visit {visit_data.name}",
            )
