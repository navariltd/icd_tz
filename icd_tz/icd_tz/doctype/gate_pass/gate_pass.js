// Copyright (c) 2024, elius mgani and contributors
// For license information, please see license.txt

frappe.ui.form.on("Gate Pass", {
	refresh(frm) {
        frm.trigger("set_filters");
	},
    onload: (frm) => {
        frm.trigger("set_filters");
    },
    set_filters: (frm) => {
        frm.set_query("clearing_agent", () => {
            return {
                filters: {
                    "disabled": 0,
                    "c_and_f_company": frm.doc.c_and_f_company
                }
            }
        });
    },
});
