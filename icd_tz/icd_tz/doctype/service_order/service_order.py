# Copyright (c) 2024, Nathan Kagoro and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from icd_tz.icd_tz.api.utils import validate_cf_agent, validate_draft_doc

class ServiceOrder(Document):
	def before_insert(self):
		self.set_missing_values()
		self.get_services()
	
	def after_insert(self):
		self.update_container_inspection()

	def before_save(self):
		if not self.company:
			self.company = frappe.defaults.get_user_default("Company")
	
	def validate(self):
		validate_draft_doc("Container Inspection", self.container_inspection)
		validate_cf_agent(self)

	def on_submit(self):
		self.create_getpass()

	def set_missing_values(self):
		if self.container_no:
			container_doc = frappe.get_doc("Container", self.container_no)
			container_reception_doc = frappe.get_doc("Container Reception", container_doc.container_reception)

			self.vessel_name = container_reception_doc.ship
			self.port = container_reception_doc.port
		
			if container_doc.place_of_destination and "TZ" in container_doc.place_of_destination:
				self.destination = "Local"
				self.country = "Local"
			else:
				self.destination = container_doc.place_of_destination
				self.country = ""
	
	def get_services(self):
		self.get_transport_services()
		self.get_shore_handling_services()
		self.get_strip_services()
		self.get_custom_verification_services()
		self.get_storage_services()
		self.get_removal_services()
		self.get_corridor_services()
		self.get_other_charges()

	def get_transport_services(self):
		if self.container_no:
			container_reception = frappe.db.get_value(
				"Container",
				self.container_no,
				"container_reception"
			)
			has_transport_charges = has_shore_handling_charges = frappe.db.get_value(
				"Container Reception",
				container_reception,
				"has_transport_charges"
			)

			if has_transport_charges == "Yes":
				service_names = [row.get("service") for row in self.get("services")]
				transport_item = frappe.db.get_single_value("ICD TZ Settings", "transport_item")
				
				if transport_item not in service_names:
					self.append("services", {
						"service": transport_item
					})
	
	def get_shore_handling_services(self):
		if self.container_no:
			container_reception = frappe.db.get_value(
				"Container",
				self.container_no,
				"container_reception"
			)
			has_shore_handling_charges, discharged_at = frappe.db.get_value(
				"Container Reception",
				container_reception,
				["has_shore_handling_charges", "discharged_at"]
			)
			self.discharged_at = discharged_at
			
			if has_shore_handling_charges == "Yes":
				service_names = [row.get("service") for row in self.get("services")]
				shore_handling_item = frappe.db.get_single_value("ICD TZ Settings", "shore_handling_item")
				
				if shore_handling_item not in service_names:
					self.append("services", {
						"service": shore_handling_item,
						"remarks": f"Size: {self.container_size}, Destination: {self.destination}, DischargedAt: {self.discharged_at}"
					})
	
	def get_custom_verification_services(self):
		if not self.get("container_inspection"):
			return
		
		has_custom_verification_charges = frappe.db.get_value(
			"In Yard Container Booking",
            {"container_inspection": self.get("container_inspection")},
            "has_custom_verification_charges"
		)
		if has_custom_verification_charges == "Yes":
			service_names = [row.get("service") for row in self.get("services")]
			verification_item = frappe.db.get_single_value("ICD TZ Settings", "custom_verification_item")
			
			if verification_item not in service_names:
				self.append("services", {
					"service": verification_item
				})

	def get_strip_services(self):
		if not self.get("container_inspection"):
			return
		
		has_stripping_charges = frappe.db.get_value(
            "In Yard Container Booking",
            {"container_inspection": self.get("container_inspection")},
            "has_stripping_charges"
        )
		if has_stripping_charges == "Yes":
			service_names = [row.get("service") for row in self.get("services")]
			booking_item = frappe.db.get_single_value("ICD TZ Settings", "in_yard_booking_item")
			
			if booking_item not in service_names:
				self.append("services", {
					"service": booking_item
				})
    
	def get_storage_services(self):
		if not self.get("container_no"):
			return

		has_storage_charges = frappe.db.get_value(
            "Container", self.get("container_no"), "days_to_be_billed"
        )
		if has_storage_charges > 0:
			service_names = [row.get("service") for row in self.get("services")]
			storage_item = frappe.db.get_single_value("ICD TZ Settings", "container_storage_item")
            
			if storage_item not in service_names:
				self.append("services", {
					"service": storage_item
				})
	
	def get_removal_services(self):
		if self.container_no:
			container_doc = frappe.get_doc("Container", self.container_no)
			if container_doc.has_paid_for_removal_charges == 0:
				service_names = [row.get("service") for row in self.get("services")]
				removal_item = frappe.db.get_single_value("ICD TZ Settings", "removal_item")
				
				if removal_item not in service_names:
					self.append("services", {
						"service": removal_item
					})
	
	def get_corridor_services(self):
		if self.container_no:
			container_doc = frappe.get_doc("Container", self.container_no)
			if container_doc.has_paid_for_corridor_levy == 0:
				service_names = [row.get("service") for row in self.get("services")]
				corridor_item = frappe.db.get_single_value("ICD TZ Settings", "corridor_levy_item")
				
				if corridor_item not in service_names:
					self.append("services", {
						"service": corridor_item
					})
	
	def get_other_charges(self):
		if not self.container_inspection:
			return
		
		service_names = [row.get("service") for row in self.get("services")]
		c_rec_doc = frappe.get_doc("Container Inspection", self.container_inspection)

		for d in c_rec_doc.get("services"):
			if d.get("service") not in service_names:
				self.append("services", {
					"service": d.get("service")
				})		


	def update_container_inspection(self):
		if not self.container_inspection:
			return
		
		frappe.db.set_value(
			"Container Inspection",
			self.container_inspection,
			"service_order",
			self.name
		)
	
	def create_getpass(self):
		"""
		Create a Get pass document
		"""
		booking_id = frappe.db.get_value(
			"In Yard Container Booking", 
			{"container_inspection": self.container_inspection},
			"name"
		)
		
		getpass = frappe.new_doc("Gate Pass")
		getpass.update({
			"booking_id": booking_id,
			"service_order": self.name,
			"c_and_f_company": self.c_and_f_company,
			"clearing_agent": self.clearing_agent,
			"consignee": self.consignee,
			"container_no": self.container_no,
		})
		getpass.save(ignore_permissions=True)
		getpass.reload()

		self.db_set("get_pass", getpass.name)
		self.reload()