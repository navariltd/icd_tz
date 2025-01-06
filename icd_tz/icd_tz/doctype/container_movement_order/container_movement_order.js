// Copyright (c) 2024, elius mgani and contributors
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
        frm.set_query("transporter", () => {
            return {
                filters: {
                    "disabled": 0
                }
            }
        });
        frm.set_query("driver", () => {
            return {
                filters: {
                    "status": "Active",
                    "vehicle_owner": frm.doc.transporter
                }
            }
        });
        frm.set_query("truck", () => {
            return {
                filters: {
                    "disabled": 0,
                    "vehicle_owner": frm.doc.transporter,
                    "is_truck": 1
                }
            }
        });
        frm.set_query("trailer", () => {
            return {
                filters: {
                    "disabled": 0,
                    "vehicle_owner": frm.doc.transporter,
                    "is_trailer": 1
                }
            }
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
                    console.log(r.message);
                    if (r.message) {
                        let container_info = r.message;
                        frm.set_value("size", container_info.container_size);
                        frm.set_value("cargo_classification", container_info.cargo_classification);
                        frm.refresh_field("size");
                        frm.refresh_field("cargo_classification");
                    }
                }
            });
        } else if (!frm.doc.container_no) {
            frm.set_value("size", "");
            frm.set_value("cargo_classification", "");
            frm.refresh_field("size");
            frm.refresh_field("cargo_classification");
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
                    "truck": frm.doc.truck,
                    "trailer": frm.doc.trailer,
                    "driver": frm.doc.driver,
                    "driver_license": frm.doc.driver_license,
                    "transporter": frm.doc.transporter,
                    "cargo_classification": frm.doc.cargo_classification,
                }, doc => {});
            }).addClass('btn-primary');
        }
    }
});
