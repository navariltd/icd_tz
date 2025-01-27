# Copyright (c) 2025, elius mgani and contributors
# For license information, please see license.txt

# import frappe

import frappe
from frappe import _


def execute(filters=None):
    """
    Main execution function for the Exited Containers report
    Args:
        filters (dict): Filter parameters
    Returns:
        tuple: (columns, data)
    """
    return get_columns(), get_data(filters)

def get_columns():
    """
    Define and return columns for the report
    Returns:
        list: List of column dictionaries
    """
    return [
        {
            "fieldname": "bl_no",
            "label": _("B/L No"),
            "fieldtype": "Data", 
            "width": 120
        },
        {
            "fieldname": "container_no",
            "label": _("Container No"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "type_of_container",
            "label": _("Cargo Type"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "arrival_date",
            "label": _("Discharge Date"),
            "fieldtype": "Date",
            "width": 100
        },
        {
            "fieldname": "departure_date",
            "label": _("Carryout Date"),
            "fieldtype": "Date",
            "width": 100
        },
        {
            "fieldname": "port_of_destination",
            "label": _("Port Operator"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "consignee_name",
            "label": _("Consignee Name"),
            "fieldtype": "Data",
            "width": 200
        },
        {
            "fieldname": "goods_description",
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
            "fieldname": "vessel_name",
            "label": _("Vessel"),
            "fieldtype": "Data",
            "width": 120
        }
    ]

def get_conditions(filters):
    """
    Generate SQL conditions based on filters
    Args:
        filters (dict): Filter parameters
    Returns:
        str: SQL WHERE conditions
    """
    if not filters:
        return ""
        
    conditions = []
    
    if filters.get("from_date"):
        conditions.append("c.arrival_date >= %(from_date)s")
        
    if filters.get("to_date"):
        conditions.append("c.departure_date <= %(to_date)s")
        
    if filters.get("container_no"):
        conditions.append("c.container_no = %(container_no)s")
        
    if filters.get("shipping_line"):
        conditions.append("c.sline = %(shipping_line)s")
        
    if filters.get("vessel_name"):
        conditions.append("gp.vessel_name = %(vessel_name)s")
        
    if filters.get("bl_no"):
        conditions.append("c.m_bl_no = %(bl_no)s")
        
    return " AND " + " AND ".join(conditions) if conditions else ""

def get_data(filters):
    """
    Fetch and return report data for Exited Containers
    Args:
        filters (dict): Filter parameters
    Returns:
        list: List of dictionaries containing report data
    """
    try:
        conditions = get_conditions(filters)
        
        query = """
            SELECT DISTINCT
                c.m_bl_no as bl_no,
                c.container_no,
                # c.type_of_container,
                c.arrival_date,
                c.departure_date,
                c.port_of_destination,
                IFNULL(c.consignee, gp.consignee) as consignee_name,
                IFNULL(gp.goods_description, c.cargo_description) as goods_description,
                IFNULL(c.sline, gp.sline) as shipping_line,
                gp.vessel_name
            FROM 
                `tabContainer` c
            INNER JOIN 
                `tabGate Pass` gp ON c.name = gp.container_id
            WHERE 
                gp.docstatus = 1 
                {conditions}
            ORDER BY 
                c.modified DESC
        """.format(conditions=conditions)
        
        return frappe.db.sql(query, filters, as_dict=1)
        
    except Exception as e:
        frappe.log_error(
            message=f"Error in Exited Containers Report: {str(e)}\nQuery: {query}",
            title="Exited Containers Report Error"
        )
        return []

def validate_data_exists():
    """
    Validate that data exists in required tables
    Returns:
        bool: True if data exists, False otherwise
    """
    gate_pass_count = frappe.db.count('Gate Pass', {'docstatus': 1})
    container_count = frappe.db.count('Container')
    
    if not gate_pass_count:
        frappe.msgprint(_("No submitted Gate Pass records found"))
        return False
        
    if not container_count:
        frappe.msgprint(_("No Container records found"))
        return False
        
    return True