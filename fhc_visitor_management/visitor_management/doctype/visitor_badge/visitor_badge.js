// Visitor Badge — Client-side controller

frappe.ui.form.on("Visitor Badge", {

    refresh(frm) {
        frm._set_status_indicator(frm);

        if (!frm.is_new() && frm.doc.badge_status === "Issued") {
            frm.add_custom_button(__("Mark as Returned"), () => {
                frappe.confirm(
                    __("Mark badge <b>{0}</b> as returned?", [frm.doc.badge_number]),
                    () => {
                        frappe.call({
                            method: "fhc_visitor_management.visitor_management.doctype.visitor_badge.visitor_badge.mark_badge_returned",
                            args: { badge_name: frm.doc.name },
                            callback(r) {
                                if (!r.exc) {
                                    frappe.show_alert({ message: __("Badge marked as returned."), indicator: "green" });
                                    frm.reload_doc();
                                }
                            },
                        });
                    }
                );
            }, __("Actions"));
        }
    },

    badge_status(frm) {
        frm._set_status_indicator(frm);
    },

    _set_status_indicator(frm) {
        const colours = {
            Available: "green",
            Issued:    "orange",
            Lost:      "red",
            Damaged:   "red",
        };
        frm.page.set_indicator(
            frm.doc.badge_status || "Unknown",
            colours[frm.doc.badge_status] || "grey"
        );
    },
});
