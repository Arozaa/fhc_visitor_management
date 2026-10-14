"""
Visitor DocType Controller
Handles visitor registration, blacklist validation, and visit statistics.
"""

import frappe
from frappe import _
from frappe.model.document import Document


class Visitor(Document):
    # ------------------------------------------------------------------
    # Lifecycle hooks
    # ------------------------------------------------------------------

    def validate(self):
        self._validate_id_number()
        self._sync_blacklist_status()

    def after_insert(self):
        """Send a welcome / registration confirmation to the visitor (if email provided)."""
        if self.email:
            self._send_registration_email()

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------

    def _validate_id_number(self):
        """Ensure the ID number is unique across all visitor records."""
        if not self.id_number:
            return

        duplicate = frappe.db.exists(
            "Visitor",
            {
                "id_number": self.id_number,
                "id_type": self.id_type,
                "name": ("!=", self.name),
            },
        )

        if duplicate:
            frappe.throw(
                _("A visitor with {0} number <b>{1}</b> already exists: {2}").format(
                    self.id_type, self.id_number, duplicate
                ),
                title=_("Duplicate ID"),
            )

    def _sync_blacklist_status(self):
        """Keep visitor_status field in sync with is_blacklisted checkbox."""
        if self.is_blacklisted:
            if not self.blacklist_reason:
                frappe.throw(
                    _("Please provide a reason for blacklisting this visitor."),
                    title=_("Blacklist Reason Required"),
                )
            self.visitor_status = "Blacklisted"
        elif self.visitor_status == "Blacklisted":
            # Unchecking the blacklist flag clears the Blacklisted status
            self.visitor_status = "Active"

    # ------------------------------------------------------------------
    # Business logic
    # ------------------------------------------------------------------

    def update_visit_stats(self):
        """Recalculate total visits and last visit date. Called from Visit controller."""
        result = frappe.db.sql(
            """
            SELECT
                COUNT(*) AS total,
                MAX(visit_date) AS last_date
            FROM `tabVisit`
            WHERE visitor = %s
              AND docstatus = 1
            """,
            self.name,
            as_dict=True,
        )

        if result:
            self.db_set("total_visits", result[0].total or 0, update_modified=False)
            self.db_set("last_visit_date", result[0].last_date, update_modified=False)

    def _send_registration_email(self):
        """Send a registration acknowledgement email to the visitor."""
        try:
            frappe.sendmail(
                recipients=[self.email],
                subject=_("Visitor Registration – Federal Housing Corporation"),
                template="visitor_registered",
                args={
                    "visitor_name": self.full_name,
                    "visitor_id": self.name,
                },
                header=[_("Welcome to FHC"), "green"],
            )
        except Exception:
            # Email failure must not block the save
            frappe.log_error(frappe.get_traceback(), _("Visitor Registration Email Failed"))
