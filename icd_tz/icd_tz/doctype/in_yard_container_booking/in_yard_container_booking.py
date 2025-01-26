# Copyright (c) 2024, elius mgani and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, nowdate


class InYardContainerBooking(Document):
	def before_insert(self):
		self.posting_datetime = now_datetime()
	
	def before_save(self):
		if not self.company:
			self.company = frappe.defaults.get_user_default("Company")
		
	def validate(self):
		validate_cf_agent(self.c_and_f_company, self.clearing_agent)
	
	def before_submit(self):
		self.posting_datetime = now_datetime()
	
	def on_submit(self):
		frappe.db.set_value("Container", self.container_id, {
			# "status": "Booked"
			"booking_date": nowdate()
		})


def validate_cf_agent(c_and_f_company, clearing_agent):
	if c_and_f_company and clearing_agent:
		cf_company = frappe.get_cached_value("Clearing Agent", clearing_agent, "c_and_f_company")
	
		if c_and_f_company != cf_company:
			frappe.throw(f"The selected Clearing Agent: <b>{clearing_agent}</b> does not belong to the selected Clearing and Forwarding Company: <b>{c_and_f_company}</b>")


@frappe.whitelist()
def create_bulk_bookings(data):
	data = frappe.parse_json(data)
	validate_cf_agent(data.get("c_and_f_company"), data.get("clearing_agent"))
	containers = frappe.db.get_all(
		"Container", 
		filters={
			"status": "In Yard",
			"customs_status": "Pending",
			"m_bl_no": data.get("m_bl_no")
		},
		pluck="name"
	)
	if len(containers) == 0:
		frappe.msgprint(f"No Containers found for M BL No: <b>{data.get('m_bl_no')}</b>")
		return

	count = 0
	for container_id in containers:
		doc = frappe.new_doc("In Yard Container Booking")
		doc.c_and_f_company = data.get("c_and_f_company")
		doc.clearing_agent = data.get("clearing_agent")
		doc.container_id = container_id
		doc.m_bl_no = data.get("m_bl_no")
		doc.inspection_datetime = data.get("inspection_datetime")
		doc.inspection_location = data.get("inspection_location")

		doc.flags.ignore_permissions = True
		doc.insert()
		doc.reload()

		if doc.get("name"):
			count += 1

	return count