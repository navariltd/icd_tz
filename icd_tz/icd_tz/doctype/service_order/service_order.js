// Copyright (c) 2024, elius mgani and contributors
// For license information, please see license.txt

frappe.ui.form.on('Service Order', {
	refresh: (frm) =>{
		frm.trigger("set_filters");
	},
	onload: (frm) => {
		frm.trigger("set_filters");
	},
	set_filters: (frm) => {
		frm.set_query("service", "services", () => {
			return {
				filters: {
					"item_group": "ICD Services"
				}
			};
		});
		frm.set_query("container_id", () => {
			return {
				filters: {
					"status": ["!=", "Delivered"],
				}
			};
		});
	}
});
