// Copyright (c) 2024, elius mgani and contributors
// For license information, please see license.txt

frappe.ui.form.on('Manifest', {
	refresh: (frm) => {
		frm.trigger("create_movement_order");
	},
	onload: (frm) => {
		if (!frm.doc.company) {
			frm.set_value("company", frappe.defaults.get_user_default("Company"));
		}
		frm.trigger("create_movement_order");
	},
	manifest: (frm) => {
		if (frm.doc.manifest) {
			frappe.call({
				method: "extract_data_from_manifest_file",
				doc: frm.doc,
				args: {
				},
				freeze: true,
				freeze_message: __("Extracting data from manifest file..."),
				callback: (r) => {
					if (r.message) {
						frm.refresh();
					}
				}
			});
		}
	},
	create_movement_order: (frm) => {
		if (frm.doc.docstatus == 1) {
			frm.add_custom_button(__('Create Movement Order'), () => {
				frappe.new_doc('Container Movement Order', {
					"manifest": frm.doc.name,
					"vessel_name": frm.doc.voyage,
					"received_date": frm.doc.arrival_date,
					"voyage_no": frm.doc.voyage_no,
					"company": frm.doc.company,
				}, doc => {});
			}).addClass('btn-primary');
		}
	}
});
