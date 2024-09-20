import frappe

def validate_cf_agent(doc):
    """
    Validate the Clearing and Forwarding Agent
    """
    if doc.c_and_f_company and doc.c_and_f_agent:
        cf_company = frappe.get_cached_value("Clearing Agent", doc.c_and_f_agent, "c_and_f_company")
        if doc.c_and_f_company != cf_company:
            frappe.throw(f"The selected Clearing Agent: <b>{doc.c_and_f_agent}</b> does not belong to the selected Clearing and Forwarding Company: <b>{self.c_and_f_company}</b>")

def validate_draft_doc(doctype, docname):
    """
    Validate linking of draft documents
    """
    if frappe.db.get_value(doctype, docname, "docstatus") == 0:
        frappe.throw(f"Cannot link a draft document: <b>{doctype}- {docname}</b><br>Kindly submit the document first.")