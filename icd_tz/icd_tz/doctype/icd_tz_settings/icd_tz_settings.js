// Copyright (c) 2024, elius mgani and contributors
// For license information, please see license.txt

frappe.ui.form.on('ICD TZ Settings', {
	refresh: (frm) => {
		frm.trigger('set_filters');
	},
	onload: (frm) => {
		frm.trigger('set_filters');
	},
	set_filters: (frm) => {
		frm.set_query("in_yard_booking_item", () => {
			return {
				filters: {
					"item_group": "ICD Services"
				}
			};
		});
		frm.set_query("container_storage_item", () => {
			return {
				filters: {
					"item_group": "ICD Services"
				}
			};
		});
	}
});
