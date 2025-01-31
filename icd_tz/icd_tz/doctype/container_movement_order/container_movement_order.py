# Copyright (c) 2024, elius mgani and contributors
# For license information, please see license.txt

import frappe
from frappe.query_builder import DocType
from frappe.model.document import Document
from frappe.utils import get_url_to_form, cint

mf = DocType("Manifest")
mb = DocType("MasterBI")
cd = DocType("Containers Detail")
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
def get_manifest_details(manifest, m_bl_no=None):
	"""Get details of a manifest and container information"""
	
	query = (
        frappe.qb.from_(mf)
		.inner_join(cd)
		.on(mf.name == cd.parent)
        .inner_join(mb)
        .on(cd.m_bl_no == mb.m_bl_no)
        .select(
			mf.mrn,
			mf.vessel_name,
			mf.tpa_uid,
			mf.voyage_no,
			mf.arrival_date,
			mf.departure_date,
			mf.call_sign,
			mf.company,
            cd.container_no,
            cd.m_bl_no,
            cd.container_size,
            mb.cargo_classification.as_("cargo_type")
        )
        .where(
			(mf.name == manifest)
			& (cd.has_order == 0)
			& (cd.parent == manifest)
			& (mb.parent == manifest)
		)
    )

	if m_bl_no:
		query = query.where(
			(mb.m_bl_no == m_bl_no)
			& (cd.m_bl_no == m_bl_no)
		)
	
	details = query.run(as_dict=True)
	
	return details
