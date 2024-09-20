// Copyright (c) 2024, Nathan Kagoro and contributors
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
	},
	container_inspection: (frm) => {
		frm.trigger("get_booking_item");
		frm.trigger("get_container_storage_item");
	},
	get_booking_item: (frm) => {
		if (frm.doc.in_yard_container_booking) {
			frappe.call({
				method: "get_strip_services",
				doc: frm.doc,
				args: {
					self: frm.doc
				},
				callback: (r) => {
					if (r.message) {
						frm.add_child("services", {
							"service": r.message
						});
						frm.refresh_field("services");
					}
				}
			});
		}
	},
	get_container_storage_item: (frm) => {
		if (frm.doc.in_yard_container_booking) {
			frappe.call({
				method: "get_storage_services",
				doc: frm.doc,
				args: {
					self: frm.doc
				},
				callback: (r) => {
					if (r.message) {
						frm.add_child("services", {
							"service": r.message
						});
						frm.refresh_field("services");
					}
				}
			});
		}
	},
});
