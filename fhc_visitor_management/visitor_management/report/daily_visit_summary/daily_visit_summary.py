"""
Daily Visit Summary — Script Report
Provides a breakdown of visits per day with purpose, department,
and status filters.
"""

import frappe
from frappe import _
from frappe.utils import getdate, today


def execute(filters=None):
    filters = filters or {}
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)
    summary = get_report_summary(data)
    return columns, data, None, chart, summary


# ------------------------------------------------------------------
# Columns
# ------------------------------------------------------------------

def get_columns():
    return [
        {
            "fieldname": "visit_date",
            "label": _("Visit Date"),
            "fieldtype": "Date",
            "width": 110,
        },
        {
            "fieldname": "name",
            "label": _("Visit ID"),
            "fieldtype": "Link",
            "options": "Visit",
            "width": 150,
        },
        {
            "fieldname": "visitor_name",
            "label": _("Visitor Name"),
            "fieldtype": "Data",
            "width": 160,
        },
        {
            "fieldname": "host_department",
            "label": _("Department"),
            "fieldtype": "Link",
            "options": "Host Department",
            "width": 140,
        },
        {
            "fieldname": "host_name",
            "label": _("Host"),
            "fieldtype": "Data",
            "width": 140,
        },
        {
            "fieldname": "visit_purpose",
            "label": _("Purpose"),
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "fieldname": "workflow_state",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "fieldname": "actual_check_in",
            "label": _("Check-In"),
            "fieldtype": "Datetime",
            "width": 150,
        },
        {
            "fieldname": "actual_check_out",
            "label": _("Check-Out"),
            "fieldtype": "Datetime",
            "width": 150,
        },
        {
            "fieldname": "duration_hours",
            "label": _("Duration (hrs)"),
            "fieldtype": "Float",
            "width": 110,
            "precision": 2,
        },
    ]


# ------------------------------------------------------------------
# Data
# ------------------------------------------------------------------

def get_data(filters):
    conditions = build_conditions(filters)

    return frappe.db.sql(
        f"""
        SELECT
            v.visit_date,
            v.name,
            v.visitor_name,
            v.host_department,
            v.host_name,
            v.visit_purpose,
            v.workflow_state,
            v.actual_check_in,
            v.actual_check_out,
            v.duration_hours
        FROM `tabVisit` v
        WHERE v.docstatus < 2
          {conditions}
        ORDER BY v.visit_date DESC, v.actual_check_in DESC
        """,
        filters,
        as_dict=True,
    )


def build_conditions(filters):
    conditions = []

    if filters.get("from_date"):
        conditions.append("AND v.visit_date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append("AND v.visit_date <= %(to_date)s")
    if filters.get("host_department"):
        conditions.append("AND v.host_department = %(host_department)s")
    if filters.get("visit_purpose"):
        conditions.append("AND v.visit_purpose = %(visit_purpose)s")
    if filters.get("workflow_state"):
        conditions.append("AND v.workflow_state = %(workflow_state)s")

    return " ".join(conditions)


# ------------------------------------------------------------------
# Chart
# ------------------------------------------------------------------

def get_chart(data):
    if not data:
        return None

    from collections import defaultdict

    date_counts = defaultdict(int)
    for row in data:
        date_counts[str(row.visit_date)] += 1

    dates  = sorted(date_counts.keys())
    counts = [date_counts[d] for d in dates]

    return {
        "data": {
            "labels": dates,
            "datasets": [{"name": _("Visits"), "values": counts}],
        },
        "type": "bar",
        "colors": ["#1B4F72"],
        "title": _("Visits per Day"),
    }


# ------------------------------------------------------------------
# Summary cards
# ------------------------------------------------------------------

def get_report_summary(data):
    if not data:
        return []

    total      = len(data)
    checked_in = sum(1 for r in data if r.workflow_state == "Checked In")
    checked_out = sum(1 for r in data if r.workflow_state == "Checked Out")
    avg_duration = (
        sum(r.duration_hours or 0 for r in data if r.duration_hours) /
        max(sum(1 for r in data if r.duration_hours), 1)
    )

    return [
        {
            "value": total,
            "label": _("Total Visits"),
            "datatype": "Int",
            "indicator": "blue",
        },
        {
            "value": checked_in,
            "label": _("Currently Inside"),
            "datatype": "Int",
            "indicator": "green",
        },
        {
            "value": checked_out,
            "label": _("Checked Out"),
            "datatype": "Int",
            "indicator": "purple",
        },
        {
            "value": round(avg_duration, 2),
            "label": _("Avg Duration (hrs)"),
            "datatype": "Float",
            "indicator": "orange",
        },
    ]
