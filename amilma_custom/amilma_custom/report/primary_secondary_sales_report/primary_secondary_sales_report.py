# Copyright (c) 2023, Vivek and contributors
# For license information, please see license.txt

# Copyright (c) 2022, Vivek and contributors
# For license information, please see license.txt



import frappe
from frappe.utils import getdate
from datetime import datetime
from collections import defaultdict
# import pandas as pd


def execute(filters=None):
    dd_1 = get_period_date_ranges_columns_report_total_1(getdate(filters.get("from_date")),getdate(filters.get("to_date")))
    dd_2 = get_period_date_ranges_columns_report_total_2(getdate(filters.get("from_date")),getdate(filters.get("to_date")))

    res = (getdate(filters.get("to_date")).year - getdate(filters.get("from_date")).year) *12 + (getdate(filters.get("to_date")).month -  getdate(filters.get("from_date")).month)

    value = ""
    if filters.get("Customer"):
       value = f""" and  ci.name = '{filters.get('Customer')}'  """

    list1 =frappe.db.sql( f""" 
            select 
              ci.customer_name, 
              ci.represents_company,
              {dd_1[1]}

              sum(sip.grand_total) as sip_total
              
              from  `tabSales Invoice` sip
             
              left join `tabCustomer` ci on ci.name = sip.customer
               {dd_1[2]}

            where 
              ci.is_internal_customer = 1 
              and sip.docstatus = 1 
              and sip.is_return = 0  and
                sip.posting_date between '{filters.get("from_date")}' and '{filters.get("to_date")}'

              and sip.company = 'Sree Amoha Food Gallery Pvt Ltd'  

              {value}            
              
            group by 
              ci.name


                                """,as_dict=1)
    list2 =frappe.db.sql( f""" 
                select 
                  ci.represents_company, 
                    {dd_2[1]}
                  sum(sis.grand_total) as sis_total 
                  
                from
                    `tabCustomer` ci  

                 left join `tabSales Invoice` sis on ci.represents_company = sis.company

                      {dd_2[2]}
                where
                   sis.docstatus = 1 
                  and sis.is_return = 0 
                  and sis.posting_date between '{filters.get("from_date")}' and '{filters.get("to_date")}'
                  and   ci.represents_company is not null
                  and  ci.is_internal_customer = 1 
 
                  {value}
                 
                group by 
                  ci.represents_company


                    """,as_dict=1)


    data = []
    for dict1 in list1:
        for dict2 in list2:
            if dict1['represents_company'] == dict2['represents_company']:
               merged_dict = {**dict1, **dict2}
               data.append(merged_dict)




    columns=[
		{
			"fieldname": "customer_name",
			"label": "<b>Customer</b>",
			"fieldtype": "Data",
			"width":  200
		}
	]
    for i in dd_1[0]:
        columns.append(i)
    columns.append({"fieldname": "sip_total","label": "<b>Primary total </b>","fieldtype": "Float","default" :0.00,"width":  150})
    columns.append({"fieldname": "sis_total","label": "<b>Secondary total</b>","fieldtype": "Float","default" :0.00,"width":  150})
    return columns, data



@frappe.whitelist(allow_guest=True)
def get_period_date_ranges_columns_report_total_1(year_start_date,year_end_date):
    from dateutil.relativedelta import relativedelta
    res = (getdate(year_end_date).year - getdate(year_start_date).year) *12 + (getdate(year_end_date).month - getdate(year_start_date).month)
    increment = 1
    period_date_ranges = []
    query = ''
    row = ''
    colm = []
    FILTERR = ''
    for i in range(1, res + 2, increment):
        period_end_date = getdate(year_start_date) + relativedelta(months=increment, days=-1)
        if period_end_date > getdate(year_end_date):
            period_end_date = year_end_date
        period_date_ranges.append([year_start_date, period_end_date])
        start = getdate(year_start_date).strftime("%b%y")
        end   = getdate(period_end_date).strftime("%b%y")
        row += f'''
		sum({start}.grand_total) as {start}g,
        '''

        colm.append({'fieldname': f'{start}g','label': f'{start} Primary','fieldtype': 'Float','default' :0.00,'width':  150})
        colm.append({'fieldname': f'{start}f','label': f'{start} Secondary','fieldtype': 'Float','default' :0.00,'width':  150})
 
        query += f""" \n

			left join `tabSales Invoice` {start}  on
			sip.name = {start}.name 
                              and  {start}.posting_date between '{year_start_date}' and '{period_end_date}'

				   """
        year_start_date = period_end_date + relativedelta(days=1)
        if period_end_date == year_end_date:
            break
    return [colm,row,query,FILTERR]



@frappe.whitelist(allow_guest=True)
def get_period_date_ranges_columns_report_total_2(year_start_date,year_end_date):
    from dateutil.relativedelta import relativedelta
    res = (getdate(year_end_date).year - getdate(year_start_date).year) *12 + (getdate(year_end_date).month - getdate(year_start_date).month)
    increment = 1
    period_date_ranges = []
    query = ''
    row = ''
    colm = []
    FILTERR = ''
    for i in range(1, res + 2, increment):
        period_end_date = getdate(year_start_date) + relativedelta(months=increment, days=-1)
        if period_end_date > getdate(year_end_date):
            period_end_date = year_end_date
        period_date_ranges.append([year_start_date, period_end_date])
        start = getdate(year_start_date).strftime("%b%y")
        end   = getdate(period_end_date).strftime("%b%y")
        row += f'''
        sum({start}f.grand_total) as {start}f,
        '''


        query += f""" \n

            left join `tabSales Invoice` {start}f  on {start}f.name = sis.name 
                            and  {start}f.posting_date between '{year_start_date}' and '{period_end_date}'
                   """
        year_start_date = period_end_date + relativedelta(days=1)
        if period_end_date == year_end_date:
            break
    return [colm,row,query,FILTERR]
