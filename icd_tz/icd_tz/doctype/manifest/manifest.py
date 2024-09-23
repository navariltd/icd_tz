# Copyright (c) 2024, Nelson Mpanju and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime
from openpyxl import load_workbook
from frappe.model.document import Document
from frappe.core.doctype.file.utils import delete_file

class Manifest(Document):
    def before_save(self):
        if not self.manifest and self.is_new():
            frappe.throw("Please attach the manifest file before saving.")
        
        if not self.is_new() and not self.manifest:
            frappe.throw(
                "You cannot remove the manifest file once it has been attached.<br>\
                Please delete the record and create a new one."
            )
        
        if not self.company:
            self.company = frappe.defaults.get_user_default("Company")
    
    def before_submit(self):
        if not self.port:
            frappe.throw("Please fill the <b>Port</b> before submitting.")
        
        if not self.discharged_at:
            frappe.throw("Please Select the <b>Discharged At</b> before submitting.")

    def on_submit(self):
        self.create_consignees()

    def on_trash(self):
        if self.manifest:
            delete_file(self.manifest)
    
    @frappe.whitelist()
    def extract_data_from_manifest_file(self):
        if self.manifest:
            file_url = self.manifest
            file_path = frappe.get_site_path('private', 'files', file_url.split('/files/')[-1])
            
            # Load the Excel file
            workbook = load_workbook(file_path, data_only=True)

            # Function to convert dates
            def convert_date(excel_date):
                if isinstance(excel_date, datetime):
                    return excel_date.strftime('%Y-%m-%d')
                if isinstance(excel_date, str):
                    try:
                        return datetime.strptime(excel_date, '%d/%m/%Y').strftime('%Y-%m-%d')
                    except ValueError:
                        return None
                return None

            # Process the VesselInformation sheet
            vessel_info_sheet = workbook['VesselInformation']
            vessel_info_row = next(vessel_info_sheet.iter_rows(min_row=2, values_only=True))
            self.mrn = vessel_info_row[0]
            self.vessel_name = vessel_info_row[1]
            self.tpa_uid = vessel_info_row[2]
            self.voyage_no = vessel_info_row[3]
            self.arrival_date = convert_date(vessel_info_row[4])
            # no need for departure date
            # self.departure_date = convert_date(vessel_info_row[5])
            self.call_sign = vessel_info_row[6]

            # Process the Containers sheet
            containers_sheet = workbook['Containers']
            self.update_container_details(containers_sheet)

            # Process the HBlContainers sheet
            hbl_containers_sheet = workbook['HBlContainers']
            self.update_hbl_containers(hbl_containers_sheet)
            
            # Process the MasterBl sheet
            master_bl_sheet = workbook['MasterBl']
            self.update_masterbi_details(master_bl_sheet)

            # Process the HouseBl sheet
            house_bl_sheet = workbook['HouseBl']
            self.update_housebi_details(house_bl_sheet)
        
        # self.save()
        return True
    
    def update_container_details(self, containers_sheet):
        for row in containers_sheet.iter_rows(min_row=2, values_only=True):
            container = self.append("containers", {})
            container.m_bl_no = row[0]
            container.type_of_container = row[1]
            container.container_no = row[2]
            container.container_size = row[3]
            container.seal_no1 = row[4]
            container.seal_no2 = row[5]
            container.seal_no3 = row[6]
            container.freight_indicator = row[7]
            container.no_of_packages = row[8]
            container.package_unit = row[9]
            container.volume = row[10]
            container.volume_unit = row[11]
            container.weight = row[12]
            container.weight_unit = row[13]
            container.plug_type_of_reefer = row[14]
            container.minimum_temperature = row[15]
            container.maximum_temperature = row[16]

    def update_hbl_containers(self, hbl_containers_sheet):
        for row in hbl_containers_sheet.iter_rows(min_row=2, values_only=True):
            hbicontainer = self.append("hbicontainers", {})
            hbicontainer.m_bl_no = row[0]
            hbicontainer.h_bl_no = row[1]
            hbicontainer.type_of_container = row[2]
            hbicontainer.container_no = row[3]
            hbicontainer.container_size = row[4]
            hbicontainer.seal_no1 = row[5]
            hbicontainer.seal_no2 = row[6]
            hbicontainer.seal_no3 = row[7]
            hbicontainer.freight_indicator = row[8]
            hbicontainer.no_of_packages = row[9]
            hbicontainer.package_unit = row[10]
            hbicontainer.volume = row[11]
            hbicontainer.volume_unit = row[12]
            hbicontainer.weight = row[13]
            hbicontainer.weight_unit = row[14]
            hbicontainer.plug_type_of_reefer = row[15]
            hbicontainer.minimum_temperature = row[16]
            hbicontainer.maximum_temperature = row[17]

    def update_masterbi_details(self, master_bl_sheet):
        for row in master_bl_sheet.iter_rows(min_row=2, values_only=True):
            masterbi = self.append("masterbi", {})
            masterbi.m_bl_no = row[0]
            masterbi.cargo_classification = row[1]
            masterbi.bl_type = row[2]
            masterbi.place_of_destination = row[3]
            masterbi.place_of_delivery = row[4]
            masterbi.oil_type = row[5]
            masterbi.port_of_loading = row[6]
            masterbi.number_of_package = row[7]
            masterbi.package_unit = row[8]  # Ensure this field is of type 'Text' in Frappe
            masterbi.gross_weight = row[9]
            masterbi.gross_weight_unit = row[10]
            masterbi.gross_volume = row[11]
            masterbi.gross_volume_unit = row[12]
            masterbi.invoice_value = row[13]
            masterbi.invoice_currency = row[14]
            masterbi.freight_charge = row[15]
            masterbi.freight_currency = row[16]
            masterbi.imdg_code = row[17]
            masterbi.packing_type = row[18]
            masterbi.shipping_agent_code = row[19]
            masterbi.shipping_agent_name = row[20]
            masterbi.forwarder_code = row[21]
            masterbi.forwarder_name = row[22]
            masterbi.forwarder_tel = row[23]
            masterbi.exporter_name = row[24]
            masterbi.exporter_tel = row[25]
            masterbi.exporter_address = row[26]
            masterbi.exporter_tin = row[27]
            masterbi.cosignee_name = row[28]
            masterbi.cosignee_tel = row[29]
            masterbi.cosignee_address = row[30]
            masterbi.cosignee_tin = row[31]
            masterbi.notify_name = row[32]
            masterbi.notify_tel = row[33]
            masterbi.notify_address = row[34]
            masterbi.notify_tin = row[35]
            masterbi.shipping_mark = row[36]
            masterbi.net_weight = row[37]
            masterbi.net_weight_unit = row[38]

    def update_housebi_details(self, house_bl_sheet):
        for row in house_bl_sheet.iter_rows(min_row=2, values_only=True):
            housebi = self.append("housebi", {})
            housebi.m_bl_no = row[0]
            housebi.h_bl_no = row[1]
            housebi.cargo_classification = row[2]
            housebi.place_of_destination = row[3]
            housebi.net_weight = row[4]
            housebi.net_weight_unit = row[5]
            housebi.number_of_containers = row[6]
            housebi.description_of_goods = row[7]
            housebi.number_of_package = row[8]
            housebi.package_unit = row[9]  # Ensure this field is of type 'Text' in Frappe
            housebi.gross_weight = row[10]
            housebi.gross_weight_unit = row[11]
            housebi.gross_volume = row[12]
            housebi.gross_volume_unit = row[13]
            housebi.invoice_value = row[14]
            housebi.invoice_currency = row[15]
            housebi.freight_charge = row[16]
            housebi.freight_currency = row[17]
            housebi.imdg_code = row[18]
            housebi.packing_type = row[19]
            housebi.shipping_agent_code = row[20]
            housebi.shipping_agent_name = row[21]
            housebi.forwarder_code = row[22]
            housebi.forwarder_name = row[23]
            housebi.forwarder_tel = row[24]
            housebi.exporter_name = row[25]
            housebi.exporter_tel = row[26]
            housebi.exporter_address = row[27]
            housebi.exporter_tin = row[28]
            housebi.cosignee_name = row[29]
            housebi.cosignee_tel = row[30]
            housebi.cosignee_address = row[31]
            housebi.cosignee_tin = row[32]
            housebi.notify_name = row[33]
            housebi.notify_tel = row[34]
            housebi.notify_address = row[35]
            housebi.notify_tin = row[36]
            housebi.shipping_mark = row[37]
            # housebi.oil_type = row[38]
    
    def create_consignees(self):
        for row in self.masterbi:
            if not row.cosignee_name:
                continue

            if not frappe.db.exists("Consignee", row.cosignee_name):
                consignee = frappe.get_doc({
                    "doctype": "Consignee",
                    "consignee_name": row.cosignee_name,
                    "consignee_tel": row.cosignee_tel,
                    "consignee_tin": row.cosignee_tin,
                    "consignee_address": row.cosignee_address,
                })
                consignee.insert()
        