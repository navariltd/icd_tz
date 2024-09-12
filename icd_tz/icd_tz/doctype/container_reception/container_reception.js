// Copyright (c) 2024, Nathan Kagoro and contributors
// For license information, please see license.txt

frappe.ui.form.on('Container Reception', {
	refresh: (frm) => {

	},
	onload: (frm) => {
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
