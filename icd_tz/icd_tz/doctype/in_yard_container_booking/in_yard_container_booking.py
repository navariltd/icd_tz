# Copyright (c) 2024, Nathan Kagoro and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class InYardContainerBooking(Document):
	def before_save(self):
		if not self.company:
			self.company = frappe.defaults.get_user_default("Company")
