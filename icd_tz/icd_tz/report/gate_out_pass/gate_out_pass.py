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
      "fieldname": "bl_no",
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
      "fieldname": "vessel_name",
      "label": _("Vessel Name"),
      "fieldtype": "Data",
      "width": 120
    },
    {
      "fieldname": "c_and_f_company",
      "label": _("C & F Company"),
      "fieldtype": "Data",
      "width": 150
    },
    {
      "fieldname": "voyage_no",
      "label": _("Voyage No"),
      "fieldtype": "Data",
      "width": 150
    },
    {
      "fieldname": "sline",
      "label": _("Sline"),
      "fieldtype": "Data",
      "width": 150
    },
    {
      "fieldname": "consignee",
      "label": _("Consignee"),
      "fieldtype": "Link",
      "options": "Consignee",
      "width": 150
    },
    {
      "fieldname": "freight_indicator",
      "label": _("Status"),
      "fieldtype": "Data",
      "width": 150
    },
    {
      "fieldname": "place_of_destination",
      "label": _("Destination"),
      "fieldtype": "Data",
      "width": 150
    },
    {
      "fieldname": "arrival_date",
      "label": _("Date In"),
      "fieldtype": "Date",
      "width": 150
    },
    {
      "fieldname": "departure_date",
      "label": _("Date Out"),
      "fieldtype": "Date",
      "width": 150
    }
  ]


def get_data(filters):
  sql_query = """
  SELECT 
    gp.container_id AS container_no,
    gp.bl_no,
    gp.size,
    gp.consignee,
    gp.sline,
    gp.c_and_f_company,
    gp.vessel_name,
    gp.voyage_no,
    c.freight_indicator,
    c.place_of_destination,
    c.arrival_date,
    c.departure_date
  FROM 
    `tabGate Pass` AS gp
  LEFT JOIN
    `tabContainer` AS c ON gp.container_id = c.name
  WHERE 1=1
  """

  values = {}
  if filters.get("bl_no"):
    sql_query += " AND gp.bl_no = %(bl_no)s"
    values["bl_no"] = filters["bl_no"]

  return frappe.db.sql(sql_query, values=values, as_dict=True)

def get_filters():
  return [
    {
      "fieldname": "bl_no",
      "label": _("B/L No."),
      "fieldtype": "Data",
      "default": "",
      "reqd": 0,  
      "width": 150
    }
  ]

