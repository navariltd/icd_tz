// Copyright (c) 2024, Nathan Kagoro and contributors
// For license information, please see license.txt

frappe.ui.form.on("In Yard Container Booking", {
	refresh(frm) {
        frm.trigger("create_container_inspection");
	},
    onload: (frm) => {
        frm.trigger("create_container_inspection");
    },
	create_container_inspection: (frm) => {
		// if (frm.doc.docstatus == 1) {
			frm.add_custom_button(__('Create Container Inspection'), () => {
				frappe.new_doc('Container Inspection', {
					"in_yard_container_booking": frm.doc.name,
					"customer": frm.doc.customer,
					"clearing_agent": frm.doc.c_and_f_agent,
					"container_no": frm.doc.container_no,
                    "inspection_date": frm.doc.booking_date + " " + frm.doc.booking_time,
				}, doc => {});
			}).addClass('btn-primary');
		// }
	}
});
