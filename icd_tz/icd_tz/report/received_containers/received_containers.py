# Copyright (c) 2025, elius mgani and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    """
    Main execution function for the Received Containers report
    Args:
        filters (dict): Filter parameters
    Returns:
        tuple: (columns, data)
    """
    columns = get_columns()
    data = get_data(filters)
    
    return columns, data

def get_columns():
    """Define columns for the report"""
    return [
        {
            "fieldname": "bl_no",
            "label": _("M B/L No."),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "discharge_date",
            "label": _("Discharge Date"),
            "fieldtype": "Date",
            "width": 100
        },
        {
            "fieldname": "port_operator",
            "label": _("Port Operator"),
            "fieldtype": "Data",
            "width": 120
        },
    
        {
            "fieldname": "cargo_type",
            "label": _("Cargo Type"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "container_no",
            "label": _("Container No."),
            "fieldtype": "Data",
            "width": 120
        },
        
        {
            "fieldname": "size",
            "label": _("Size"),
            "fieldtype": "Data",
            "width": 80
        },
        {
            "fieldname": "consignee_name",
            "label": _("Consignee Name"),
            "fieldtype": "Data",
            "width": 200
        },
        {
            "fieldname": "description_of_goods",
            "label": _("Description of Goods"),
            "fieldtype": "Data",
            "width": 200
        },
        {
            "fieldname": "shipping_line",
            "label": _("Shipping Line"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "vessel",
            "label": _("Vessel"),
            "fieldtype": "Data",
            "width": 120
        }
    ]

def get_data(filters):
    """
    Fetch and return report data
    Args:
        filters (dict): Filter parameters
    Returns:
        list: List of dictionaries containing report data
    """
    conditions = get_conditions(filters)

    query = f"""
        SELECT 
            cr.ship_dc_date AS discharge_date,
            cr.port AS port_operator,
            c.container_no,
            c.m_bl_no AS bl_no,
            c.size,
            c.consignee AS consignee_name,
            c.cargo_description AS description_of_goods,
            c.sline AS shipping_line,
            cr.cargo_classification AS cargo_type,
            cr.ship AS vessel
        FROM 
            `tabContainer` c
        LEFT JOIN `tabContainer Reception` cr ON c.container_reception = cr.name            
        WHERE 
            1=1 {conditions}
        ORDER BY 
            cr.ship_dc_date DESC
    """
    
    data = frappe.db.sql(query, filters, as_dict=1)
    return data

def get_conditions(filters):
    conditions = []
    if filters.get("from_date"):
        conditions.append("cr.ship_dc_date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append("cr.ship_dc_date <= %(to_date)s")
    if filters.get("bl_no"):
        conditions.append("c.m_bl_no = %(bl_no)s")
    return " AND " + " AND ".join(conditions) if conditions else ""