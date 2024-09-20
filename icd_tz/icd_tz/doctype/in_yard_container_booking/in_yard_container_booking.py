# Copyright (c) 2024, Nathan Kagoro and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class InYardContainerBooking(Document):
	def before_save(self):
		if not self.company:
			self.company = frappe.defaults.get_user_default("Company")
		
	def validate(self):
		self.validate_cf_agent()

	def validate_cf_agent(self):
		"""
		Validate the Clearing and Forwarding Agent
		"""
		if self.c_and_f_company and self.c_and_f_agent:
			cf_company = frappe.get_cached_value("Clearing Agent", self.c_and_f_agent, "c_and_f_company")
			if self.c_and_f_company != cf_company:
				frappe.throw(f"The selected Clearing Agent: <b>{self.c_and_f_agent}</b> does not belong to the selected Clearing and Forwarding Company: <b>{self.c_and_f_company}</b>")
