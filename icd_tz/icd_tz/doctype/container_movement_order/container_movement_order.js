// Copyright (c) 2024, Nathan Kagoro and contributors
// For license information, please see license.txt

frappe.ui.form.on("Container Movement Order", {
	refresh: (frm) => {
        frm.trigger("set_queries");
        frm.trigger("create_container_reception");
	},
    onload: (frm) => {
        frm.trigger("set_queries");
        frm.trigger("create_container_reception");
    },
    set_queries: (frm) => {
        frm.set_query("manifest", () => {
            return {
                filters: {
                    docstatus: 1
                }
            };
        });
    },
    manifest: (frm) => {
        if (frm.doc.manifest) {
            frappe.call({
                method: "icd_tz.icd_tz.doctype.container_movement_order.container_movement_order.get_manifest_details",
                args: {
                    manifest: frm.doc.manifest
                },
                freeze: true,
                freeze_message: __("Please wait..."),
                callback: (r) => {
                    if (r.message) {
                        let data = r.message;
                        frm.set_value("vessel_name", data.voyage);
                        frm.set_value("received_date", data.arrival_date);
                        frm.set_value("voyage_no", data.voyage);
                        frm.set_df_property("container_number", "options", data.containers);
                        frm.refresh_fields();
                    }
                }
            });
        }
    },
    create_container_reception: (frm) => {
        if (frm.doc.docstatus == 1) {
            frm.add_custom_button(__('Create Container Reception'), () => {
                frappe.new_doc('Container Reception', {
                    "movement_order": frm.doc.name,
                    "manifest": frm.doc.manifest,
                    "ship_name": frm.doc.ship,
                    "vessel_name": frm.doc.vessel_name,
                    "received_date": frm.doc.received_date,
                    "voyage_no": frm.doc.voyage_no,
                    "port": frm.doc.port,
                    "container_no": frm.doc.container_number,
                    "size": frm.doc.size,
                    "truck_name": frm.doc.truck_name,
                }, doc => {});
            }).addClass('btn-primary');
        }
    }
});
