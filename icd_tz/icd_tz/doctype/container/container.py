# Copyright (c) 2024, elius mgani and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, getdate, add_days
from icd_tz.icd_tz.doctype.container_reception.container_reception import get_place_of_destination

class Container(Document):
	def before_save(self):
		if self.container_no and self.container_reception:
			container_reception = frappe.get_doc("Container Reception", self.container_reception)

			self.update_container_details(container_reception)
			self.validate_place_of_destination()
			self.update_container_reception(container_reception)
		
		self.update_billed_days()
		self.update_billed_details()
		self.check_corridor_levy_eligibility()
		self.check_removal_charges_elibility()

	def update_container_details(self, container_reception):
		"""Update the container details from the Container Reception, Containers Detail and Container Movement Order"""

		if self.customs_status == "Cleared":
			return

		if not self.customs_status:
			self.customs_status = "Pending"
		if not self.status:
			self.status = "In Yard"
		if not self.size:
			self.size = container_reception.size
		if not self.volume:
			self.volume = container_reception.volume
		if not self.weight:
			self.weight = container_reception.weight
		if not self.seal_no_1:
			self.seal_no_1 = container_reception.seal_no_1
		if not self.seal_no_2:
			self.seal_no_2 = container_reception.seal_no_2
		if not self.seal_no_3:
			self.seal_no_3 = container_reception.seal_no_3
		if not self.port_of_destination:
			self.port_of_destination = container_reception.port
		if not self.original_location:
			self.original_location = container_reception.container_location
		if not self.current_location:
			self.current_location = container_reception.container_location
		if not self.place_of_destination:
			self.place_of_destination = container_reception.place_of_destination
		if not self.country_of_destination:
			self.country_of_destination = container_reception.country_of_destination
		if not self.company:
			self.company = container_reception.company

		container_info = frappe.db.get_value(
			"Containers Detail", 
			{"parent": container_reception.manifest, "container_no": self.container_no}, 
			["type_of_container", "m_bl_no", "freight_indicator", "no_of_packages", "package_unit", "volume_unit", "weight_unit"],
			as_dict=True
		)

		if container_info:
			if not self.type_of_container:
				self.type_of_container = container_info.type_of_container
			if not self.m_bl_no:
				self.m_bl_no = container_info.m_bl_no
			if not self.freight_indicator:
				self.freight_indicator = container_info.freight_indicator
			if not self.no_of_packages:
				self.no_of_packages = container_info.no_of_packages
			if not self.package_unit:
				self.package_unit = container_info.package_unit
			if not self.freight_indicator:
				self.freight_indicator = container_info.freight_indicator
			if not self.volume_unit:
				self.volume_unit = container_info.volume_unit
			if not self.weight_unit:
				self.weight_unit = container_info.weight_unit
		
		if container_info.m_bl_no:
			masterbi_info = frappe.db.get_value(
				"MasterBI", 
				{"parent": container_reception.manifest, "m_bl_no": container_info.m_bl_no}, 
				["place_of_destination", "place_of_delivery", "port_of_loading", "cosignee_name", "shipping_agent_code", "shipping_agent_name", "cargo_description"],
				as_dict=True
			)
			if masterbi_info:
				if not self.abbr_for_destination:
					self.abbr_for_destination = masterbi_info.place_of_destination
				if not self.place_of_delivery:
					self.place_of_delivery = masterbi_info.place_of_delivery
				if not self.port_of_loading:
					self.port_of_loading = masterbi_info.port_of_loading
				if not self.consignee:
					self.consignee = masterbi_info.cosignee_name
				if not self.cargo_description:
					self.cargo_description = masterbi_info.cargo_description
				if not self.sline_code:
					self.sline = masterbi_info.shipping_agent_code
				if not self.sline:
					self.sline = masterbi_info.shipping_agent_name


		if len(self.container_dates) == 0:
			self.append("container_dates", {
				"date": self.arrival_date,
			})

	def update_billed_days(self):
		setting_doc = frappe.get_doc("ICD TZ Settings")

		no_of_free_days = 0
		no_of_single_days = 0
		no_of_double_days = 0
		for d in setting_doc.storage_days:
			if d.destination == self.place_of_destination:
				if d.charge == "Free":
					no_of_free_days = d.get("to") - d.get("from") + 1

				elif d.charge == "Single":
					no_of_single_days = d.get("to") - d.get("from") + 1

				elif d.charge == "Double":
					no_of_double_days = d.get("to") - d.get("from") + 1
		
		free_count = 0
		charge_count = 0
		for row in self.container_dates:
			if free_count < no_of_free_days:
				row.is_free = 1
				row.is_billable = 0
				free_count += 1
			
			elif row.is_billable == 1  and row.is_free == 0:
				charge_count += 1
		
		if charge_count == 0:
			self.has_single_charge = 0
			self.has_double_charge = 0
		
		elif charge_count > 0 and charge_count <= no_of_single_days:
			self.has_single_charge = 1
			self.has_double_charge = 0
		
		elif charge_count > no_of_single_days:
			self.has_single_charge = 1
			self.has_double_charge = 1
		
	def update_billed_details(self):
		"""Update the billed days of the container"""
		
		if self.customs_status == "Cleared":
			return
		
		if len(self.container_dates) > 0:
			no_of_free_days = 0
			no_of_billable_days = 0
			no_of_writeoff_days = 0
			no_of_billed_days = 0

			for row in self.container_dates:
				if row.is_billable == 0 and row.is_free == 1:
					no_of_free_days += 1
					
				if row.is_billable == 1 and row.is_free == 0:
					no_of_billable_days += 1
				
				if row.is_billable == 0 and row.is_free == 0:
					no_of_writeoff_days += 1
				
				if row.sales_invoice:
					no_of_billed_days += 1

			
			self.total_days = len(self.container_dates)
			self.no_of_free_days = no_of_free_days
			self.no_of_billable_days = no_of_billable_days
			self.no_of_writeoff_days = no_of_writeoff_days
			self.no_of_billed_days = no_of_billed_days
			self.days_to_be_billed = no_of_billable_days - no_of_billed_days	

	def check_removal_charges_elibility(self):
		"""Check if the container is eligible to remove charges"""

		if self.r_sales_invoice:
			self.has_removal_charges = "No"
		elif self.days_to_be_billed > 0:
			self.has_removal_charges = "Yes"
		elif self.days_to_be_billed <= 0:
			if self.has_single_charge == 1 or self.has_double_charge == 1:
				self.has_removal_charges = "Yes"
			else:
				self.has_removal_charges = "No"


	def check_corridor_levy_eligibility(self):
		"""Check if the container is eligible for Corridor Levy payments"""

		if not self.country_of_destination:
			self.has_corridor_levy_charges = "No"
			return
		
		is_eligible_for_corridor_levy_payments = False
		icd_settings = frappe.get_doc("ICD TZ Settings")
		for row in icd_settings.countries:
			if row.country == self.country_of_destination:
				is_eligible_for_corridor_levy_payments = True
				break
		
		if is_eligible_for_corridor_levy_payments:
			if self.c_sales_invoice:
				self.has_corridor_levy_charges = "No"
			elif self.days_to_be_billed > 0:
				self.has_corridor_levy_charges = "Yes"
			elif self.days_to_be_billed <= 0:
				if self.has_single_charge == 1 or self.has_double_charge == 1:
					self.has_corridor_levy_charges = "Yes"
				else:
					self.has_corridor_levy_charges = "No"
		else:
			self.has_corridor_levy_charges = "No"
	
	def update_container_reception(self, container_reception):
		if self.place_of_destination and self.place_of_destination != container_reception.place_of_destination:
			container_reception.db_set("place_of_destination", self.place_of_destination)
		
		if self.country_of_destination and self.country_of_destination != container_reception.country_of_destination:
			container_reception.db_set("country_of_destination", self.country_of_destination)
		
	def validate_place_of_destination(self):
		if not self.place_of_destination:
			return
		
		places = get_place_of_destination()
		places_str = ", ".join(places)
		if self.place_of_destination not in places:
			frappe.throw(f"Invalid Place of Destination <b>{self.place_of_destination}</b>, valid places are: <b>{places_str}</b>")

def daily_update_date_container_stay():
    containers = frappe.get_all("Container", filters={"customs_status": ["!=", "Cleared"]})

    for item in containers:
        try:
            doc = frappe.get_doc("Container", item.name)
            current_date = getdate(nowdate())
            container_dates_len = len(doc.container_dates)

            if container_dates_len > 0:
                last_row = doc.container_dates[container_dates_len - 1]
                last_date = getdate(last_row.date)

                while last_date < current_date:
                    new_row = doc.append("container_dates", {})
                    last_date = add_days(last_date, 1)
                    new_row.date = last_date

            elif container_dates_len == 0:
                start_date = doc.arrival_date
                if start_date:
                    while getdate(start_date) <= current_date:
                        new_row = doc.append("container_dates", {})
                        new_row.date = start_date
                        start_date = add_days(start_date, 1)

            doc.save(ignore_permissions=True)

        except Exception:
            frappe.log_error(
                str(f"<b>{item.name}</b> Daily Update Container Dates"),
                frappe.get_traceback()
            )
            continue

