// Copyright (c) 2024, Nathan Kagoro and contributors
// For license information, please see license.txt

frappe.ui.form.on('Service Order', {
	refresh: (frm) =>{
		frm.trigger("set_filters");
		frm.trigger("make_sales_order");
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
	make_sales_order: (frm) => {
		if (!frm.doc.sales_order && frm.doc.docstatus == 1) {
			frm.add_custom_button(__("Make Sales Order"), () => {
				if (!frm.doc.services.length) {
					frappe.msgprint("Please add services to the inspection");
					return;
				}
				frappe.call({
					method: "icd_tz.icd_tz.api.sales_order.make_sales_order",
					args: {
						doc_type: frm.doc.doctype,
						doc_name: frm.doc.name
					},
					freeze: true,
					freeze_message: __("Creating Sales Order"),
					callback: (r) => {
						if (r.message) {
							frappe.set_route("Form", "Sales Order", r.message);
						}
					}
				});
			}).addClass("btn-primary");
		}
	},
});
