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
    def get_strip_services(self):
        if isinstance(self, str):
            self = frappe.parse_json(self)
        
        if not self.get("in_yard_container_booking"):
            return
        
        has_stripping_charges = frappe.db.get_value(
            "In Yard Container Booking",
            self.get("in_yard_container_booking"),
            "has_stripping_charges"
        )
        if has_stripping_charges == "Yes":
            service_names = []
            for row in self.get("services"):
                service_names.append(row.get("service"))

            in_yard_booking_item = frappe.db.get_single_value("ICD TZ Settings", "in_yard_booking_item")
            
            if in_yard_booking_item not in service_names:
                return in_yard_booking_item
            
    
    @frappe.whitelist()
    def get_storage_services(self):
        if isinstance(self, str):
            self = frappe.parse_json(self)
        
        if not self.get("in_yard_container_booking"):
            return

        yard_doc = frappe.get_doc("In Yard Container Booking", self.in_yard_container_booking)
        
        has_storage_charges = frappe.db.get_value(
            "Container", yard_doc.container_no, "days_to_be_billed"
        )
        if has_storage_charges > 0:
            service_names = []
            for row in self.get("services"):
                service_names.append(row.get("service"))
            
            storage_item = frappe.db.get_single_value("ICD TZ Settings", "container_storage_item")
            
            if storage_item not in service_names:
                return storage_item



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

    if self.in_yard_container_booking:
        frappe.db.set_value("In Yard Container Booking", self.in_yard_container_booking, "sales_order", sales_order.name)

    frappe.msgprint(f"Sales Order <b>{sales_order.name}</b> created successfully", alert=True)
    return sales_order.name
