import frappe
from frappe.utils import nowdate

@frappe.whitelist()
def make_sales_order(doc_type, doc_name):
    doc = frappe.get_doc(doc_type, doc_name)
    
    items = []
    container_childs = []
    storage_item = frappe.db.get_single_value("ICD TZ Settings", "container_storage_item")

    for item in doc.get("services"):
        qty = 1
        if item.get("service") == storage_item:
            container_childs = get_container_days_to_be_billed(doc.get("container_no"))
            qty = len(container_childs)
        
        items.append({
            'item_code': item.get("service"),
            'qty': qty,
        })

    default_price_list = frappe.db.get_value("ICD TZ Settings", None, "default_price_list")
    sales_order = frappe.get_doc({
        "doctype": "Sales Order",
        "company": doc.get("company"),
        "customer": doc.c_and_f_company,
        "transaction_date": nowdate(),
        "delivery_date": nowdate(),
        "selling_price_list": default_price_list,
        "items": items,
    })
    
    sales_order.insert()
    sales_order.set_missing_values()
    sales_order.calculate_taxes_and_totals()
    sales_order.save(ignore_permissions=True)
    sales_order.reload()

    frappe.db.set_value("Container Inspection", doc.name, "sales_order", sales_order.name)

    if doc.in_yard_container_booking:
        frappe.db.set_value("In Yard Container Booking", doc.in_yard_container_booking, "sales_order", sales_order.name)

    if doc.container_no and len(container_childs) > 0:
        for child in container_childs:
            frappe.db.set_value("Container Service Detail", child.get("name"), "sales_order", sales_order.name)

    frappe.msgprint(f"Sales Order <b>{sales_order.name}</b> created successfully", alert=True)
    return sales_order.name

def get_container_days_to_be_billed(container_no):
    details = frappe.db.get_all(
        "Container Service Detail",
        filters={"parent": container_no, "is_billable": 1, "sales_order": ["=", ""]},
        fields=["date", "name"]
    )
    return details