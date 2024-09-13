// Copyright (c) 2024, Nathan Kagoro and contributors
// For license information, please see license.txt

frappe.ui.form.on('Container Reception', {
	refresh: (frm) => {
		frm.trigger("set_queries");
	},
	onload: (frm) => {
        if (!frm.doc.company) {
            frm.set_value("company", frappe.defaults.get_user_default("Company"));
            console.log("Company: ", frm.doc.company);
        }

		frm.trigger("set_queries");
	},
    set_queries: (frm) => {
        frm.set_query("movement_order", () => {
            return {
                filters: {
                    docstatus: 1
                }
            };
        });
    },
});
