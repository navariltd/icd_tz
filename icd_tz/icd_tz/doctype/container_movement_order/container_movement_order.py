# Copyright (c) 2024, elius mgani and contributors
# For license information, please see license.txt

import frappe
from frappe.query_builder import DocType
from frappe.model.document import Document
from frappe.utils import get_url_to_form, cint

cmo = DocType("Container Movement Order")

class ContainerMovementOrder(Document):
	def before_insert(self):
		self.update_container_count()
	
	def before_save(self):
		if not self.company:
			self.company = frappe.defaults.get_user_default("Company")
		
	def validate(self):
		if self.container_no:
			self.validate_container_is_in_manifest()
			self.validate_duplicate_cmo_per_container_number()
	
	def before_submit(self):
		self.validate_signature()

	def on_submit(self):
		self.update_container_has_order()
	
	def validate_container_is_in_manifest(self):
		"""Validate that the container number is in the selected manifest"""

		if not frappe.db.exists(
			"Containers Detail",
			{"parent": self.manifest, "container_no": self.container_no}
		):
			frappe.throw(
				f"Container: {self.container_no} does not belong to the this Manifest: {self.manifest}"
			)
	
	def validate_duplicate_cmo_per_container_number(self):
		"""Validate the duplicate of cmo per container number"""
		duplicates = (
			frappe.qb.from_(cmo)
			.select(
				cmo.name.as_("cmo_id")
			)
			.where(
				(cmo.manifest == self.manifest) &
				(cmo.container_no == self.container_no)
				& (cmo.name != self.name)
			)
		).run(as_dict=True)
		if duplicates:
			url = get_url_to_form("Container Movement Order", duplicates[0].cmo_id)
			frappe.throw(
				f"Container: {self.container_no} already has a Movement Order: <a href='{url}'>{duplicates[0].cmo_id}</a>"
			)
	
	def update_container_has_order(self):
		"""Update the status of the container to Has Order"""
		if self.container_no:
			frappe.db.set_value(
				"Containers Detail",
				{"parent": self.manifest, "container_no": self.container_no},
				"has_order", 1
			)
	
	def validate_signature(self):
		settings_doc = frappe.get_doc("ICD TZ Settings")
		if settings_doc.enable_signature_validation == 1:
			if (
				not self.driver_signature or
				not self.gate_no_signature
			):
				frappe.throw("Please ensure all signatures are provided before submitting this document.")

	def update_container_count(self):
		"""Update the container count based on the manifest and m_bl_no"""

		if (
			self.manifest and 
			self.m_bl_no and
			not self.container_count
		):
			total_count = frappe.db.get_value(
				"MasterBI",
				{"parent": self.manifest, "m_bl_no": self.m_bl_no},
				"number_of_containers"
			)

			current_count = frappe.db.count(
				"Container Movement Order",
				{"manifest": self.manifest, "m_bl_no": self.m_bl_no}
			)

			self.container_count = f"{current_count + 1}/{total_count}"



@frappe.whitelist()
def get_manifest_details(manifest):
	"""Get details of a manifest"""
	
	details = frappe.db.get_value(
		"Manifest",
		manifest,
		["mrn", "vessel_name", "tpa_uid", "voyage_no", "arrival_date", "departure_date", "call_sign", "company"], 
		as_dict=True
	)

	containers = frappe.db.get_all(
		"Containers Detail",
		filters={"parent": manifest, "has_order": 0},
		fields=["container_no"],
		pluck="container_no"
	)

	if len(containers) > 0:
		details["containers"] = containers

	return details

@frappe.whitelist()
def get_container_size_from_manifest(manifest, container_no):
	"""Get the size of the container from the manifest"""
	
	container_info = frappe.db.get_value(
		"Containers Detail",
		{"parent": manifest, "container_no": container_no},
		["container_size", "m_bl_no"],
		as_dict=True
	)

	if container_info.m_bl_no:
		cargo_classification = frappe.db.get_value(
			"MasterBI",
			{"parent": manifest, "m_bl_no": container_info.m_bl_no},
			"cargo_classification",
		)

		if cargo_classification == "IM":
			container_info["cargo_classification"] = "Local"
		elif cargo_classification == "TR":
			container_info["cargo_classification"] = "Transit"

	return container_info