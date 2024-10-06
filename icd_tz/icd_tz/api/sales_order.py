import frappe
from frappe.utils import nowdate

@frappe.whitelist()
def make_sales_order(doc_type, doc_name):
    doc = frappe.get_doc(doc_type, doc_name)
    settings_doc = frappe.get_doc("ICD TZ Settings")
    container_doc = frappe.get_doc("Container", doc.get("container_id"))

    items = []
    single_days, double_days = get_container_days_to_be_billed(doc, container_doc, settings_doc)
    for item in doc.get("services"):
        qty = 1
        container_childs = []
        if item.get("service") in [settings_doc.get("storage_item_single_20ft"), settings_doc.get("storage_item_single_40ft")]:
            qty = len(single_days)
            container_childs = single_days
        
        elif item.get("service") in [settings_doc.get("storage_item_double_20ft"), settings_doc.get("storage_item_double_40ft")]:
            qty = len(double_days)
            container_childs = double_days
            
        row_item = {
            'item_code': item.get("service"),
            'qty': qty,
        }
        if len(container_childs) > 0:
            row_item["container_child_refs"] = container_childs
        
        items.append(row_item)

    sales_order = frappe.get_doc({
        "doctype": "Sales Order",
        "company": doc.get("company"),
        "customer": doc.c_and_f_company,
        "transaction_date": nowdate(),
        "delivery_date": nowdate(),
        "selling_price_list": settings_doc.get("default_price_list"),
        "items": items,
        "container_no": doc.container_no,
        "service_order": doc.name,
        "consignee": doc.consignee,
    })
    
    sales_order.insert()
    sales_order.set_missing_values()
    sales_order.calculate_taxes_and_totals()
    sales_order.save(ignore_permissions=True)
    sales_order.reload()

    doc.db_set("sales_order", sales_order.name)
    frappe.msgprint(f"Sales Order <b>{sales_order.name}</b> created successfully", alert=True)
    return sales_order.name

def get_container_days_to_be_billed(service_doc, doc, container_doc, settings_doc):
    single_days = []
    double_days = []
    no_of_single_days = 0
    no_of_double_days = 0
    single_charge_count = 0
    double_charge_count = 0

    if container_doc.days_to_be_billed == 0:
        return single_days, double_days

    for d in setting_doc.storage_days:
        if d.destination == service_doc.country_of_destination:
            if d.charge == "Single":
                no_of_single_days = d.get("to") - d.get("from")

            elif d.charge == "Double":
                no_of_double_days = d.get("to") - d.get("from")
                
    for row in container_doc.container_dates:
        if (
            row.is_billable == 1 and
            doc.has_single_charge == 1 and
            single_charge_count < no_of_single_days
        ):
            single_days.append(row)
            single_charge_count += 1
        
        elif (
            row.is_billable == 1 and
            doc.is_double_charge == 1 and
            single_charge_count >= no_of_single_days and
            double_charge_count < no_of_double_days
        ):
            double_days.append(row.name)
            double_charge_count += 1
    
    single_days = [row.name for row in single_days if not row.sales_invoice]
    double_days = [row.name for row in double_days if not row.sales_invoice]
    return single_days, double_days