"""
Test suite for the Visit DocType.
Run with:  bench run-tests --app fhc_visitor_management --doctype Visit
"""

import unittest
import frappe
from frappe.utils import today, now_datetime, add_hours


def make_visitor(**kwargs):
    """Helper — create a test Visitor record."""
    defaults = {
        "doctype": "Visitor",
        "full_name": "Test Visitor",
        "id_type": "National ID",
        "id_number": f"TEST-{frappe.generate_hash(length=6)}",
        "phone": "08000000000",
        "visitor_status": "Active",
        "is_blacklisted": 0,
    }
    defaults.update(kwargs)
    doc = frappe.get_doc(defaults)
    doc.insert(ignore_permissions=True)
    return doc


def make_department():
    """Helper — create or reuse a test Host Department."""
    name = "TEST-DEPT"
    if not frappe.db.exists("Host Department", name):
        frappe.get_doc({
            "doctype": "Host Department",
            "department_name": name,
            "is_active": 1,
        }).insert(ignore_permissions=True)
    return name


def make_visit(visitor_name, **kwargs):
    """Helper — create a test Visit record."""
    dept = make_department()
    defaults = {
        "doctype": "Visit",
        "visitor": visitor_name,
        "visit_date": today(),
        "visit_purpose": "Meeting",
        "host_department": dept,
        "host_name": "Test Host",
    }
    defaults.update(kwargs)
    doc = frappe.get_doc(defaults)
    doc.insert(ignore_permissions=True)
    return doc


class TestVisitValidation(unittest.TestCase):
    """Tests for Visit server-side validation rules."""

    def setUp(self):
        frappe.set_user("Administrator")

    def test_visit_created_successfully(self):
        """A valid visit should save without errors."""
        visitor = make_visitor()
        visit = make_visit(visitor.name)
        self.assertIsNotNone(visit.name)
        self.assertTrue(visit.name.startswith("VM-VISIT-"))

    def test_blacklisted_visitor_blocked(self):
        """Creating a visit for a blacklisted visitor must raise an error."""
        visitor = make_visitor(
            full_name="Blacklisted Visitor",
            is_blacklisted=1,
            visitor_status="Blacklisted",
            blacklist_reason="Security concern",
        )
        with self.assertRaises(frappe.exceptions.ValidationError):
            make_visit(visitor.name)

    def test_departure_must_be_after_arrival(self):
        """expected_departure before expected_arrival must raise ValidationError."""
        visitor = make_visitor()
        now = now_datetime()
        with self.assertRaises(frappe.exceptions.ValidationError):
            make_visit(
                visitor.name,
                expected_arrival=now,
                expected_departure=add_hours(now, -1),
            )

    def test_duration_calculated_on_checkout(self):
        """Duration in hours should be calculated when check-in and check-out are both set."""
        visitor = make_visitor()
        visit = make_visit(visitor.name)
        check_in = now_datetime()
        check_out = add_hours(check_in, 2)
        visit.actual_check_in = check_in
        visit.actual_check_out = check_out
        visit.save(ignore_permissions=True)
        self.assertAlmostEqual(visit.duration_hours, 2.0, places=1)

    def tearDown(self):
        frappe.db.rollback()


class TestVisitorValidation(unittest.TestCase):
    """Tests for Visitor server-side validation rules."""

    def setUp(self):
        frappe.set_user("Administrator")

    def test_duplicate_id_blocked(self):
        """Two visitors with the same ID type and number must not be allowed."""
        id_number = f"DUP-{frappe.generate_hash(length=6)}"
        make_visitor(id_number=id_number)
        with self.assertRaises(frappe.exceptions.ValidationError):
            make_visitor(id_number=id_number)

    def test_blacklist_requires_reason(self):
        """Blacklisting a visitor without a reason must raise ValidationError."""
        visitor = make_visitor()
        visitor.is_blacklisted = 1
        visitor.blacklist_reason = ""
        with self.assertRaises(frappe.exceptions.ValidationError):
            visitor.save(ignore_permissions=True)

    def test_blacklist_with_reason_succeeds(self):
        """Blacklisting with a reason must succeed and update visitor_status."""
        visitor = make_visitor()
        visitor.is_blacklisted = 1
        visitor.blacklist_reason = "Attempted tailgating"
        visitor.save(ignore_permissions=True)
        self.assertEqual(visitor.visitor_status, "Blacklisted")

    def tearDown(self):
        frappe.db.rollback()


if __name__ == "__main__":
    unittest.main()
