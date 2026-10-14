"""
Visitor Badge DocType Controller
Manages badge inventory status and assignment lifecycle.
"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class VisitorBadge(Document):

    def validate(self):
        self._validate_unique_badge_number()
        self._validate_assignment_consistency()

    def _validate_unique_badge_number(self):
        """Badge numbers must be unique across all badge records."""
        duplicate = frappe.db.exists(
            "Visitor Badge",
            {
                "badge_number": self.badge_number,
                "name": ("!=", self.name),
            },
        )
        if duplicate:
            frappe.throw(
                _("Badge number <b>{0}</b> is already registered as {1}.").format(
                    self.badge_number, duplicate
                ),
                title=_("Duplicate Badge Number"),
            )

    def _validate_assignment_consistency(self):
        """Ensure status reflects assignment state correctly."""
        if self.assigned_visit and self.badge_status == "Available":
            frappe.throw(
                _("Badge status cannot be 'Available' while assigned to a visit."),
                title=_("Inconsistent Badge Status"),
            )

    def mark_returned(self):
        """Mark the badge as returned and available for re-use."""
        self.badge_status = "Available"
        self.returned_at = now_datetime()
        self.assigned_visit = None
        self.assigned_to_visitor = None
        self.save(ignore_permissions=True)
