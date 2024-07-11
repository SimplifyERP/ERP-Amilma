# Copyright (c) 2024, Vivek and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint
import re
from frappe.utils import get_first_day, today, get_last_day, format_datetime, add_years, date_diff, add_days, getdate, cint, format_date,get_url_to_form
from frappe.contacts.doctype.address.address import get_address_display


#execute the columns and data in main
def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

# giving the columns below for report
def get_columns(filters):
	columns = [
		_("Outlet Name") + ":Data:200",
		_("Bill Date") + ":Data:120",
		_("Bill No") + ":Data:300",
		_("Bill Amount") + ":Data:100",
		_("SGST") + ":Currency:100",
		_("CGST") + ":Currency:100",
		_("IGST") + ":Currency:100",
		_("Customer GST No") + ":Data:150",
		_("Discount Amount") + ":Currency:150",
		_("Total Amount") +":Currency:150",
	]
	return columns
def get_data(filters):
    data = []
    if filters.company:
        get_sales_invoice = frappe.db.get_all("Sales Invoice", {'docstatus': ('!=', 0),'posting_date': ('between', (filters.from_date, filters.to_date)),'company': filters.company},['customer_name', 'tax_id', 'posting_date', 'name', 'base_net_total', 'rounded_total', 'status', 'base_discount_amount','additional_discount_percentage'],order_by='name')
    else:
        get_sales_invoice = frappe.db.get_all("Sales Invoice",{'docstatus': ('!=', 0),'posting_date': ('between', (filters.from_date, filters.to_date))},['customer_name', 'tax_id', 'posting_date', 'name', 'base_net_total','rounded_total', 'status','base_discount_amount' 'additional_discount_percentage'],order_by='name')
    for sales in get_sales_invoice:
        sgst_tax_amount = get_sgst_tax_amount(sales.name)
        cgst_tax_amount = get_cgst_tax_amount(sales.name)
        igst_tax_amount = get_igst_tax_amount(sales.name)
        if sales.status == "Cancelled":
            row = [sales.customer_name, format_date(sales.posting_date), sales.name, float(0.0), float(0.0),float(0.0), float(0.0), float(0.0), sales.tax_id]
        elif sales.additional_discount_percentage > 0:  # Check if additional_discount_percentage > 0
            row = [sales.customer_name, format_date(sales.posting_date), sales.name, sales.base_net_total,sgst_tax_amount, cgst_tax_amount, igst_tax_amount, sales.tax_id, sales.base_discount_amount,sales.rounded_total]
            data.append(row)
    return data



# get the sales taxes table in thata if sgst is here get the tax_amount 
def get_sgst_tax_amount(name):
	get_tax_amount = 0
	tax_account = frappe.db.get_all("Sales Taxes and Charges",{'parent':name},['account_head'])
	for tax in tax_account:
		pattern = re.compile(r'\bSGST\b')
		matches = pattern.findall(tax.account_head)
		if matches == ["SGST"]:
			get_tax_amount = frappe.db.get_value("Sales Taxes and Charges",{'parent':name,'account_head':tax.account_head},['tax_amount']) or 0
			return get_tax_amount

# get the sales taxes table in thata if cgst is here get the tax_amount 
def get_cgst_tax_amount(name):
	get_tax_amount = 0
	tax_account = frappe.db.get_all("Sales Taxes and Charges",{'parent':name},['account_head'])
	for tax in tax_account:
		pattern = re.compile(r'\bCGST\b')
		matches = pattern.findall(tax.account_head)
		if matches == ["CGST"]:
			get_tax_amount = frappe.db.get_value("Sales Taxes and Charges",{'parent':name,'account_head':tax.account_head},['tax_amount']) or 0
			return get_tax_amount		

# get the sales taxes table in thata if igst is here get the tax_amount 
def get_igst_tax_amount(name):
	get_tax_amount = 0
	tax_account = frappe.db.get_all("Sales Taxes and Charges",{'parent':name},['account_head'])
	for tax in tax_account:
		pattern = re.compile(r'\bIGST\b')
		matches = pattern.findall(tax.account_head)
		if matches == ["IGST"]:
			get_tax_amount = frappe.db.get_value("Sales Taxes and Charges",{'parent':name,'account_head':tax.account_head},['tax_amount']) or 0
			return get_tax_amount
		