// Copyright (c) 2024, Nathan Kagoro and contributors
// For license information, please see license.txt

frappe.ui.form.on("Container Movement Order", {
	refresh: (frm) => {
        frm.trigger("set_queries");

	},
    onload: (frm) => {
        frm.trigger("set_queries");
    },
    set_queries: (frm) => {
        frm.set_query("manifest", () => {
            return {
                filters: {
                    docstatus: 1
                }
            };
        });
    },

