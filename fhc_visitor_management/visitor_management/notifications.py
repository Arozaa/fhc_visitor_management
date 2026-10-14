"""
Desk notification configuration for the Visitor Management module.
"""

import frappe


def get_notification_config():
    return {
        "for_doctype": {
            "Visit": {
                # Show badge count for visits pending approval
                "Pending Approval": {"workflow_state": "Pending Approval", "docstatus": 0},
                # Show badge count for visits with visitors currently inside
                "Checked In": {"workflow_state": "Checked In", "docstatus": 1},
            },
        },
    }
