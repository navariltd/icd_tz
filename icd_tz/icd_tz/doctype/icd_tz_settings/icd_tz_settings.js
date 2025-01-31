// Copyright (c) 2024, elius mgani and contributors
// For license information, please see license.txt

frappe.ui.form.on('ICD TZ Settings', {
	refresh: (frm) => {
		frm.trigger('set_filters');
	},
	onload: (frm) => {
		frm.trigger('set_filters');
	},
	set_filters: (frm) => {
		frm.set_query("transport_item", () => {
			return {
				filters: {
					"item_group": "ICD Services"
				}
			};
		});
		frm.set_query("in_yard_booking_item", () => {
			return {
				filters: {
					"item_group": "ICD Services"
				}
			};
		});
		frm.set_query("custom_verification_item", () => {
			return {
				filters: {
					"item_group": "ICD Services"
				}
			};
		});
		frm.set_query("removal_item", () => {
			return {
				filters: {
					"item_group": "ICD Services"
				}
			};
		});
		frm.set_query("corridor_levy_item", () => {
			return {
				filters: {
					"item_group": "ICD Services"
				}
			};
		});
		frm.set_query("shore_handling_item_t1_20ft", () => {
			return {
				filters: {
					"item_group": "ICD Services"
				}
			};
		});
		frm.set_query("shore_handling_item_t1_40ft", () => {
			return {
				filters: {
					"item_group": "ICD Services"
				}
			};
		});
		frm.set_query("shore_handling_item_t2_20ft", () => {
			return {
				filters: {
					"item_group": "ICD Services"
				}
			};
		});
		frm.set_query("shore_handling_item_t2_40ft", () => {
			return {
				filters: {
					"item_group": "ICD Services"
				}
			};
		});
		frm.set_query("storage_item_single_20ft", () => {
			return {
				filters: {
					"item_group": "ICD Services"
				}
			};
		});

		frm.set_query("storage_item_single_40ft", () => {
			return {
				filters: {
					"item_group": "ICD Services"
				}
			};
		});
		frm.set_query("storage_item_double_20ft", () => {
			return {
				filters: {
					"item_group": "ICD Services"
				}
			};
		});
		frm.set_query("storage_item_double_40ft", () => {
			return {
				filters: {
					"item_group": "ICD Services"
				}
			};
		});
	}
});
