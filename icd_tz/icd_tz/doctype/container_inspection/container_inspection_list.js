frappe.listview_settings['Container Inspection'] = {
    onload: (listview) => {
        listview.page.add_inner_button(__("Create Bulk Inspections"), () => {
            show_dialog(listview);
        }).removeClass("btn-default").addClass("btn-info btn-sm");

    }
}

var show_dialog = (listview) => {
    let d = new frappe.ui.Dialog({
        title: "Bulk Inspections",
        fields: [
            {
                label: 'M BL No',
                fieldname: 'm_bl_no',
                fieldtype: 'Data',
                reqd: 1
            },
            {
                fieldname: 'insp_cb',
                fieldtype: 'Column Break'
            },
            {
                label: 'Inspection Name',
                fieldname: 'inspection_name',
                fieldtype: 'Data',
                reqd: 1
            },
        ],
        size: "large",
        primary_action_label: 'Create Inspections',
        primary_action(values) {
            console.log(values);
            if (values) {
                frappe.call({
                    method: 'icd_tz.icd_tz.doctype.container_inspection.container_inspection.create_bulk_inspections',
                    args: {
                        data: values
                    },
                    freeze: true,
                    freeze_message: __('<i class="fa fa-spinner fa-spin fa-4x"></i>'),
                    callback: (r) => {
                        if (r.message) {
                            d.hide()
                            frappe.show_alert({
                                message: __("{0} Inspections Created successfully", [r.message]),
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
