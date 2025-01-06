// Copyright (c) 2024, elius mgani and contributors
// For license information, please see license.txt

frappe.ui.form.on('Service Order', {
	refresh: (frm) =>{
		frm.trigger("set_filters");
		frm.trigger("make_sales_order_for_single_service_order");
	},
	onload: (frm) => {
		frm.trigger("set_filters");
		frm.trigger("make_sales_order_for_multilple_service_order")
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
					"status": "In Yard",
				}
			};
		});
	},
	make_sales_order_for_single_service_order: (frm) => {
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
	make_sales_order_for_multilple_service_order: (frm) => {
		if (!frm.doc.sales_order && frm.doc.docstatus == 1) {
			frappe.call({
				method: "get_service_orders_by_m_bl_no",
				doc: frm.doc,
				args: {},
				callback: (r) => {
					if (r.message) {
						frm.add_custom_button(__("Make Sales Order By M BL No"), () => {
							frm.trigger("make_sales_order")
							frappe.call({
								method: "icd_tz.icd_tz.api.sales_order.make_sales_order",
								args: {
									doc_type: frm.doc.doctype,
									doc_name: frm.doc.name,
									m_bl_no: frm.doc.m_bl_no,
									manifest: frm.doc.manifest
								},
								freeze: true,
								freeze_message: __("Creating Sales Order"),
								callback: (r) => {
									if (r.message) {
										frappe.set_route("Form", "Sales Order", r.message);
									}
								}
							});
						}).addClass("btn-info");
					}
				}
			});
		}
	}
});
