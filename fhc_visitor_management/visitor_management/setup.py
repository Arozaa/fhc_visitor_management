"""
Sample data setup for demonstration and evaluator testing.
Run via:
  bench --site <site> execute fhc_visitor_management.visitor_management.setup.create_sample_data
"""

import frappe
from frappe.utils import today, add_days, now_datetime


DEPARTMENTS = [
    {"department_name": "Finance & Accounts",    "department_code": "FIN",  "floor_location": "1st Floor", "is_active": 1},
    {"department_name": "Human Resources",        "department_code": "HR",   "floor_location": "2nd Floor", "is_active": 1},
    {"department_name": "Information Technology", "department_code": "IT",   "floor_location": "3rd Floor", "is_active": 1},
    {"department_name": "Legal & Compliance",     "department_code": "LGL",  "floor_location": "4th Floor", "is_active": 1},
    {"department_name": "Executive Office",       "department_code": "EXEC", "floor_location": "5th Floor", "is_active": 1},
]

VISITORS = [
    {"full_name": "Emeka Okafor",      "id_type": "National ID",     "id_number": "NIN-001-VMS", "phone": "08011111111", "gender": "Male",   "company_organization": "Okafor Consulting"},
    {"full_name": "Ngozi Adeyemi",     "id_type": "Passport",        "id_number": "PAS-002-VMS", "phone": "08022222222", "gender": "Female",  "company_organization": "Lagos State Govt"},
    {"full_name": "Chukwudi Eze",      "id_type": "Driver's License","id_number": "DRV-003-VMS", "phone": "08033333333", "gender": "Male",   "company_organization": "Eze Builders Ltd"},
    {"full_name": "Amina Suleiman",    "id_type": "Voter's Card",    "id_number": "VTR-004-VMS", "phone": "08044444444", "gender": "Female",  "company_organization": "Abuja Properties"},
    {"full_name": "Tunde Fashola",     "id_type": "Staff ID",        "id_number": "STF-005-VMS", "phone": "08055555555", "gender": "Male",   "company_organization": "Federal Ministry"},
    {"full_name": "Hauwa Musa",        "id_type": "National ID",     "id_number": "NIN-006-VMS", "phone": "08066666666", "gender": "Female",  "company_organization": "Musa Enterprises"},
    {"full_name": "Babatunde Adewale", "id_type": "Passport",        "id_number": "PAS-007-VMS", "phone": "08077777777", "gender": "Male",   "company_organization": "Adewale Law Firm"},
    {"full_name": "Chisom Obi",        "id_type": "National ID",     "id_number": "NIN-008-VMS", "phone": "08088888888", "gender": "Female",  "company_organization": "Obi Tech Solutions"},
    {"full_name": "Ibrahim Kwara",     "id_type": "Driver's License","id_number": "DRV-009-VMS", "phone": "08099999999", "gender": "Male",   "company_organization": "Kwara Housing"},
    {"full_name": "Yetunde Coker",     "id_type": "Voter's Card",    "id_number": "VTR-010-VMS", "phone": "08010101010", "gender": "Female",  "company_organization": "Coker & Associates"},
]

BADGES = [
    "VMS-BADGE-001",
    "VMS-BADGE-002",
    "VMS-BADGE-003",
    "VMS-BADGE-004",
    "VMS-BADGE-005",
]


def create_sample_data():
    """Entry point — creates all sample data."""
    frappe.flags.ignore_permissions = True

    _create_departments()
    visitor_map = _create_visitors()
    badge_map = _create_badges()
    _create_visits(visitor_map, badge_map)

    frappe.db.commit()
    print("[VMS] Sample data created successfully.")


def _create_departments():
    for dept in DEPARTMENTS:
        if not frappe.db.exists("Host Department", dept["department_name"]):
            frappe.get_doc({"doctype": "Host Department", **dept}).insert()
            print(f"  Created department: {dept['department_name']}")


def _create_visitors():
    visitor_map = {}
    for v in VISITORS:
        if not frappe.db.exists("Visitor", {"id_number": v["id_number"]}):
            doc = frappe.get_doc({"doctype": "Visitor", "visitor_status": "Active", **v})
            doc.insert()
            visitor_map[v["full_name"]] = doc.name
            print(f"  Created visitor: {v['full_name']} ({doc.name})")
        else:
            existing = frappe.db.get_value("Visitor", {"id_number": v["id_number"]}, "name")
            visitor_map[v["full_name"]] = existing
    return visitor_map


def _create_badges():
    badge_map = {}
    for badge_num in BADGES:
        if not frappe.db.exists("Visitor Badge", {"badge_number": badge_num}):
            doc = frappe.get_doc({
                "doctype": "Visitor Badge",
                "badge_number": badge_num,
                "badge_status": "Available",
            })
            doc.insert()
            badge_map[badge_num] = doc.name
            print(f"  Created badge: {badge_num}")
        else:
            badge_map[badge_num] = frappe.db.get_value("Visitor Badge", {"badge_number": badge_num}, "name")
    return badge_map


def _create_visits(visitor_map, badge_map):
    visits = [
        {
            "visitor_key": "Emeka Okafor",
            "host_department": "Finance & Accounts",
            "host_name": "Mr. Bello Yusuf",
            "visit_purpose": "Meeting",
            "visit_date": today(),
            "workflow_state": "Checked In",
        },
        {
            "visitor_key": "Ngozi Adeyemi",
            "host_department": "Human Resources",
            "host_name": "Mrs. Kemi Balogun",
            "visit_purpose": "Interview",
            "visit_date": today(),
            "workflow_state": "Approved",
        },
        {
            "visitor_key": "Chukwudi Eze",
            "host_department": "Information Technology",
            "host_name": "Mr. Usman Garba",
            "visit_purpose": "Maintenance",
            "visit_date": today(),
            "workflow_state": "Pending Approval",
        },
        {
            "visitor_key": "Amina Suleiman",
            "host_department": "Legal & Compliance",
            "host_name": "Barrister Ada Nwosu",
            "visit_purpose": "Official Business",
            "visit_date": add_days(today(), -1),
            "workflow_state": "Checked Out",
        },
        {
            "visitor_key": "Tunde Fashola",
            "host_department": "Executive Office",
            "host_name": "DG Office",
            "visit_purpose": "Meeting",
            "visit_date": add_days(today(), -1),
            "workflow_state": "Checked Out",
        },
    ]

    for v in visits:
        visitor_id = visitor_map.get(v["visitor_key"])
        if not visitor_id:
            continue

        doc = frappe.get_doc({
            "doctype": "Visit",
            "visitor": visitor_id,
            "visit_date": v["visit_date"],
            "visit_purpose": v["visit_purpose"],
            "host_department": v["host_department"],
            "host_name": v["host_name"],
            "workflow_state": v["workflow_state"],
        })
        doc.insert()
        print(f"  Created visit: {doc.name} ({v['visitor_key']} → {v['host_department']})")
