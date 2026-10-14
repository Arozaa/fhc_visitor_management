// Visitor Form — Client-side controller
// Handles UI behaviour, dynamic field visibility, and quick-action buttons.

frappe.ui.form.on("Visitor", {

    // ----------------------------------------------------------------
    // Form lifecycle
    // ----------------------------------------------------------------

    onload(frm) {
        frm.set_query("id_type", () => ({})); // keep default filter
    },

    refresh(frm) {
        frm._set_indicators(frm);
        frm._render_visit_history_button(frm);

        if (!frm.is_new()) {
            frm._render_new_visit_button(frm);
        }

        // Blacklist reason only visible when blacklisted
        frm.toggle_display("blacklist_reason", frm.doc.is_blacklisted);
    },

    // ----------------------------------------------------------------
    // Field events
    // ----------------------------------------------------------------

    is_blacklisted(frm) {
        frm.toggle_display("blacklist_reason", frm.doc.is_blacklisted);

        if (!frm.doc.is_blacklisted) {
            frm.set_value("blacklist_reason", "");
            frm.set_value("visitor_status", "Active");
        } else {
            frm.set_value("visitor_status", "Blacklisted");
        }
    },

    visitor_status(frm) {
        // Keep checkbox in sync when status is changed manually
        if (frm.doc.visitor_status !== "Blacklisted" && frm.doc.is_blacklisted) {
            frm.set_value("is_blacklisted", 0);
            frm.set_value("blacklist_reason", "");
        }
    },

    // ----------------------------------------------------------------
    // Custom methods
    // ----------------------------------------------------------------

    _set_indicators(frm) {
        const statusColour = {
            Active:      "green",
            Blacklisted: "red",
            VIP:         "purple",
        };
        const colour = statusColour[frm.doc.visitor_status] || "grey";
        frm.page.set_indicator(frm.doc.visitor_status || "Unknown", colour);
    },

    _render_new_visit_button(frm) {
        if (frm.doc.is_blacklisted) return; // do not allow visit creation for blacklisted visitors

        frm.add_custom_button(__("New Visit"), () => {
            frappe.new_doc("Visit", {
                visitor: frm.doc.name,
                visitor_name: frm.doc.full_name,
            });
        }, __("Actions"));
    },

    _render_visit_history_button(frm) {
        if (frm.is_new()) return;

        frm.add_custom_button(__("Visit History"), () => {
            frappe.set_route("List", "Visit", { visitor: frm.doc.name });
        }, __("Actions"));
    },
});
