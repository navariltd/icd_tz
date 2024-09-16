# Copyright (c) 2024, Nathan Kagoro and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import nowdate
from frappe.model.document import Document

class ContainerInspection(Document):

    def on_submit(self):
        if not self.sales_order:
            make_sales_order(self)

@frappe.whitelist()
def make_sales_order(self):
    if isinstance(self, str):
        self = frappe.parse_json(self)
    
    items = []
    for item in self.get("services"):
        items.append({
            'item_code': item.get("service"),
            'qty': 1,
        })

    default_price_list = frappe.db.get_value("ICD TZ Settings", None, "default_price_list")
    sales_order = frappe.get_doc({
        "doctype": "Sales Order",
        "company": self.get("company"),
        "customer": self.get("customer"),
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

    frappe.db.set_value("Container Inspection", self.name, "sales_order", sales_order.name)

    frappe.msgprint(f"Sales Order <b>{sales_order.name}</b> created successfully", alert=True)
    return sales_order.name
