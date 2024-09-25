import frappe


def on_submit(doc, method):
    update_sales_references(doc)

def update_sales_references(doc):
    if not doc.service_order:
        return
    
    order_doc = frappe.get_doc("Service Order", doc.service_order)
    if not order_doc.container_no:
        return
    
    icd_settings = frappe.get_doc("ICD TZ Settings")

    invoice_id = doc.name
    if doc.is_return:
        invoice_id = None

    for item in doc.items:
        if item.item_code == icd_settings.transport_item:
            update_container_rec(doc.container_no, invoice_id, "t_sales_invoice")
        
        elif item.item_code == icd_settings.shore_handling_item:
            update_container_rec(doc.container_no, invoice_id, "s_sales_invoice")
        
        elif item.item_code == icd_settings.in_yard_booking_item:
            update_booking_refs(order_doc.container_inspection, invoice_id, "s_sales_invoice")
        
        elif item.item_code == icd_settings.custom_verification_item:
            update_booking_refs(order_doc.container_inspection, invoice_id, "cv_sales_invoice")
        
        elif item.item_code == icd_settings.removal_item:
            update_container_refs(doc.container_id, invoice_id, "r_sales_invoice")
        
        elif item.item_code == icd_settings.corridor_levy_item:
            update_container_refs(doc.container_id, invoice_id, "c_sales_invoice")
        
        elif item.item_code == icd_settings.container_storage_item:
            update_storage_date_refs(doc.container_id, invoice_id, item.container_child_refs)
        
        else:
            update_container_insp(order_doc.container_inspection, item.item_code, invoice_id)
    


def update_container_rec(container_no, invoice_id, field):
    container_reception = frappe.db.get_value(
        "Container",
        container_no,
        "container_reception"
    )

    if container_reception:
        frappe.db.set_value(
            "Container Reception",
            container_reception,
            field,
            invoice_id
        )

def update_booking_refs(container_inspection, invoice_id, field):
    frappe.db.set_value(
        "In Yard Container Booking",
        {"container_inspection": container_inspection},
        field,
        invoice_id
    )

def update_container_refs(container_id, invoice_id, field):
    container_doc = frappe.get_doc("Container", container_id)
    container_doc[field] = invoice_id
    container_doc.save(ignore_permissions=True)

def update_storage_date_refs(container_id, invoice_id, child_refs):
    container_doc = frappe.get_doc("Container", container_id)
    for child in container_doc.container_dates:
        if child.name in child_refs:
            child.sales_invoice = invoice_id
    
    container_doc.save(ignore_permissions=True)

def update_container_insp(container_inspection, item_code, invoice_id):
    insp_doc = frappe.get_doc("Container Inspection", container_inspection)
    for row in insp_doc.services:
        if row.service == item_code:
            frappe.db.set_value(
                "Container Inspection Detail",
                row.name,
                "sales_invoice",
                invoice_id
            )

