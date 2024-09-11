// Copyright (c) 2024, Nelson Mpanju and contributors
// For license information, please see license.txt

frappe.ui.form.on('Manifest', {
	refresh: (frm) => {

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
			console.log(frm.doc.manifest);
		}
	},
});
