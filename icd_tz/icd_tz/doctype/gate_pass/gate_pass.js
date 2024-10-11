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
        frm.set_query("icd_officer_1", () => {
            return {
                filters: {
                    "status": "Active"
                }
            }
        });
        frm.set_query("icd_officer_2", () => {
            return {
                filters: {
                    "status": "Active"
                }
            }
        });
        frm.set_query("driver", () => {
            return {
                filters: {
                    "status": "Active"
                }
            }
        });
        frm.set_query("security_officer", () => {
            return {
                filters: {
                    "disabled": 0
                }
            }
        });
        frm.set_query("transporter", () => {
            return {
                filters: {
                    "disabled": 0
                }
            }
        });
    },
});
