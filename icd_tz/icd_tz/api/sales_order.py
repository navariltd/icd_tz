import frappe
from frappe.utils import nowdate
from icd_tz.icd_tz.api.utils import validate_qty_storage_item


def before_save(doc, method):
    validate_qty_storage_item(doc)

def on_trash(doc, method):
    unlink_sales_order(doc)

def unlink_sales_order(doc):
    if not doc.service_order:
        return
    
    service_order = frappe.get_doc("Service Order", doc.service_order)
    service_order.db_set("sales_order", None)
    service_order.reload()

@frappe.whitelist()
def make_sales_order(doc_type, doc_name, m_bl_no=None, manifest=None):
    service_docs = []

    if m_bl_no and manifest:
        service_docs = get_orders(m_bl_no, manifest)
    
    if len(service_docs) == 0:
        if not doc_type or not doc_name:
            return
        
        source_doc = frappe.get_doc(doc_type, doc_name)
        service_docs.append(source_doc)


    items = []
    company = None
    consignee = None
    c_and_f_company = None
    order_m_bl_no = m_bl_no if m_bl_no else None
    order_manifest = manifest if manifest else None

    settings_doc = frappe.get_cached_doc("ICD TZ Settings")
    
    for doc in service_docs:
        container_doc = frappe.get_doc("Container", doc.get("container_id"))

        single_days, double_days = get_container_days_to_be_billed(doc, container_doc, settings_doc)
        items += get_items(doc, single_days, double_days, settings_doc)

        if not consignee:
            consignee = doc.consignee
        
        if not company:
            company = doc.company
        
        if not c_and_f_company:
            c_and_f_company = doc.c_and_f_company
        
        if not order_m_bl_no:
            order_m_bl_no = doc.m_bl_no
        
        if not order_manifest:
            order_manifest = doc.manifest
    
    sales_order = frappe.get_doc({
        "doctype": "Sales Order",
        "company": company,
        "customer": c_and_f_company,
        "transaction_date": nowdate(),
        "delivery_date": nowdate(),
        "selling_price_list": settings_doc.get("default_price_list"),
        "items": items,
        "consignee": consignee,
        "m_bl_no": order_m_bl_no,
    })
    
    sales_order.insert()
    sales_order.set_missing_values()
    sales_order.calculate_taxes_and_totals()
    sales_order.save(ignore_permissions=True)
    sales_order.reload()

    for doc in service_docs:
        doc.db_set("sales_order", sales_order.name)
    
    frappe.msgprint(f"Sales Order <b>{sales_order.name}</b> created successfully", alert=True)
    return sales_order.name


def get_container_days_to_be_billed(service_doc, container_doc, settings_doc):
    single_days = []
    double_days = []
    no_of_single_days = 0
    no_of_double_days = 0
    single_charge_count = 0
    double_charge_count = 0

    if container_doc.days_to_be_billed == 0:
        return single_days, double_days

    for d in settings_doc.storage_days:
        if d.destination == service_doc.place_of_destination:
            if d.charge == "Single":
                no_of_single_days = d.get("to") - d.get("from") + 1

            elif d.charge == "Double":
                no_of_double_days = d.get("to") - d.get("from") + 1
                
    for row in container_doc.container_dates:
        if (
            row.is_billable == 1 and
            container_doc.has_single_charge == 1 and
            single_charge_count < no_of_single_days
        ):
            single_days.append(row)
            single_charge_count += 1
        
        elif (
            row.is_billable == 1 and
            container_doc.has_double_charge == 1 and
            single_charge_count >= no_of_single_days and
            double_charge_count <= no_of_double_days
        ):
            double_days.append(row)
            double_charge_count += 1
    
    single_days = [row.name for row in single_days if not row.sales_invoice]
    double_days = [row.name for row in double_days if not row.sales_invoice]
    return single_days, double_days


def get_items(doc, single_days, double_days, settings_doc):
    items = []
    for item in doc.get("services"):
        qty = 1
        container_childs = ""
        if item.get("service") in [settings_doc.get("storage_item_single_20ft"), settings_doc.get("storage_item_single_40ft")]:
            qty = len(single_days)
            container_childs = ",".join(single_days)
        
        elif item.get("service") in [settings_doc.get("storage_item_double_20ft"), settings_doc.get("storage_item_double_40ft")]:
            qty = len(double_days)
            container_childs = ",".join(double_days)
        
        row_item = {
            'item_code': item.get("service"),
            'qty': qty,
            'container_no': doc.container_no,
            'container_id': doc.container_id
        }
        if container_childs:
            row_item["container_child_refs"] = container_childs
        
        items.append(row_item)
    
    return items


def get_orders(m_bl_no, manifest):
    service_docs = []

    filters = {
        "manifest": manifest,
        "m_bl_no": m_bl_no,
        "docstatus": 1,
    }
    orders = frappe.db.get_all(
        "Service Order",
        filters=filters,
    )

    for entry in orders:
        doc = frappe.get_doc("Service Order", entry.name)
        service_docs.append(doc)

    return service_docs
    
