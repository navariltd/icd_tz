// Copyright (c) 2024, Nathan Kagoro and contributors
// For license information, please see license.txt

frappe.ui.form.on("Container Movement Order", {
	refresh: (frm) => {
        frm.trigger("set_queries");
        frm.trigger("create_container_reception");
	},
    onload: (frm) => {
        if (!frm.doc.company) {
            frm.set_value("company", frappe.defaults.get_user_default("Company"));
        }
        
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
                        frm.set_value("ship", data.vessel_name);
                        frm.set_value("company", data.company);
                        frm.set_value("received_date", data.arrival_date);
                        frm.set_value("voyage_no", data.voyage_no);
                        frm.set_df_property("container_no", "options", data.containers);
                        frm.refresh_fields();
                    }
                }
            });
        }
    },
    container_no: (frm) => {
        if (frm.doc.manifest && frm.doc.container_no) {
            frappe.call({
                method: "icd_tz.icd_tz.doctype.container_movement_order.container_movement_order.get_container_size_from_manifest",
                args: {
                    manifest: frm.doc.manifest,
                    container_no: frm.doc.container_no
                },
                callback: (r) => {
                    if (r.message) {
                        frm.set_value("size", r.message);
                        frm.refresh_field("size");
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
                    "ship": frm.doc.ship,
                    "ship_dc_date": frm.doc.received_date,
                    "voyage_no": frm.doc.voyage_no,
                    "port": frm.doc.port,
                    "container_no": frm.doc.container_no,
                    "size": frm.doc.size,
                    "truck_name": frm.doc.truck_name,
                }, doc => {});
            }).addClass('btn-primary');
        }
    }
});
