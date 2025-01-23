frappe.listview_settings['In Yard Container Booking'] = {
    add_fields: [],
    hide_name_column: true,
    
    onload: (listview) => {
        listview.page.add_inner_button(__("Create Bulk Bookings"), () => {
            show_dialog(listview);
        }).removeClass("btn-default").addClass("btn-info btn-sm");

    }
}

var show_dialog = (listview) => {
    let d = new frappe.ui.Dialog({
        title: "Bulk Container Booking",
        fields: [
            {
                label: 'M BL No',
                fieldname: 'm_bl_no',
                fieldtype: 'Data',
                reqd: 1
            },
            {
                fieldname: 'cf_cb',
                fieldtype: 'Column Break'
            },
            {
                label: 'C & F Company',
                fieldname: 'c_and_f_company',
                fieldtype: 'Link',
                options: 'Clearing and Forwarding Company',
                reqd: 1
            },
            {
                label: 'Clearing Agent',
                fieldname: 'clearing_agent',
                fieldtype: 'Link',
                options: 'Clearing Agent',
                reqd: 1,
            },
            {
                fieldname: 'insp_cb',
                fieldtype: 'Column Break'
            },
            {
                label: 'Inspection Datetime',
                fieldname: 'inspection_datetime',
                fieldtype: 'Datetime',
                reqd: 1
            },
            {
                label: 'Inspection Location',
                fieldname: 'inspection_location',
                fieldtype: 'Link',
                options: 'Container Location',
                reqd: 1
            }
        ],
        size: "large",
        primary_action_label: 'Create Bookings',
        primary_action(values) {
            if (values) {
                frappe.call({
                    method: 'icd_tz.icd_tz.doctype.in_yard_container_booking.in_yard_container_booking.create_bulk_bookings',
                    args: {
                        data: values
                    },
                    freeze: true,
                    freeze_message: __('<i class="fa fa-spinner fa-spin fa-4x"></i>'),
                    callback: (r) => {
                        if (r.message) {
                            d.hide()
                            frappe.show_alert({
                                message: __("{0} Bookings Created successfully", [r.message]),
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
