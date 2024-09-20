# Copyright (c) 2024, Nathan Kagoro and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from icd_tz.icd_tz.api.utils import validate_cf_agent, validate_draft_doc

class ServiceOrder(Document):
	def after_insert(self):
		self.update_container_inspection()

	def before_save(self):
		if not self.company:
			self.company = frappe.defaults.get_user_default("Company")
	
	def validate(self):
		validate_draft_doc("Container Inspection", self.container_inspection)
		validate_cf_agent(self)

	@frappe.whitelist()
	def get_strip_services(self):
		if isinstance(self, str):
			self = frappe.parse_json(self)
		
		if not self.get("container_inspection"):
			return
		
		has_stripping_charges = frappe.db.get_value(
            "In Yard Container Booking",
            {"container_inspection": self.get("container_inspection")},
            "has_stripping_charges"
        )
		if has_stripping_charges == "Yes":
			service_names = []
			for row in self.get("services"):
				service_names.append(row.get("service"))
			
			booking_item = frappe.db.get_single_value("ICD TZ Settings", "in_yard_booking_item")
			
			if booking_item not in service_names:
				return booking_item
    
	@frappe.whitelist()
	def get_storage_services(self):
		if isinstance(self, str):
			self = frappe.parse_json(self)
        
		if not self.get("container_no"):
			return

		has_storage_charges = frappe.db.get_value(
            "Container", container_no, "days_to_be_billed"
        )
		if has_storage_charges > 0:
			service_names = []
			for row in self.get("services"):
				service_names.append(row.get("service"))
            
			storage_item = frappe.db.get_single_value("ICD TZ Settings", "container_storage_item")
            
			if storage_item not in service_names:
				return storage_item

	def update_container_inspection(self):
		if not self.container_inspection:
			return
		
		frappe.db.set_value(
			"Container Inspection",
			self.container_inspection,
			"service_order",
			self.name
		)