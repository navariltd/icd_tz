# Copyright (c) 2024, elius mgani and contributors
# For license information, please see license.txt

import frappe
from frappe.query_builder import DocType
from frappe.model.document import Document
from frappe.utils import get_link_to_form, nowdate, getdate, add_days

cr = DocType("Container Reception")

class ContainerReception(Document):
	def before_save(self):
		if not self.company:
			self.company = frappe.defaults.get_user_default("Company")
		
	def validate(self):
		self.validate_duplicate_cr()
	
	def before_submit(self):
		if not self.clerk:
			frappe.throw("Clerk is missing, Please select clerk to proceed..!")
	
	def on_submit(self):
		self.create_container()
		self.update_container_storage_days()

	def validate_duplicate_cr(self):
		"""Validate that there is no duplicate Container Reception based on Container Movement Order (CMO)"""
		if self.movement_order:
			duplicates = (
				frappe.qb.from_(cr)
				.select(
					cr.name
				)
				.where(
					(cr.movement_order == self.movement_order)
					& (cr.name != self.name)
				)
			).run(as_dict=True)

			if len(duplicates) > 0:
				url = get_link_to_form("Container Reception", duplicates[0].name)
				frappe.throw(
					f"Another Container Reception with the same Movement Order already exists: <a href='{url}'><b>{duplicates[0].name}</b></a>"
				)

	def create_container(self):
		"""Create a Container record from the Container Reception"""

		container = frappe.new_doc("Container")
		container.container_reception = self.name
		container.container_no = self.container_no
		container.size = self.size
		container.volume = self.volume
		container.weght = self.weight
		container.seal_no_1 = self.seal_no_1
		container.seal_no_2 = self.seal_no_2
		container.seal_no_3 = self.seal_no_3
		container.port_of_destination = self.port
		container.arrival_date = self.ship_dc_date
		container.received_date = self.received_date
		container.original_location = self.container_location
		container.current_location = self.container_location
		container.place_of_destination = self.place_of_destination
		container.country_of_destination = self.country_of_destination
		container.manifest = self.manifest
		container.movement_order = self.movement_order
		container.m_bl_no = self.m_bl_no
		container.container_count = self.container_count
		container.status = "In Yard"

		container.append("container_dates", {
			"date": self.received_date,
		})
		container.save(ignore_permissions=True)

		return container.name
	
	def update_container_storage_days(self):
		"""Update the storage days of the containers based on the current received date and m_bl_no"""

		records = (
			frappe.qb.from_(cr)
			.select(
				cr.name
			)
			.where(
				(cr.name != self.name)
				& (cr.m_bl_no == self.m_bl_no)
				& (cr.manifest == self.manifest)
				& (cr.received_date != self.received_date)
			)
		).run(as_dict=True)

		if len(records) == 0:
			return
		
		for record in records:
			frappe.db.set_value(
				"Container Reception",
				record.name,
				"received_date",
				self.received_date,
				update_modified=False
			)

			container_id = frappe.db.get_value(
				"Container",
				{"container_reception": record.name},
				"name"
			)
			if not container_id:
				continue

			container_doc = frappe.get_doc("Container", container_id)
			container_doc.container_dates = []
			container_doc.arrival_date = self.ship_dc_date
			container_doc.received_date = self.received_date
			container_doc.append("container_dates", {
				"date": self.received_date,
			})
			container_doc.save(ignore_permissions=True)


@frappe.whitelist()
def get_container_details(manifest, container_no):
	"""Get the details of a container based on the container no and manifest"""

	container = frappe.get_all(
		"Containers Detail",
		filters={"parent": manifest, "container_no": container_no},
		fields=["*"]
	)

	if len(container) > 0:
		container_row = container[0]
		container_row["abbr_for_destination"] = frappe.db.get_value(
			"Master BL", 
			{"parent": manifest, "m_bl_no": container_row.m_bl_no}, 
			"place_of_destination"
		)
		return container_row

@frappe.whitelist()
def get_place_of_destination():
	destinations = []

	icd_doc = frappe.get_doc("ICD TZ Settings")

	for row in icd_doc.storage_days:
		destinations.append(row.destination)
	
	return set(destinations)