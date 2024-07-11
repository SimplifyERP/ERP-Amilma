# Copyright (c) 2023, Vivek and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate
from datetime import datetime


def execute(filters=None):
	dd2 = get_period_date_ranges_columns_report(getdate(filters.get("from_date")),getdate(filters.get("to_date")))
	res = (getdate(filters.get("to_date")).year - getdate(filters.get("from_date")).year) *12 + (getdate(filters.get("to_date")).month -  getdate(filters.get("from_date")).month)

	value = ""
	data_v = ''
	if filters.get("Customer"):
		value += f""" and  si.customer = '{filters.get('Customer')}'  """

	# 
	if filters.get("OutletType"):
		value += f""" and  ci.outlet_type = '{filters.get('OutletType')}'  """
		data_v += f""" and  ci.outlet_type = '{filters.get('OutletType')}'  """
	if filters.get("Customer_Group"):
		value += f""" and  ci.customer_group = '{filters.get('Customer_Group')}'  """
		data_v += f""" and  customer_group = '{filters.get('Customer_Group')}'  """


	data = frappe.db.sql(f"""  select customer_name,name as cu_id, outlet_type,make,freezer_type,capacity,serial_no,territory,   'InActive' as billedstatus from `tabCustomer`
	  where disabled = 0 {data_v}   """,as_dict=1)
	ddl = [l['customer_name'] for l in data]
	# frappe.msgprint(dd2[3])
	# frappe.msgprint(f"{dd2[3]}g")
	from_date = datetime.strptime(filters.get("from_date"), '%Y-%m-%d')
	to_date = datetime.strptime(filters.get("to_date"), '%Y-%m-%d')
	months_count = (to_date.year - from_date.year) * 12 + to_date.month - from_date.month + 1
	dd = frappe.db.sql(f""" 
				select 
                  ci.customer_name,
				  ci.custom_customer_joining_date,
				  ci.serial_no,
					{dd2[1]}

					CASE
					      WHEN sum(si.rounded_total) is null or sum(si.rounded_total) = 0 THEN 'InActive'
					      ELSE 'Active'
					  END AS billedstatus,
					ci.capacity,
					COALESCE(sum(si.rounded_total),0) as grand,
          DATEDIFF('{filters.get("to_date")}' , ci.creation) DIV 30 as join_moth,
	        (COALESCE(sum(si.rounded_total),0)/{months_count}) as avg
          from 
            `tabSales Invoice` si
             left join `tabCustomer` ci on ci.name =si.customer

					{dd2[2]}
                  
           where si.docstatus in (0,1) 
            and si.company = '{filters.get("company")}' 
            and si.posting_date between '{filters.get("from_date")}' and '{filters.get("to_date")}'

						{value}

                  group by si.customer_name


				""",as_dict=1)
	total = 0
	count = 0
	avg=0
	for i in dd:
		try:
			# frappe.msgprint(str(i[f'{dd2[3]}g']))
			if i[f'{dd2[3]}g'] != None :
				if i[f'{dd2[3]}g'] < 2000 :
					i['billedstatus'] = "InActive"
			if i[f'{dd2[3]}g'] == None :
				i['billedstatus'] = "InActive"
			
		except Exception as e:
			pass
			# frappe.msgprint(str(frappe.get_traceback()))

		if i['grand']:
			total += i['grand']
		count += 1
		if i['avg']:
			avg += i['avg']
		try:
			data[ddl.index(i.customer_name)].update(i)
		except Exception as e:
			print(e)
	data.append({'customer_name':"Total",'grand':total,'avg':(avg*count/100)})

	columns=[
		{
			"fieldname": "customer_name",
			"label": "<b>Customer</b>",
			"fieldtype": "Data",
			"width":  200
		},
		{
			"fieldname": "cu_id",
			"label": "<b>Customer ID</b>",
			"fieldtype": "Data",
			"width":  80
		},
		{
			"fieldname": "customer_joining_date",
			"label": "<b>Customer Joining Date</b>",
			"fieldtype": "Data",
			"width":  80
		},
		{
			"fieldname": "outlet_type",
			"label": "<b>Outlet Type</b>",
			"fieldtype": "Data",
			"width":  80
		},
		{
			"fieldname": "make",
			"label": "<b>Freezer Make</b>",
			"fieldtype": "Data",
			"width":  80
		},
		{
			"fieldname": "freezer_type",
			"label": "<b>Freezer Type</b>",
			"fieldtype": "Data",
			"width":  80
		},
		{
			"fieldname": "capacity",
			"label": "<b>Freezer Size</b>",
			"fieldtype": "Data",
			"width":  80
		},
		{
			"fieldname": "serial_no",
			"label": "<b>Serial No</b>",
			"fieldtype": "Data",
			"width":  80
		},
		{
			"fieldname": "territory",
			"label": "<b>Route</b>",
			"fieldtype": "Data",
			"width":  80
		},
		{
			"fieldname": "billedstatus",
			"label": "<b>Status</b>",
			"fieldtype": "Data",
			"width":  80
		},
		
		

	]
	for i in dd2[0]:
		columns.append(i)
	columns.append(
			{
				"fieldname": "grand",
				"label": "<b>Total </b>",
				"fieldtype": "Float",
				"default" :0.00,
				"width":  150
			}
		)
	columns.append(
                       {
                                "fieldname": "join_moth",
                                "label": "<b>Created month ago</b>",
                                "fieldtype": "Data",
                                "default" :0.00,
                                "width":  150,
								"hidden":1
                        }
                )

	columns.append(
			{
				"fieldname": "avg",
				"label": "<b>Avg</b>",
				"fieldtype": "Float",
				"default" :0.00,
				"width":  150
			}
	)

	return columns, data




@frappe.whitelist(allow_guest=True)
def get_period_date_ranges_columns_report(year_start_date,year_end_date):
	from dateutil.relativedelta import relativedelta


	res = (getdate(year_end_date).year - getdate(year_start_date).year) *12 + (getdate(year_end_date).month - getdate(year_start_date).month)
	
	increment = 1
	period_date_ranges = []
	query = ''
	row = ''
	colm = []
	last_mnth = ''

	for i in range(1, res + 2, increment):
		period_end_date = getdate(year_start_date) + relativedelta(months=increment, days=-1)
		if period_end_date > getdate(year_end_date):
			period_end_date = year_end_date

		period_date_ranges.append([year_start_date, period_end_date])

		start = getdate(year_start_date).strftime("%b%y") 
		end   = getdate(period_end_date).strftime("%b%y")
		last_mnth = start

		row += f'''
				Sum({start}.base_rounded_total) AS {start}g,
				''' 
		colm.append(
					{'fieldname': f'{start}g','label': f'{start}','fieldtype': 'Float','default' :0.00,'width':  150}
				)


		query += f""" \n
				LEFT JOIN `tabSales Invoice` {start} ON si.name = {start}.name 
				and si.posting_date between '{year_start_date}' 
				and '{period_end_date}' 
				   """

		year_start_date = period_end_date + relativedelta(days=1)
		if period_end_date == year_end_date:
			break
	return [colm,row,query,last_mnth]
