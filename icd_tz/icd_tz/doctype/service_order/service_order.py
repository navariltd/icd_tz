# Copyright (c) 2024, elius mgani and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from icd_tz.icd_tz.api.utils import validate_cf_agent, validate_draft_doc
from icd_tz.icd_tz.api.sales_order import get_container_days_to_be_billed

class ServiceOrder(Document):
	def before_insert(self):
		self.set_missing_values()
		self.validate_draft_references()
		self.get_services()
	
	def after_insert(self):
		frappe.db.set_value(
            "Container",
            self.container_id,
            "status",
            "At Payments"
        )

	def before_save(self):
		if not self.company:
			self.company = frappe.defaults.get_user_default("Company")
	
	def validate(self):
		validate_cf_agent(self)

	def on_submit(self):
		self.create_getpass()

	def set_missing_values(self):
		if self.container_id:
			container_doc = frappe.get_doc("Container", self.container_id)

			self.manifest = container_doc.manifest
			self.vessel_name = container_doc.ship
			self.port = container_doc.port_of_destination
			self.place_of_destination = container_doc.place_of_destination
			self.country_of_destination = container_doc.country_of_destination
			self.consignee = container_doc.consignee
			if not self.m_bl_no:
				self.m_bl_no = container_doc.m_bl_no
			if not self.h_bl_no and container_doc.has_hbl == 1:
				self.h_bl_no = container_doc.h_bl_no

			inspection_info = frappe.get_cached_value(
				"Container Inspection",
				{"container_id": self.container_id},
				["name", "c_and_f_company", "clearing_agent"],
				as_dict=True
			)

			if inspection_info:
				self.c_and_f_company = inspection_info.c_and_f_company
				self.clearing_agent = inspection_info.clearing_agent

			if not self.c_and_f_company or not self.clearing_agent:
				booking_info = frappe.get_cached_value(
					"In Yard Container Booking",
					{"container_id": self.container_id},
					["name", "c_and_f_company", "clearing_agent"],
					as_dict=True
				)
				if booking_info:
					self.c_and_f_company = booking_info.c_and_f_company
					self.clearing_agent = booking_info.clearing_agent
	
	def validate_draft_references(self):
		draft_inspections = frappe.db.get_all(
			"Container Inspection",
			filters={"container_id": self.container_id, "docstatus": 0}
		)
		if len(draft_inspections) > 0:
			frappe.throw(f"There are <b>{len(draft_inspections)}</b> draft Container Inspection(s) for Container: {self.container_no}, Please submit them to continue")
		
		draft_bookings = frappe.db.get_all(
			"In Yard Container Booking",
			filters={"container_id": self.container_id, "docstatus": 0}
		)
		if len(draft_bookings) > 0:
			frappe.throw(f"There are <b>{len(draft_bookings)}</b> draft In Yard Container Booking(s) for Container: {self.container_no}, Please submit them to continue")

	def get_services(self):
		settings_doc = frappe.get_cached_doc("ICD TZ Settings")

		self.get_reception_services(settings_doc)
		self.get_booking_services(settings_doc)
		self.get_corridor_services(settings_doc)
		self.get_other_charges()		

	def get_reception_services(self, settings_doc):
		if not self.container_id:
			return
		
		container_reception = frappe.db.get_value(
			"Container",
			self.container_id,
			"container_reception"
		)
		reception_details = frappe.get_cached_value(
			"Container Reception",
			container_reception,
			[
				"cargo_type", "has_transport_charges", "t_sales_invoice",
				"has_shore_handling_charges", "s_sales_invoice"
			],
			as_dict=True
		)
		if not reception_details:
			return

		service_names = [row.get("service") for row in self.get("services")]
		if (
			not reception_details.t_sales_invoice and
			reception_details.has_transport_charges == "Yes"
		):
			transport_item = None

			if self.container_status == "LCL":
				for row in settings_doc.loose_types:
					if row.service_type == "Transport":
						transport_item = row.service_name
						break
			else:
				for row in settings_doc.service_types:
					if (
						row.service_type == "Transport" and 
						row.cargo_type == reception_details.cargo_type
					):
						transport_item = row.service_name
						break
			
			if not transport_item:
				frappe.throw("Transport Pricing Criteria is not set in ICD TZ Settings, Please set it to continue")
			
			if transport_item and transport_item not in service_names:
				self.append("services", {
					"service": transport_item,
					"qty": 1
				})
		
		if (
			not reception_details.s_sales_invoice and
			reception_details.has_shore_handling_charges == "Yes"
		):
			shore_handling_item = None

			if self.container_status == "LCL":
				for row in settings_doc.loose_types:
					if (
						row.service_type == "Shore"
						and row.cargo_type == reception_details.cargo_type
					):
						shore_handling_item = row.service_name
						break
			else:
				for row in settings_doc.service_types:
					if (
						row.service_type == "Shore" and
						row.cargo_type == reception_details.cargo_type and
						row.port == self.port
					):
						if "2" in str(row.size)[0] and "2" in str(self.container_size)[0]:
							shore_handling_item = row.service_name
							break

						elif "4" in str(row.size)[0] and "4" in str(self.container_size)[0]:
							shore_handling_item = row.service_name
							break

						else:
							continue
			
			if not shore_handling_item:
				frappe.throw(
					f"Shore Handling Pricing Criteria for Size: {self.container_size}, Port: {self.port} and Cargo Type: {reception_details.cargo_type} is not set in ICD TZ Settings, Please set it to continue"
				)
			
			service_names = [row.get("service") for row in self.get("services")]
			if shore_handling_item and shore_handling_item not in service_names:
				self.append("services", {
					"service": shore_handling_item,
					"qty": 1,
					"remarks": f"Size: {self.container_size}, Cargo Type: {reception_details.cargo_type}, Port: {self.port}"
				})
		
	def get_booking_services(self, settings_doc):
		if not self.container_id:
			return

		booking_details = frappe.db.get_all(
			"In Yard Container Booking",
            {"container_id": self.container_id, "docstatus": 1},
            ["has_stripping_charges", "s_sales_invoice", "has_custom_verification_charges", "cv_sales_invoice"],
		)
		if len(booking_details) == 0:
			return
		
		strips = []
		verifications = []
		for booking in booking_details:
			if (
				not booking.s_sales_invoice and
				booking.has_stripping_charges == "Yes"
			):
				stripping_item = None

				if self.container_status == "LCL":
					for row in settings_doc.loose_types:
						if row.service_type == "Stripping":
							stripping_item = row.service_name
							break
				else:
					for row in settings_doc.service_types:
						if row.service_type == "Stripping":
							if "2" in str(row.size)[0] and "2" in str(self.container_size)[0]:
								stripping_item = row.service_name
								break

							elif "4" in str(row.size)[0] and "4" in str(self.container_size)[0]:
								stripping_item = row.service_name
								break

							else:
								continue
						
				if not stripping_item:
					frappe.throw(f"Stripping Pricing Criteria for Size: {self.container_size} is not set in ICD TZ Settings, Please set it to continue")
				
				strips.append(stripping_item)
			
			if (
				not booking.cv_sales_invoice and
				booking.has_custom_verification_charges == "Yes"
			):
				verification_item = None
				if self.container_status == "LCL":
					for row in settings_doc.loose_types:
						if row.service_type == "Verification":
							verification_item = row.service_name
							break
				else:
					for row in settings_doc.service_types:
						if row.service_type == "Verification":
							if "2" in str(row.size)[0] and "2" in str(self.container_size)[0]:
								verification_item = row.service_name
								break

							elif "4" in str(row.size)[0] and "4" in str(self.container_size)[0]:
								verification_item = row.service_name
								break

							else:
								continue
						
				if not verification_item:
					frappe.throw(f"Custom Verification Pricing criteria for Size: {self.container_size} is not set in ICD TZ Settings, Please set it to continue")
				
				verifications.append(verification_item)
		
		if len(strips) > 0:
			self.append("services", {
				"service": strips[0],
				"qty": len(strips),
				"remarks": "Having more than one booking" if len(strips) > 1 else ""
			})
		
		if len(verifications) > 0:
			self.append("services", {
				"service": verifications[0],
				"qty": len(verifications),
				"remarks": "Having more than one booking" if len(verifications) > 1 else ""
			})
	
	def get_corridor_services(self, settings_doc):
		if not self.container_id:
			return
		
		container_doc = frappe.get_doc("Container", self.container_id)
		if container_doc.has_corridor_levy_charges != "Yes":
			return
		
		if container_doc.c_sales_invoice:
			return
		
		corridor_item = None
		service_names = [row.get("service") for row in self.get("services")]

		if self.container_status == "LCL":
			for row in settings_doc.loose_types:
				if row.service_type == "Levy":
					corridor_item = row.service_name
					break
		else:
			for row in settings_doc.service_types:
				if row.service_type == "Levy":
					if "2" in str(row.size)[0] and "2" in str(self.container_size)[0]:
						corridor_item = row.service_name
						break

					elif "4" in str(row.size)[0] and "4" in str(self.container_size)[0]:
						corridor_item = row.service_name
						break

					else:
						continue
		
		if not corridor_item:
			frappe.throw(f"Corridor Levy Pricing Criteria for Size: {self.container_size} is not set in ICD TZ Settings, Please set it to continue")
		
		if corridor_item and corridor_item not in service_names:
			self.append("services", {
				"service": corridor_item,
				"qty": 1
			})
	
	def get_other_charges(self):
		if not self.container_id:
			return
		
		service_names = [row.get("service") for row in self.get("services")]
		inspeactions = frappe.db.get_all(
			"Container Inspection",
			{"container_id": self.container_id, "docstatus": 1},
			["name"]
		)
		if len(inspeactions) == 0:
			return

		for inspection in inspeactions:
			inspection_doc = frappe.get_doc("Container Inspection", inspection.name)

			for d in inspection_doc.get("services"):
				if d.get("sales_invoice"):
					continue

				if "verification" in str(d.get("service")).lower():
					continue
				
				if d.get("service") and d.get("service") not in service_names:
					self.append("services", {
						"service": d.get("service"),
						"qty": 1
					})
	
	def create_getpass(self):
		"""
		Create a Get pass document
		"""
		exist_get_pass = frappe.db.get_all(
			"Gate Pass",
			filters={
				"manifest": self.manifest,
				"container_id": self.container_id
			}
		)
		if len(exist_get_pass) > 0:
			self.db_set("get_pass", exist_get_pass[0].name)
			self.reload()
			return

		inspection_location = frappe.db.get_value(
			"In Yard Container Booking", 
			{"container_id": self.container_id},
			"inspection_location"
		)
		
		getpass = frappe.new_doc("Gate Pass")
		getpass.update({
			"manifest": self.manifest,
			"c_and_f_company": self.c_and_f_company,
			"clearing_agent": self.clearing_agent,
			"consignee": self.consignee,
			"container_id": self.container_id,
			"container_no": self.container_no,
			"inspection_location": inspection_location,
		})
		getpass.save(ignore_permissions=True)
		getpass.reload()

		self.db_set("get_pass", getpass.name)
		self.reload()


@frappe.whitelist()
def create_bulk_service_orders(data):
	data = frappe.parse_json(data)

	filters = {}
	if data.get("m_bl_no"):
		filters["m_bl_no"] = data.get("m_bl_no")
		filters["has_hbl"] = 0
	elif data.get("h_bl_no"):
		filters["h_bl_no"] = data.get("h_bl_no")
		filters["has_hbl"] = 1

	containers = frappe.db.get_all(
		"Container",
		filters=filters,
        fields=["name"]
	)

	msg = ""
	if data.get("m_bl_no"):
		msg = f"M BL No: <b>{data.get('m_bl_no')}</b>"
	elif data.get("h_bl_no"):
		msg = f"H BL No: <b>{data.get('h_bl_no')}</b>"

	if len(containers) == 0:
		frappe.msgprint(f"No Containers found for {msg}")
		return
    
	count = 0
	for container in containers:
		doc = frappe.new_doc("Service Order")
		doc.container_id = container.name
		doc.m_bl_no = data.get("m_bl_no")
		doc.h_bl_no = data.get("h_bl_no")
        
		doc.flags.ignore_permissions = True
		doc.save()
		doc.reload()

		if doc.get("name"):
			count += 1

	return count
