frappe.listview_settings["Service Order"] = {
    add_fields: [],
    hide_name_column: true,

    onload: (listview) => {
        listview.page.add_inner_button(__("Create Bulk Service Order"), () => {
            show_dialog(listview);
        }).removeClass("btn-default").addClass("btn-info btn-sm");
    },
    button: {
        show: function(doc) {
            return doc.docstatus === 0;
        },
        get_label: function() {
          return __("<strong>Submit</strong>");
        },
        get_description: function(doc) {
          return __("Submit {0}", [
            `${__(doc.name)}: ${doc.container_no}`
          ]);
        },
        action: function(doc) {
            frappe.call({
                method: 'icd_tz.icd_tz.api.utils.submit_doc',
                args: {
                    doc_type: 'Service Order',
                    doc_name: doc.name
                },
                freeze: true,
                freeze_message: __('<i class="fa fa-spinner fa-spin fa-4x"></i>'),
                callback: function(response) {
                    if (response.message) {
                        frappe.show_alert(__("Service Order: {0} submitted successfully.", [doc.name]), 5);
                    } else {
                        frappe.show_alert(__("Failed to submit Service Order {0}.", [doc.name]), 5);
                    }
                }
            });
        },
    },
};


var show_dialog = (listview) => {
    let d = new frappe.ui.Dialog({
        title: "Bulk Service Order",
        fields: [
            {
                label: 'M BL No',
                fieldname: 'm_bl_no',
                fieldtype: 'Data',
                reqd: 1
            },
        ],
        size: "small",
        primary_action_label: 'Create Orders',
        primary_action(values) {
            if (values) {
                frappe.call({
                    method: 'icd_tz.icd_tz.doctype.service_order.service_order.create_bulk_service_orders',
                    args: {
                        data: values
                    },
                    freeze: true,
                    freeze_message: __('<i class="fa fa-spinner fa-spin fa-4x"></i>'),
                    callback: (r) => {
                        if (r.message) {
                            d.hide()
                            frappe.show_alert({
                                message: __("{0} Service Orders Created successfully", [r.message]),
                                indicator: 'green'
                            }, 10);
                            listview.refresh();
                        }
                    }
                });
            }
        }
    });

    d.show();
}
