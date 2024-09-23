# Copyright (c) 2024, Nathan Kagoro and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from icd_tz.icd_tz.api.utils import validate_cf_agent, validate_draft_doc


class GatePass(Document):
	def validate(self):
		validate_draft_doc("Service Order", self.service_order)
		validate_cf_agent(self)
	
	def before_submit(self):
		self.validate_storage_charges()
		self.validate_in_yard_booking()

	def validate_storage_charges(self):
		return
		"""Validate the storage payments for the Gate Pass"""
		if self.container_no:
			days_to_be_billed = frappe.db.get_value("Container", self.container_no, "days_to_be_billed")

			if days_to_be_billed > 0:
				frappe.throw(
					f"There are <b>{days_to_be_billed}</b> days to be billed for this container.<br>\
					Please clear storage payment dues before issuing the Gate Pass."
				)
	
	def validate_in_yard_booking(self):
		"""Validate the In Yard Container Booking for the Gate Pass"""

		if self.booking_id:
			booking_doc = frappe.get_doc("In Yard Container Booking", self.booking_id)
			if booking_doc.has_stripping_charges == "Yes" and not booking_doc.sales_invoice:
				frappe.throw(
					"Payment for Stripping charge were not done. Please clear the payment before issuing the Gate Pass."
				)
