# Copyright (c) 2024, elius mgani and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import nowdate
from frappe.model.document import Document
from icd_tz.icd_tz.api.utils import validate_cf_agent, validate_draft_doc

class ContainerInspection(Document):
    def after_insert(self):
        self.update_in_yard_booking()
    
    def before_save(self):
        if not self.company:
            self.company = frappe.defaults.get_user_default("Company")
    
    def validate(self):
        validate_draft_doc("In Yard Container Booking", self.in_yard_container_booking)
        validate_cf_agent(self)
    
    def on_submit(self):
        self.update_container_doc()
    
    def update_in_yard_booking(self):
        if not self.in_yard_container_booking:
            return
        
        frappe.db.set_value(
            "In Yard Container Booking",
            self.in_yard_container_booking,
            "container_inspection",
            self.name
        )
    
    def update_container_doc(self):
        if not self.container_no:
            return
        
        container_doc = frappe.get_doc("Container", self.container_no)
        container_doc.current_location = self.container_location
        container_doc.save(ignore_permissions=True)
