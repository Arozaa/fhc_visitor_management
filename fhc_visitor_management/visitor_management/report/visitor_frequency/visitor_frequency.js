// Visitor Frequency Report — filters

frappe.query_reports["Visitor Frequency"] = {
    filters: [
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            default: frappe.datetime.year_start(),
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: frappe.datetime.get_today(),
        },
        {
            fieldname: "visitor_status",
            label: __("Visitor Status"),
            fieldtype: "Select",
            options: "\nActive\nBlacklisted\nVIP",
        },
    ],
};
