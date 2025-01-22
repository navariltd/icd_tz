frappe.listview_settings["Service Order"] = {
    add_fields: [],
    hide_name_column: true,

    onload: (listview) => {
        listview.page.add_inner_button(__("Create Bulk Service Order"), () => {
            show_dialog(listview);
        }).removeClass("btn-default").addClass("btn-info btn-sm");

    }
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