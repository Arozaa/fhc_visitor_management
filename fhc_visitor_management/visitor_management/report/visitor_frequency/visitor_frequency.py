"""
Visitor Frequency Report — Script Report
Ranks visitors by number of visits within a date range.
Useful for identifying frequent visitors and potential security flags.
"""

import frappe
from frappe import _


def execute(filters=None):
    filters = filters or {}
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)
    return columns, data, None, chart


def get_columns():
    return [
        {
            "fieldname": "visitor",
            "label": _("Visitor ID"),
            "fieldtype": "Link",
            "options": "Visitor",
            "width": 140,
        },
        {
            "fieldname": "full_name",
            "label": _("Full Name"),
            "fieldtype": "Data",
            "width": 180,
        },
        {
            "fieldname": "company_organization",
            "label": _("Organisation"),
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "fieldname": "visitor_status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "fieldname": "total_visits",
            "label": _("Total Visits"),
            "fieldtype": "Int",
            "width": 110,
        },
        {
            "fieldname": "last_visit_date",
            "label": _("Last Visit"),
            "fieldtype": "Date",
            "width": 110,
        },
        {
            "fieldname": "most_visited_dept",
            "label": _("Most Visited Dept"),
            "fieldtype": "Data",
            "width": 160,
        },
    ]


def get_data(filters):
    conditions = ""
    if filters.get("from_date"):
        conditions += " AND v.visit_date >= %(from_date)s"
    if filters.get("to_date"):
        conditions += " AND v.visit_date <= %(to_date)s"
    if filters.get("visitor_status"):
        conditions += " AND vis.visitor_status = %(visitor_status)s"

    return frappe.db.sql(
        f"""
        SELECT
            vis.name         AS visitor,
            vis.full_name,
            vis.company_organization,
            vis.visitor_status,
            COUNT(v.name)    AS total_visits,
            MAX(v.visit_date) AS last_visit_date,
            (
                SELECT vx.host_department
                FROM `tabVisit` vx
                WHERE vx.visitor = vis.name
                  AND vx.docstatus = 1
                GROUP BY vx.host_department
                ORDER BY COUNT(*) DESC
                LIMIT 1
            ) AS most_visited_dept
        FROM `tabVisitor` vis
        LEFT JOIN `tabVisit` v
            ON v.visitor = vis.name
            AND v.docstatus = 1
            {conditions}
        GROUP BY vis.name
        HAVING total_visits > 0
        ORDER BY total_visits DESC
        """,
        filters,
        as_dict=True,
    )


def get_chart(data):
    if not data:
        return None

    top10 = data[:10]
    return {
        "data": {
            "labels": [r.full_name for r in top10],
            "datasets": [{"name": _("Visits"), "values": [r.total_visits for r in top10]}],
        },
        "type": "bar",
        "colors": ["#154360"],
        "title": _("Top 10 Most Frequent Visitors"),
    }
