import frappe
from icd_tz.icd_tz.api.utils import validate_qty_storage_item


def before_save(doc, method):
    validate_qty_storage_item(doc)

def on_submit(doc, method):
    update_sales_references(doc)

def update_sales_references(doc):
    if not doc.service_order:
        return
    
    order_doc = frappe.get_doc("Service Order", doc.service_order)
    if not order_doc.container_id:
        return
    
    settings_doc = frappe.get_doc("ICD TZ Settings")

    invoice_id = doc.name
    if doc.is_return:
        invoice_id = None

    for item in doc.items:
        if item.item_code == settings_doc.transport_item:
            update_container_rec(order_doc.container_id, invoice_id, "t_sales_invoice")
        
        elif item.item_code in [
            settings_doc.get("shore_handling_item_t1_20ft"),
            settings_doc.get("shore_handling_item_t1_40ft"),
            settings_doc.get("shore_handling_item_t2_20ft"),
            settings_doc.get("shore_handling_item_t2_40ft")
        ]:
            update_container_rec(order_doc.container_id, invoice_id, "s_sales_invoice")
        
        elif item.item_code == settings_doc.in_yard_booking_item:
            update_booking_refs(order_doc.container_inspection, invoice_id, "s_sales_invoice")
        
        elif item.item_code == settings_doc.custom_verification_item:
            update_booking_refs(order_doc.container_inspection, invoice_id, "cv_sales_invoice")
        
        elif item.item_code == settings_doc.removal_item:
            update_container_refs(order_doc.container_id, invoice_id, "r_sales_invoice")
        
        elif item.item_code == settings_doc.corridor_levy_item:
            update_container_refs(order_doc.container_id, invoice_id, "c_sales_invoice")
        
        elif item.item_code in [
            settings_doc.get("storage_item_single_20ft"),
            settings_doc.get("storage_item_single_40ft"),
            settings_doc.get("storage_item_double_20ft"),
            settings_doc.get("storage_item_double_40ft")
        ]:
            update_storage_date_refs(order_doc.container_id, invoice_id, item.container_child_refs)
        
        else:
            update_container_insp(order_doc.container_inspection, item.item_code, invoice_id)
    
    order_doc.db_set("sales_invoice", invoice_id)


def update_container_rec(container_id, invoice_id, field):
    container_reception = frappe.db.get_value(
        "Container",
        container_id,
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

