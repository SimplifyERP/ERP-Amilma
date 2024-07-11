# Copyright (c) 2022, Vivek and contributors
# For license information, please see license.txt



import frappe
from frappe.utils import getdate
from datetime import datetime

 
def execute(filters=None):
	dd = get_period_date_ranges_columns_report(getdate(filters.get("from_date")),getdate(filters.get("to_date")))



	res = (getdate(filters.get("to_date")).year - getdate(filters.get("from_date")).year) *12 + (getdate(filters.get("to_date")).month -  getdate(filters.get("from_date")).month)

	value = ""
	if filters.get("Customer"):
		value += f""" and  si.customer = '{filters.get('Customer')}'  """
	
	data = frappe.db.sql(f"""   
                                        
                    select 
                       si.customer_name,
					             si.customer,

                      sum(DISTINCT si.base_grand_total) as grand,
								{dd[1]}
					  sum( ats.target_amount) as target_amount_sum,
					( sum( si.base_grand_total) / sum( ats.target_amount) ) * 100 as achieved


                    from 
                      `tabSales Invoice` si
                      left join `tabAmilma Target Setting` ats on si.customer = ats.distributor 
					  and 
						ats.date between '{filters.get("from_date")}' and '{filters.get("to_date")}'
								
								
								
								{dd[2]}


                      where si.docstatus = 1 and ats.type = 'Primary' and
                      si.company = '{filters.get("company")}' and 
						si.posting_date between '{filters.get("from_date")}' and '{filters.get("to_date")}'
						{value}

                      
                      group by ats.distributor 
					  
                    
                     """,as_dict=1)




	CUST = [i.customer for i in data]
	CUST.append('wqqw')
	CUST.append('wqqwwww')

	for i in data:
		sum_of = frappe.db.sql(f"""  select sum(ats.target_amount) as tag  from  `tabAmilma Target Setting`
		ats  where ats.distributor = '{i.customer}' and ats.type = 'Primary' and  
		ats.target_from BETWEEN  '{filters.get("from_date")}' and '{filters.get("to_date")}'   """,as_dict=1)
		if len(sum_of) != 0:
			i.target_amount_sum = sum_of[0]['tag']
			i.achieved = (i.grand /sum_of[0]['tag'] *100 )
				

	rr = frappe.db.sql(f"""   
				
			SELECT 
			si.customer,
			si.customer_name,
			si.territory,
			DATE_FORMAT(si.posting_date, '%b%y') as cole,

			COALESCE( (SUM(sii.amount) + (SUM(sii.amount)  * 0.18) ),0) AS sii_amount,
			COALESCE((SUM(sii_b.amount) + (SUM(sii_b.amount)  * 0.18) ),0) AS sii_b_amount,
			COALESCE((SUM(sii_o.amount) + (SUM(sii_o.amount)  * 0.18) ),0) AS sii_o_amount
			
			FROM 
			`tabSales Invoice` si
			LEFT JOIN `tabSales Invoice Item` sii ON si.name = sii.parent 
			LEFT JOIN `tabSales Invoice Item` sii_b ON sii.name = sii_b.name AND sii.sub_group = 'BULK' 
			LEFT JOIN `tabSales Invoice Item` sii_o ON sii.name = sii_o.name AND sii.sub_group != 'BULK' 
			WHERE 
			si.docstatus = 1 AND
			si.company = '{filters.get("company")}' AND 
			si.customer IN {tuple(CUST)} AND
			si.posting_date BETWEEN '{filters.get("from_date")}' and '{filters.get("to_date")}' 
			GROUP BY 

			si.customer_name, 
			YEAR(si.posting_date), 
			MONTH(si.posting_date)

                     """,as_dict=1)

	# frappe.msgprint(str(rr))



	for i in rr:
		data[CUST.index(i.customer)][i.cole] = i.sii_amount
		
		data[CUST.index(i.customer)][f'{i.cole}bulk'] = round(i.sii_b_amount,2)
		data[CUST.index(i.customer)][f'{i.cole}nov'] = round(i.sii_o_amount,2)
		#           ( sum(DISTINCT si.base_grand_total) / sum(DISTINCT ats.target_amount) ) * 100   as achieved
		if i.sii_b_amount and data[CUST.index(i.customer)][f'{i.cole}ats']: 
			data[CUST.index(i.customer)][f'{i.cole}bulkach'] = round((i.sii_b_amount /  data[CUST.index(i.customer)][f'{i.cole}ats']) * 100,2)
	
		if i.sii_o_amount and data[CUST.index(i.customer)][f'{i.cole}ats']: 
			data[CUST.index(i.customer)][f'{i.cole}novach'] = round(( i.sii_o_amount  /  data[CUST.index(i.customer)][f'{i.cole}ats']) * 100,2)



	# frappe.msgprint(str(data))






	columns=[
		{
			"fieldname": "customer_name",
			"label": "<b>Customer</b>",
			"fieldtype": "Data",
			"width":  200
		},
		{
			"fieldname": "territory",
			"label": "<b>Territory</b>",
			"fieldtype": "Data",
			"width":  200
		}
	]
	for i in dd[0]:
		columns.append(i)
	columns.append(
			{
				"fieldname": "target_amount_sum",
				"label": "<b>Target Total </b>",
				"fieldtype": "Float",
				"default" :0.00,
				"width":  150
			}
		)
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
				"fieldname": "achieved",
				"label": "<b>Overall achieved </b>",
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
	
	for i in range(1, res + 2, increment):
		period_end_date = getdate(year_start_date) + relativedelta(months=increment, days=-1)
		if period_end_date > getdate(year_end_date):
			period_end_date = year_end_date

		period_date_ranges.append([year_start_date, period_end_date])

		start = getdate(year_start_date).strftime("%b%y") 
		end   = getdate(period_end_date).strftime("%b%y")

		row += f'''
				Sum(DISTINCT {start}.base_grand_total) AS {start}g,
				{start}ats.target_amount as {start}ats,
				(Sum(DISTINCT {start}.base_grand_total) /{start}ats.target_amount ) * 100 as achieved{start}a,


				''' 

		colm.append(
					{'fieldname': f'{start}ats','label': f'<b> Target </b> for  {start}','fieldtype': 'Float','default' :0.00,'width':  150}
				)
		colm.append(
					{'fieldname': f'{start}bulk','label': f'<b> Bulk </b> for {start}','fieldtype': 'data','default' :0.00,'width':  150}
				)
		colm.append(
					{'fieldname': f'{start}nov','label': f'<b> Novelty </b> for {start}','fieldtype': 'Float','default' :0.00,'width':  150}
				)
		colm.append(
					{'fieldname': f'{start}g','label': f'<b> Amount </b> for {start}','fieldtype': 'Float','default' :0.00,'width':  150}
				)
		colm.append(
					{'fieldname': f'{start}bulkach','label': f'<b> Bulk % </b> for {start}','fieldtype': 'Float','default' :0.00,'width':  150}
				)
		colm.append(
					{'fieldname': f'{start}novach','label': f'<b> Novelty % </b> for {start}','fieldtype': 'Float','default' :0.00,'width':  150}
				)
		colm.append(
					{'fieldname': f'achieved{start}a','label': f'<b> Achieved % </b> for {start}','fieldtype': 'Float','default' :0.00,'width':  150}
				)

		query += f""" \n
				LEFT JOIN `tabSales Invoice` {start} ON si.name = {start}.name 
				and si.posting_date between '{year_start_date}' 
				and '{period_end_date}' 


				left join `tabAmilma Target Setting`  {start}ats ON si.customer = {start}ats.distributor 
				and {start}ats.target_from between '{year_start_date}' 
				and '{period_end_date}' and  {start}ats.type = 'Primary'
				   """

		year_start_date = period_end_date + relativedelta(days=1)
		if period_end_date == year_end_date:
			break
	return [colm,row,query]



