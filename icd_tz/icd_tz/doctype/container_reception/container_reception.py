# Copyright (c) 2024, Nathan Kagoro and contributors
# For license information, please see license.txt

import frappe
from frappe.query_builder import DocType
from frappe.model.document import Document
from frappe.utils import get_link_to_form, nowdate

cr = DocType("Container Reception")

class ContainerReception(Document):
	def before_save(self):
		if not self.company:
			self.company = frappe.defaults.get_user_default("Company")
		
	def validate(self):
		self.validate_duplicate_cmo()
	
	def on_submit(self):
		self.create_container()

	def validate_duplicate_cmo(self):
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
		container.volume = self.cbm
		container.weght = self.weight
		container.seal_no_1 = self.seal_no_1
		container.seal_no_2 = self.seal_no_2
		container.port_of_origin = self.port
		container.port_of_destination = self.port
		container.arrival_date = nowdate()
		container.save(ignore_permissions=True)

		return container.name

@frappe.whitelist()
def get_container_details(manifest, container_no):
	"""Get the details of a container based on the container no and manifest"""

	container = frappe.get_all(
		"Containers Detail",
		filters={"parent": manifest, "container_no": container_no},
		fields=["*"]
	)

	if len(container) > 0:
		return container[0]