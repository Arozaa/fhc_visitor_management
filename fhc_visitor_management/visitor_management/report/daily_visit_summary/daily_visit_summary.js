// Daily Visit Summary — Report filters

frappe.query_reports["Daily Visit Summary"] = {
    filters: [
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            default: frappe.datetime.month_start(),
            reqd: 1,
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: frappe.datetime.get_today(),
            reqd: 1,
        },
        {
            fieldname: "host_department",
            label: __("Department"),
            fieldtype: "Link",
            options: "Host Department",
        },
        {
            fieldname: "visit_purpose",
            label: __("Purpose"),
            fieldtype: "Select",
            options: "\nMeeting\nDelivery\nMaintenance\nAudit\nInterview\nOfficial Business\nPersonal\nOther",
        },
        {
            fieldname: "workflow_state",
            label: __("Status"),
            fieldtype: "Select",
            options: "\nDraft\nPending Approval\nApproved\nChecked In\nChecked Out\nCancelled",
        },
    ],
};
