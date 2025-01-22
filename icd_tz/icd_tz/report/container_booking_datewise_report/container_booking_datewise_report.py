# Copyright (c) 2025, elius mgani and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	return columns, data

def get_columns():
    return [
        {
            "fieldname": "container_no",
            "label": _("Container No."),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "m_bl_no",
            "label": _("B/L No."),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "size",
            "label": _("Size (FT)"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "seal",
            "label": _("Seal"),
            "fieldtype": "Data",
            "width": 360
        },
        {
            "fieldname": "c_and_f_company",
            "label": _("C & F Company"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "original_location",
            "label": _("Original Location"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "post",
            "label": _("Post"),
            "fieldtype": "Datetime",
            "width": 150
        },
    ]
    

def get_data(filters=None):
    sql_query = """
    SELECT 
        c.name AS container_no,
        c.m_bl_no,
        c.size,
        CONCAT_WS(', ', c.seal_no_1, c.seal_no_2, c.seal_no_3) AS seal,
        ci.c_and_f_company,
        ci.original_location,
        CONCAT(ci.posting_date, ' ', ci.posting_time) AS post
    FROM 
        `tabContainer` AS c
    LEFT JOIN 
        `tabContainer Inspection` AS ci ON c.name = ci.container_id
    """
    return frappe.db.sql(sql_query, as_dict=True)
