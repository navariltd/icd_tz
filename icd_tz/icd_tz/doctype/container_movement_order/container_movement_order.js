// Copyright (c) 2024, Nathan Kagoro and contributors
// For license information, please see license.txt

frappe.ui.form.on("Container Movement Order", {
	refresh: (frm) => {
        frm.trigger("set_queries");

	},
    onload: (frm) => {
        frm.trigger("set_queries");
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
});
