"""
Visit DocType Controller
Core business logic: validation, check-in/out, badge management,
permission scoping, and visitor stat updates.
"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import (
    now_datetime,
    get_datetime,
    time_diff_in_hours,
    today,
    getdate,
)


class Visit(Document):
    # ------------------------------------------------------------------
    # Lifecycle hooks
    # ------------------------------------------------------------------

    def before_save(self):
        self._validate_visitor_not_blacklisted()
        self._validate_date_not_in_past()
        self._validate_departure_after_arrival()
        self._compute_duration()

    def on_submit(self):
        """Submission finalises the visit record — update visitor stats."""
        self._update_visitor_stats()

    def on_cancel(self):
        """On cancellation release the badge if one was issued."""
        self._release_badge()

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate_visitor_not_blacklisted(self):
        is_blacklisted = frappe.db.get_value("Visitor", self.visitor, "is_blacklisted")
        if is_blacklisted:
            frappe.throw(
                _("Visitor <b>{0}</b> is blacklisted and cannot be allowed entry.").format(
                    self.visitor_name or self.visitor
                ),
                title=_("Blacklisted Visitor"),
            )

    def _validate_date_not_in_past(self):
        """Prevent creating backdated visits unless the user has Manager role."""
        if frappe.session.user == "Administrator":
            return
        if not frappe.db.exists("Has Role", {"parent": frappe.session.user, "role": "VM Admin Manager"}):
            if self.visit_date and getdate(self.visit_date) < getdate(today()):
                frappe.throw(
                    _("Visit date cannot be set to a past date."),
                    title=_("Invalid Date"),
                )

    def _validate_departure_after_arrival(self):
        if self.expected_arrival and self.expected_departure:
            if get_datetime(self.expected_departure) <= get_datetime(self.expected_arrival):
                frappe.throw(
                    _("Expected departure must be after the expected arrival time."),
                    title=_("Invalid Departure Time"),
                )

    # ------------------------------------------------------------------
    # Business logic
    # ------------------------------------------------------------------

    def _compute_duration(self):
        """Automatically calculate visit duration in hours once checked out."""
        if self.actual_check_in and self.actual_check_out:
            self.duration_hours = round(
                time_diff_in_hours(self.actual_check_out, self.actual_check_in), 2
            )

    def do_check_in(self):
        """Mark the visitor as checked in and issue badge if specified."""
        if self.actual_check_in:
            frappe.throw(_("Visitor has already been checked in."), title=_("Already Checked In"))

        self.actual_check_in = now_datetime()
        self._issue_badge()
        self.save(ignore_permissions=True)

        frappe.msgprint(
            _("Check-in recorded at {0}").format(
                frappe.utils.format_datetime(self.actual_check_in)
            ),
            indicator="green",
            alert=True,
        )

    def do_check_out(self):
        """Record check-out time, compute duration, and release badge."""
        if not self.actual_check_in:
            frappe.throw(_("Cannot check out — visitor has not checked in yet."), title=_("Not Checked In"))

        if self.actual_check_out:
            frappe.throw(_("Visitor has already been checked out."), title=_("Already Checked Out"))

        self.actual_check_out = now_datetime()
        self._compute_duration()
        self._release_badge()
        self.save(ignore_permissions=True)

        frappe.msgprint(
            _("Check-out recorded. Duration: {0} hours.").format(self.duration_hours),
            indicator="blue",
            alert=True,
        )

    def _issue_badge(self):
        if not self.badge_number:
            return

        badge = frappe.get_doc("Visitor Badge", self.badge_number)
        if badge.badge_status != "Available":
            frappe.throw(
                _("Badge <b>{0}</b> is not available (current status: {1}).").format(
                    self.badge_number, badge.badge_status
                ),
                title=_("Badge Unavailable"),
            )

        badge.badge_status = "Issued"
        badge.assigned_visit = self.name
        badge.assigned_to_visitor = self.visitor
        badge.issued_at = now_datetime()
        badge.issued_by = frappe.session.user
        badge.save(ignore_permissions=True)

    def _release_badge(self):
        if not self.badge_number:
            return
        try:
            badge = frappe.get_doc("Visitor Badge", self.badge_number)
            if badge.badge_status == "Issued":
                badge.mark_returned()
        except frappe.DoesNotExistError:
            pass

    def _update_visitor_stats(self):
        visitor = frappe.get_doc("Visitor", self.visitor)
        visitor.update_visit_stats()


# ------------------------------------------------------------------
# Permission helpers (called from hooks.py)
# ------------------------------------------------------------------

def get_permission_query_conditions(user):
    """
    Receptionists only see visits they created.
    Security Officers and VM Admin Managers see all visits.
    """
    if not user:
        user = frappe.session.user

    if frappe.db.exists("Has Role", {"parent": user, "role": "VM Admin Manager"}):
        return ""  # no restriction
    if frappe.db.exists("Has Role", {"parent": user, "role": "Security Officer"}):
        return ""  # security sees all
    # Receptionist — own visits only
    return f"`tabVisit`.`owner` = {frappe.db.escape(user)}"


def has_permission(doc, user=None, permission_type=None):
    """Fine-grained permission check used alongside query conditions."""
    if not user:
        user = frappe.session.user
    if frappe.db.exists("Has Role", {"parent": user, "role": "VM Admin Manager"}):
        return True
    if frappe.db.exists("Has Role", {"parent": user, "role": "Security Officer"}):
        return True
    # Receptionist can access their own records
    return doc.owner == user
