// Copyright (c) 2024, elius mgani and contributors
// For license information, please see license.txt

frappe.ui.form.on('Container Inspection', {
	refresh: (frm) =>{
		frm.trigger("set_filters");
		frm.trigger("create_service_order");
	},
	onload: (frm) => {
		frm.trigger("set_filters");
		frm.trigger("create_service_order");
	},
	set_filters: (frm) => {
		frm.set_query("service", "services", () => {
			return {
				filters: {
					"item_group": "ICD Services"
				}
			};
		});
        frm.set_query("driver_name", () => {
            return {
                filters: {
                    "status": "Active"
                }
            }
        });
        frm.set_query("in_yard_container_booking", () => {
            return {
                filters: {
                    "docstatus": 1
                }
            }
        });
	},
	in_yard_container_booking: (frm) => {
		frm.trigger("get_container_custom_verification");
	},
	get_container_custom_verification: (frm) => {
		if (frm.doc.in_yard_container_booking) {
			frappe.call({
				method: "get_custom_verification_services",
				doc: frm.doc,
				args: {
					// self: frm.doc,
					caller: "Front End"
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
	create_service_order: (frm) => {
		if (!frm.doc.service_order & frm.doc.docstatus == 1) {
			frm.add_custom_button(__('Create Service Order'), () => {
				frappe.new_doc('Service Order', {
					"container_inspection": frm.doc.name,
					"consignee": frm.doc.consignee,
					"clearing_agent": frm.doc.c_and_f_agent,
					"c_and_f_company": frm.doc.c_and_f_company,
					"container_id": frm.doc.container_id,
					"container_no": frm.doc.container_no,
					"container_location": frm.doc.container_location,
				}, doc => {
				});
			}).addClass('btn-primary');
		}
	}
});
