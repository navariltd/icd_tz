frappe.listview_settings["Sales Order"] = {
    add_fields: [],
    hide_name_column: true,

    onload: (listview) => {
        listview.page.add_inner_button(__("Create Sales Order"), () => {
            show_dialog();
        }).removeClass("btn-default").addClass("btn-info btn-sm");
    }
};


var show_dialog = () => {
    let d = new frappe.ui.Dialog({
        title: "Create Sales Order",
        fields: [
            {
                label: 'M BL No',
                fieldname: 'm_bl_no',
                fieldtype: 'Data',
                reqd: 1
            },
        ],
        size: "small",
        primary_action_label: 'Create Order',
        primary_action(values) {
            if (values) {
                frappe.call({
                    method: 'icd_tz.icd_tz.api.sales_order.create_sales_order',
                    args: {
                        data: values
                    },
                    freeze: true,
                    freeze_message: __('<i class="fa fa-spinner fa-spin fa-4x"></i>'),
                    callback: (r) => {
                        if (r.message) {
                            d.hide()
                            frappe.show_alert({
                                message: __("Sales Order Created successfully"),
                                indicator: 'green'
                            }, 10);
                        }
                    }
                });
            }
        }
    });

    d.show();
}