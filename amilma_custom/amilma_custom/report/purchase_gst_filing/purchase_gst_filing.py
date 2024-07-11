# Copyright (c) 2024, Vivek and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint
import re
from frappe.utils import get_first_day, today, get_last_day, format_datetime, add_years, date_diff, add_days, getdate, cint, format_date,get_url_to_form
from frappe.contacts.doctype.address.address import get_address_display


def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data



# giving the columns below for report
def get_columns(filters):
    columns = [
        _("Supplier Name") + ":Data:200",
        _(" Supplier GST No") + ":Data:150",
        _("Customer Name") + ":Data:200",
        _("Customer GST No") + ":Data:150",
        _("Bill Date") + ":Data:120",
        _("Bill No") + ":Data:200",
        _("Bill Amount") + ":Currency:100",
        _("SGST") + ":Currency:100",
        _("CGST") + ":Currency:100",
        _("IGST") + ":Currency:100",
        _("Total Amount") +":Currency:150",
        _('Status') +":Data:100"
    ]
    return columns

# getting the purchase invoice data
def get_data(filters):
    data = []
    if filters.company:
        get_purchase_invoice = frappe.db.get_all("Purchase Invoice",{'docstatus':('!=','0'), 'posting_date': ('between', (filters.from_date, filters.to_date)), 'company': filters.company},['supplier_name', 'tax_id', 'posting_date', 'name', 'base_net_total','inter_company_invoice_reference', 'rounded_total','company','status'],order_by='name' )
    else:
        get_purchase_invoice = frappe.db.get_all("Purchase Invoice",{'docstatus': ('!=','0'), 'posting_date': ('between', (filters.from_date, filters.to_date))},['supplier_name', 'tax_id', 'posting_date', 'name', 'base_net_total', 'rounded_total','inter_company_invoice_reference','company','status'],order_by='name'  )

    for purchase in get_purchase_invoice:
        sgst_tax_amount = get_sgst_tax_amount(purchase.name)
        cgst_tax_amount = get_cgst_tax_amount(purchase.name)
        igst_tax_amount = get_igst_tax_amount(purchase.name)
        supplier_gst_no = get_supplier_gst_no(purchase.supplier_name)
        customer_gst_no = get_customer_gst_no(purchase.company)
        if purchase.status == "Cancelled":
            row = [purchase.supplier_name, supplier_gst_no, purchase.company, customer_gst_no,format_date(purchase.posting_date), purchase.inter_company_invoice_reference,float(0.0),float(0.0),float(0.0),float(0.0),float(0.0),purchase.status]
        else:
            row = [purchase.supplier_name, supplier_gst_no, purchase.company, customer_gst_no,format_date(purchase.posting_date), purchase.inter_company_invoice_reference, purchase.base_net_total, sgst_tax_amount,cgst_tax_amount, igst_tax_amount, purchase.rounded_total,purchase.status]
        data.append(row)
    return data

# get the purchase taxes table in thata if sgst is here get the tax_amount 
def get_sgst_tax_amount(name):
    get_tax_amount = 0
    tax_account = frappe.db.get_all("Purchase Taxes and Charges",{'parent':name},['account_head'])
    for tax in tax_account:
        pattern = re.compile(r'\bSGST\b')
        matches = pattern.findall(tax.account_head)
        if matches == ["SGST"]:
            get_tax_amount = frappe.db.get_value("Purchase Taxes and Charges",{'parent':name,'account_head':tax.account_head},['tax_amount']) or 0
            return get_tax_amount

# get the purchase taxes table in thata if cgst is here get the tax_amount 
def get_cgst_tax_amount(name):
    get_tax_amount = 0
    tax_account = frappe.db.get_all("Purchase Taxes and Charges",{'parent':name},['account_head'])
    for tax in tax_account:
        pattern = re.compile(r'\bCGST\b')
        matches = pattern.findall(tax.account_head)
        if matches == ["CGST"]:
            get_tax_amount = frappe.db.get_value("Purchase Taxes and Charges",{'parent':name,'account_head':tax.account_head},['tax_amount']) or 0
            return get_tax_amount		

# get the purchase taxes table in thata if igst is here get the tax_amount 
def get_igst_tax_amount(name):
    get_tax_amount = 0
    tax_account = frappe.db.get_all("Purchase Taxes and Charges",{'parent':name},['account_head'])
    for tax in tax_account:
        pattern = re.compile(r'\bIGST\b')
        matches = pattern.findall(tax.account_head)
        if matches == ["IGST"]:
            get_tax_amount = frappe.db.get_value("Purchase Taxes and Charges",{'parent':name,'account_head':tax.account_head},['tax_amount']) or 0
            return get_tax_amount
        
def get_supplier_gst_no(supplier_name):
    return frappe.db.get_value("Supplier", supplier_name, "tax_id") or ""


def get_customer_gst_no(company):
    return frappe.db.get_value("Company", company, "tax_id") or ""



@frappe.whitelist()
def get_address(company):
    address_without_br_tags = ""
    address = frappe.db.get_value("Dynamic Link",{'link_name':company},['parent'])
    if address:
        address_without_br_tags = re.sub('<br>', '', get_address_display(address))
    else:
        address_without_br_tags = ""    
    return address_without_br_tags