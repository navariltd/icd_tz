# Copyright (c) 2024, elius mgani and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from icd_tz.icd_tz.api.utils import validate_cf_agent, validate_draft_doc
from icd_tz.icd_tz.api.sales_order import get_container_days_to_be_billed

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
		if self.container_id:
			container_reception = frappe.db.get_value("Container", self.container_id, "container_reception")
			container_reception_doc = frappe.get_doc("Container Reception", container_reception)

			self.vessel_name = container_reception_doc.ship
			self.port = container_reception_doc.port
			self.destination = container_reception_doc.country_of_destination
			self.manifest = container_reception_doc.manifest
			self.discharged_at = container_reception_doc.discharged_at
	
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
		if self.container_id:
			container_reception = frappe.db.get_value(
				"Container",
				self.container_id,
				"container_reception"
			)
			has_transport_charges, t_sales_invoice = frappe.db.get_value(
				"Container Reception",
				container_reception,
				["has_transport_charges", "t_sales_invoice"]
			)
			if t_sales_invoice:
				return

			if has_transport_charges == "Yes":
				service_names = [row.get("service") for row in self.get("services")]
				transport_item = frappe.db.get_single_value("ICD TZ Settings", "transport_item")
				if not transport_item:
					frappe.throw("Transport item is not set in ICD TZ Settings, Please set it to continue")
				
				if transport_item not in service_names:
					self.append("services", {
						"service": transport_item
					})
	
	def get_shore_handling_services(self):
		if self.container_id:
			container_reception = frappe.db.get_value(
				"Container",
				self.container_id,
				"container_reception"
			)
			has_shore_handling_charges, s_sales_invoice = frappe.db.get_value(
				"Container Reception",
				container_reception,
				["has_shore_handling_charges", "s_sales_invoice"]
			)

			if s_sales_invoice:
				return
			
			if has_shore_handling_charges != "Yes":
				return

			shore_handling_item = None
			settings_doc = frappe.get_doc("ICD TZ Settings")
			if self.discharged_at == "Terminal 1":
				if "2" in str(self.container_size)[0]:
					shore_handling_item = settings_doc.get("shore_handling_item_t1_20ft")
					if not shore_handling_item:
						frappe.throw("Shore Handling Item (t1) for 20ft container is not set in ICD TZ setting, Please set it to continue")
				
				if "4" in str(self.container_size)[0]:
					shore_handling_item = settings_doc.get("shore_handling_item_t1_40ft")
					if not shore_handling_item:
						frappe.throw("Shore Handling Item (t1) for 40ft container is not set in ICD TZ setting, Please set it to continue")

			if self.discharged_at == "Terminal 2":
				if "2" in str(self.container_size)[0]:
					shore_handling_item = settings_doc.get("shore_handling_item_t2_20ft")
					if not shore_handling_item:
						frappe.throw("Shore Handling Item (t2) for 20ft container is not set in ICD TZ setting, Please set it to continue")
				
				if "4" in str(self.container_size)[0]:
					shore_handling_item = settings_doc.get("shore_handling_item_t2_40ft")
					if not shore_handling_item:
						frappe.throw("Shore Handling Item (t2) for 40ft container is not set in ICD TZ setting, Please set it to continue")

			service_names = [row.get("service") for row in self.get("services")]
			if shore_handling_item not in service_names:
				self.append("services", {
					"service": shore_handling_item,
					"remarks": f"Size: {self.container_size}, Destination: {self.destination}, DischargedAt: {self.discharged_at}"
				})
	
	def get_custom_verification_services(self):
		if not self.get("container_inspection"):
			return
		
		has_custom_verification_charges, cv_sales_invoice = frappe.db.get_value(
			"In Yard Container Booking",
            {"container_inspection": self.get("container_inspection")},
            "has_custom_verification_charges", "cv_sales_invoice"
		)

		if cv_sales_invoice:
			return
		
		if has_custom_verification_charges == "Yes":
			service_names = [row.get("service") for row in self.get("services")]
			verification_item = frappe.db.get_single_value("ICD TZ Settings", "custom_verification_item")
			if not verification_item:
				frappe.throw("Custom Verification item is not set in ICD TZ Settings, Please set it to continue")
			
			if verification_item not in service_names:
				self.append("services", {
					"service": verification_item
				})

	def get_strip_services(self):
		if not self.get("container_inspection"):
			return
		
		has_stripping_charges, s_sales_invoice = frappe.db.get_value(
            "In Yard Container Booking",
            {"container_inspection": self.get("container_inspection")},
            ["has_stripping_charges", "s_sales_invoice"]
        )

		if s_sales_invoice:
			return
		
		if has_stripping_charges == "Yes":
			service_names = [row.get("service") for row in self.get("services")]
			booking_item = frappe.db.get_single_value("ICD TZ Settings", "in_yard_booking_item")
			if not booking_item:
				frappe.throw("In Yard Booking item is not set in ICD TZ Settings, Please set it to continue")
			
			if booking_item not in service_names:
				self.append("services", {
					"service": booking_item
				})
    
	def get_storage_services(self):
		if not self.get("container_id"):
			return

		container_doc = frappe.get_doc("Container", self.get("container_id"))
		if container_doc.days_to_be_billed == 0:
			return

		service_names = [row.get("service") for row in self.get("services")]

		settings_doc = frappe.get_doc("ICD TZ Settings")
		single_days, double_days = get_container_days_to_be_billed(
			self,
			container_doc,
			settings_doc
		)
		if container_doc.has_single_charge == 1:
			if "2" in str(self.container_size)[0]:
				storage_item = settings_doc.get("storage_item_single_20ft")
				if not storage_item:
					frappe.throw("Storage item (single) for 20ft container is not set in ICD TZ Settings, Please set it to continue")
				
			elif "4" in str(self.container_size)[0]:
				storage_item = settings_doc.get("storage_item_single_40ft")
				if not storage_item:
					frappe.throw("Storage item (single) for 40ft container is not set in ICD TZ Settings, Please set it to continue")
			
			if storage_item not in service_names:
				self.append("services", {
					"service": storage_item,
					"remarks": f"Days: {len(single_days)}, Size: {self.container_size}, Destination: {self.destination}"
				})
		
		if container_doc.has_double_charge == 1:
			if "2" in str(self.container_size)[0]:
				storage_item = settings_doc.get("storage_item_double_20ft")
				if not storage_item:
					frappe.throw("Storage item (double) for 20ft container is not set in ICD TZ Settings, Please set it to continue")
				
			elif "4" in str(self.container_size)[0]:
				storage_item = settings_doc.get("storage_item_double_40ft")
				if not storage_item:
					frappe.throw("Storage item (double) for 40ft container is not set in ICD TZ Settings, Please set it to continue")
			
			if storage_item not in service_names:
				self.append("services", {
					"service": storage_item,
					"remarks": f"Days: {len(double_days)}, Size: {self.container_size}, Destination: {self.destination}"
				})
	
	def get_removal_services(self):
		if not self.container_id:
			return

		container_doc = frappe.get_doc("Container", self.container_id)
		if container_doc.has_removal_charges != "Yes":
			return
		
		if container_doc.r_sales_invoice:
			return

		if container_doc.days_to_be_billed <= 0:
			return
		
		service_names = [row.get("service") for row in self.get("services")]
		removal_item = frappe.db.get_single_value("ICD TZ Settings", "removal_item")
		if not removal_item:
			frappe.throw("Removal item is not set in ICD TZ Settings, Please set it to continue")
		
		if removal_item not in service_names:
			self.append("services", {
				"service": removal_item
			})
	
	def get_corridor_services(self):
		if not self.container_id:
			return
		
		container_doc = frappe.get_doc("Container", self.container_id)
		if container_doc.has_corridor_levy_charges != "Yes":
			return
		
		if container_doc.c_sales_invoice:
			return
		
		if container_doc.days_to_be_billed <= 0:
			return
		
		service_names = [row.get("service") for row in self.get("services")]
		corridor_item = frappe.db.get_single_value("ICD TZ Settings", "corridor_levy_item")
		if not corridor_item:
			frappe.throw("Corridor Levy item is not set in ICD TZ Settings, Please set it to continue")
		
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
			if d.get("sales_invoice"):
				continue
				
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
			"container_id": self.container_id,
			"container_no": self.container_no,
		})
		getpass.save(ignore_permissions=True)
		getpass.reload()

		self.db_set("get_pass", getpass.name)
		self.reload()