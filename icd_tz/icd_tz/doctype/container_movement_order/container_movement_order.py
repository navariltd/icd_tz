# Copyright (c) 2024, Nathan Kagoro and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import get_url_to_form
from frappe.query_builder import DocType
from frappe.model.document import Document

cmo = DocType("Container Movement Order")

class ContainerMovementOrder(Document):
	def validate(self):
		if self.container_number:
			self.validate_container_is_in_manifest()
			self.validate_duplicate_cmo_per_container_number()
	
	
	def validate_container_is_in_manifest(self):
		"""Validate that the container number is in the selected manifest"""

		if not frappe.db.exists(
			"Containers Detail",
			{"parent": self.manifest, "container_no": self.container_number}
		):
			frappe.throw(
				f"Container: {self.container_number} does not belong to the this Manifest: {self.manifest}"
			)
	
	def validate_duplicate_cmo_per_container_number(self):
		"""Validate the duplicate of cmo per container number"""
		duplicates = (
			frappe.qb.from_(cmo)
			.select(
				cmo.name.as_(cmo_id)
			)
			.where(
				(cmo.manifest == self.manifest) &
				(cmo.container_number == self.container_number)
				(cmo.name != self.name)
			)
		).run(as_dict=True)
		if duplicates:
			url = get_url_to_form("Container Movement Order", duplicates[0].cmo_id)
			frappe.throw(
				f"Container: {self.container_number} already has a Movement Order: <a href='{url}'>{duplicates[0].cmo_id}</a>"
			)
	
				