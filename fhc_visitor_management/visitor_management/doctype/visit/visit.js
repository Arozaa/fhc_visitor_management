// Visit Form — Client-side controller
// Handles status indicators, dynamic field behaviour,
// check-in/check-out buttons, and real-time duration display.

frappe.ui.form.on("Visit", {

    // ----------------------------------------------------------------
    // Form lifecycle
    // ----------------------------------------------------------------

    setup(frm) {
        // Filter badge lookup to only Available badges
        frm.set_query("badge_number", () => ({
            filters: { badge_status: "Available" },
        }));

        // Filter host department to active departments only
        frm.set_query("host_department", () => ({
            filters: { is_active: 1 },
        }));
    },

    onload(frm) {
        if (frm.is_new()) {
            frm.set_value("visit_date", frappe.datetime.get_today());
        }
    },

    refresh(frm) {
        frm._render_status_indicator(frm);
        frm._render_action_buttons(frm);
        frm._toggle_timing_fields(frm);
    },

    // ----------------------------------------------------------------
    // Field events
    // ----------------------------------------------------------------

    visitor(frm) {
        if (!frm.doc.visitor) return;

        // Warn immediately if the visitor is blacklisted
        frappe.db.get_value("Visitor", frm.doc.visitor, ["is_blacklisted", "visitor_status"], (d) => {
            if (d && d.is_blacklisted) {
                frappe.msgprint({
                    title: __("Blacklisted Visitor"),
                    message: __("This visitor is blacklisted and cannot be granted entry."),
                    indicator: "red",
                });
                frm.set_value("visitor", "");
            }
        });
    },

    expected_arrival(frm) {
        frm._suggest_departure(frm);
    },

    actual_check_in(frm) {
        frm._compute_live_duration(frm);
    },

    actual_check_out(frm) {
        frm._compute_live_duration(frm);
    },

    // ----------------------------------------------------------------
    // Private helpers
    // ----------------------------------------------------------------

    _render_status_indicator(frm) {
        const colours = {
            Draft:            "grey",
            "Pending Approval": "yellow",
            Approved:         "blue",
            "Checked In":     "green",
            "Checked Out":    "purple",
            Cancelled:        "red",
        };
        const state = frm.doc.workflow_state || "Draft";
        frm.page.set_indicator(state, colours[state] || "grey");
    },

    _render_action_buttons(frm) {
        if (frm.is_new() || frm.doc.docstatus === 2) return;

        const state = frm.doc.workflow_state;

        // Check In button — only when visit is Approved
        if (state === "Approved" && !frm.doc.actual_check_in) {
            frm.add_custom_button(__("Check In"), () => {
                frappe.confirm(
                    __("Confirm check-in for <b>{0}</b>?", [frm.doc.visitor_name]),
                    () => {
                        frappe.call({
                            method: "fhc_visitor_management.visitor_management.doctype.visit.visit_api.check_in",
                            args: { visit_name: frm.doc.name },
                            callback(r) {
                                if (!r.exc) frm.reload_doc();
                            },
                        });
                    }
                );
            }, __("Actions")).addClass("btn-success");
        }

        // Check Out button — only when visitor is currently Checked In
        if (state === "Checked In" && frm.doc.actual_check_in && !frm.doc.actual_check_out) {
            frm.add_custom_button(__("Check Out"), () => {
                frappe.confirm(
                    __("Confirm check-out for <b>{0}</b>?", [frm.doc.visitor_name]),
                    () => {
                        frappe.call({
                            method: "fhc_visitor_management.visitor_management.doctype.visit.visit_api.check_out",
                            args: { visit_name: frm.doc.name },
                            callback(r) {
                                if (!r.exc) frm.reload_doc();
                            },
                        });
                    }
                );
            }, __("Actions")).addClass("btn-primary");
        }

        // Print Pass button — always available for saved records
        frm.add_custom_button(__("Print Visitor Pass"), () => {
            frappe.set_route("print", "Visit", frm.doc.name, { print_format: "Visitor Pass" });
        }, __("Actions"));
    },

    _toggle_timing_fields(frm) {
        const checkedIn  = !!frm.doc.actual_check_in;
        const checkedOut = !!frm.doc.actual_check_out;

        frm.set_df_property("actual_check_in",  "hidden", 0);
        frm.set_df_property("actual_check_out", "hidden", 0);
        frm.set_df_property("duration_hours",   "hidden", !checkedOut);
    },

    _suggest_departure(frm) {
        // Auto-suggest departure as 2 hours after arrival
        if (frm.doc.expected_arrival && !frm.doc.expected_departure) {
            const arrival = moment(frm.doc.expected_arrival);
            frm.set_value(
                "expected_departure",
                arrival.add(2, "hours").format("YYYY-MM-DD HH:mm:ss")
            );
        }
    },

    _compute_live_duration(frm) {
        if (frm.doc.actual_check_in && frm.doc.actual_check_out) {
            const checkIn  = moment(frm.doc.actual_check_in);
            const checkOut = moment(frm.doc.actual_check_out);
            const hours    = checkOut.diff(checkIn, "minutes") / 60;
            frm.set_value("duration_hours", Math.round(hours * 100) / 100);
        }
    },
});
