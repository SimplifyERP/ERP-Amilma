# Copyright (c) 2023, vps and contributors
# For license information, please see license.txt




import frappe
from frappe.utils import today,getdate

from datetime import datetime, timedelta
import pendulum

def execute(filters=None):
	sd=filters.get("from_date")
	ed=filters.get("to_date")

	days_before=filters.get("days_before")

	order_date=filters.get("order_date")

# order_date

	date = pendulum.parse(order_date)
	first = pendulum.parse(order_date)

	date_order = pendulum.parse(order_date)

	# get the first and last dates of the previous month
	first_day_prev_month = date_order.subtract(days=int(days_before))
	# last_day_prev_month = date_order.subtract(days=int(days_before)+)

	last_day_prev_month = date_order

	# format the dates as strings
	first_day_str = first_day_prev_month.to_date_string()
	last_day_str = last_day_prev_month.to_date_string()

#	frappe.msgprint(f"""   sd = {sd}   """)
#	frappe.msgprint(f"""   ed = {ed}   """)
	# frappe.msgprint(f"""   first_day_str = {first_day_str}   """)
	# frappe.msgprint(f"""   last_day_str = {last_day_str}   """)

	# check if date1 is the first day of the month
	# if first.day != 1:
	# 	frappe.throw(f"{first_day_str} is not the first day of the month")

	# # check if date2 is the last day of the month
	# if date.day != date.days_in_month:
	# 	frappe.throw(f"{last_day_str} is not the last day of the month")

	condition = ""
	codn_si = "" 
	if filters.get("item_group"):
		condition = condition + f""" and soi.item_group = '{filters.get("item_group")}' """
		codn_si = codn_si + f""" and sii.item_group = '{filters.get("item_group")}' """

	data  =  frappe.db.sql(f"""                              
                        select 
                              soi.item_code,
                              0 as order_qty,
                              0 as actual_qty,
                              0 as cutoff_qty
                            from 
                              `tabSales Order Item` soi 
                            left join `tabSales Order` so on so.name = soi.parent 
                            left join `tabSales Invoice Item` sii on soi.name = sii.so_detail
                            left join `tabSales Invoice` si on si.name = sii.parent and si.is_return = 0 
                            and si.posting_date between'{sd}' and '{ed}' 
                              
                            where 
                              soi.docstatus in (0, 1)  and so.company ='{filters.get("company")}'  {condition}
							 
                              group by soi.item_code  
                              
                            """,as_dict=1)
	# frappe.msgprint(str(data))
	dd =  frappe.db.sql(f"""  
				select 
					soi.qty as qty, 
					sii.qty as siiqty,
				CASE
					WHEN sii.qty IS NULL THEN   soi.qty 
					ELSE sii.qty
				END AS quantitytext,
					soi.name, 
					sii.name as siiname,
					soi.item_code
				from 
					`tabSales Order Item` soi 
				left join `tabSales Order` so on so.name = soi.parent  
				left join `tabSales Invoice Item` sii on soi.name = sii.so_detail
				left join `tabSales Invoice` si on si.name = sii.parent and si.is_return = 0
				and si.posting_date between'{sd}' and '{ed}' 
                              
				where 
					soi.docstatus in (0, 1)  and so.company ='{filters.get("company")}'  {condition}
						""",as_dict=1)

	pr = frappe.db.sql(f""" 
				select 
					sum(sii.qty) as qty, 
					sii.item_code 
				from 
					`tabSales Invoice Item` sii 
					left join `tabSales Invoice` si on si.name = sii.parent 
				where 
					si.posting_date between '{str(first_day_str)}' 
					and '{str(last_day_str)}'  
					and  si.docstatus != 2
					and si.company ='{filters.get("company")}'  {codn_si}

				group by sii.item_code 


	  """,as_dict=1)

#	frappe.msgprint(str(data))
#	frappe.msgprint(str(dd))
#	frappe.msgprint(str(pr))

	for i in pr:
		try:
			ind = [j for j,_ in enumerate(data) if _['item_code'] == i['item_code']][0]
			data[ind]["order_qty"] += i['qty']
		except Exception as e:
			print(e)



	for i in dd:
		try:
			ind = [j for j,_ in enumerate(data) if _['item_code'] == i['item_code']][0]
			data[ind]["actual_qty"] += i['quantitytext']
		except Exception as e:
			print(e)

	for i in data:
		try:
			i['cutoff_qty'] = i['actual_qty'] - i['order_qty']
		except Exception as e:
			print(e)


	columns =  [
		{
			"fieldname": "item_code",
			"label": "<b>Item Code</b>",
			"fieldtype": "Link",
			"options":"Item",
			"width":  200
		},
		{
			"fieldname": "order_qty",
			"label": "<b>Order Qty</b>",
			"fieldtype": "Float",
			"width":  200
		},
		{
			"fieldname": "actual_qty",
			"label": "<b>Available Qty</b>",
			"fieldtype": "Float",
			"width":  200
		},
		{
			"fieldname": "cutoff_qty",
			"label": "<b>cut off Qty</b>",
			"fieldtype": "Float",
			"width":  200
		}
	]
	return columns, data
