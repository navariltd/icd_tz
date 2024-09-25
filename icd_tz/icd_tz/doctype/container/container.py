# Copyright (c) 2024, elius mgani and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, getdate, add_days

class Container(Document):
	def before_save(self):
		if self.container_no and self.container_reception:
			self.update_container_details()

		self.update_billed_days()
	

	def update_container_details(self):
		"""Update the container details from the Container Reception, Containers Detail and Container Movement Order"""

		if self.customs_status == "Cleared":
			return

		container_reception = frappe.get_doc("Container Reception", self.container_reception)
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
				["place_of_destination", "place_of_delivery", "port_of_loading", "cosignee_name"],
				as_dict=True
			)
			if masterbi_info:
				if not self.place_of_destination:
					self.place_of_destination = masterbi_info.place_of_destination
				if not self.place_of_delivery:
					self.place_of_delivery = masterbi_info.place_of_delivery
				if not self.port_of_loading:
					self.port_of_loading = masterbi_info.port_of_loading
				if not self.consignee:
					self.consignee = masterbi_info.cosignee_name


		if len(self.container_dates) == 0:
			self.append("container_dates", {
				"date": self.arrival_date,
			})

	def update_billed_days(self):
		"""Update the billed days of the container"""
		
		if self.customs_status == "Cleared":
			return
		
		if len(self.container_dates) > 0:
			self.total_days = len(self.container_dates)
			self.no_of_billable_days = len([row for row in self.container_dates if row.is_billable == 1])
			self.no_of_unbilled_days = len([row for row in self.container_dates if row.is_billable == 0])
			self.days_to_be_billed = len([row for row in self.container_dates if row.is_billable == 1 and not row.sales_invoice])
			self.no_of_billed_days = len([row for row in self.container_dates if row.sales_invoice])


def daily_update_date_container_stay():
	containers = frappe.get_all("Container", filters={"customs_status": ["!=", "Cleared"]})

	for item in containers:
		try:
			doc = frappe.get_doc("Container", item.name)
			container_dates_len = len(doc.container_dates)
			if container_dates_len > 0:
				last_row = doc.container_dates[container_dates_len - 1]
				if getdate(last_row.date) != getdate(nowdate()):
					new_row = doc.append("container_dates", {})
					new_row.date = add_days(last_row.date, 1)
			elif container_dates_len == 0:
				new_row = doc.append("container_dates", {})
				new_row.date = doc.arrival_date
			
			doc.save(ignore_permissions=True)
			frappe.db.commit()
		except Exception:
			frappe.log_error(
				str(f"<b>{item.name}</b> Daily Update Container Dates"),
				frappe.get_traceback()
			)
			continue

