# Copyright (c) 2024, Nathan Kagoro and contributors
# For license information, please see license.txt

import frappe
from frappe.query_builder import DocType
from frappe.utils import get_link_to_form
from frappe.model.document import Document

cr = DocType("Container Reception")

class ContainerReception(Document):
	def validate(self):
		self.validate_duplicate_cmo()

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

