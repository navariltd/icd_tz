// Copyright (c) 2024, Nathan Kagoro and contributors
// For license information, please see license.txt

frappe.ui.form.on('Container Inspection', {
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
	make_sales_order: (frm) => {
		frm.add_custom_button(__("Make Sales Order"), () => {
			if (!frm.doc.customer) {
				frappe.msgprint("Please select a customer");
				return;
			}
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
	},
});
