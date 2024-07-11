
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
					   si.company,
                      sum(si.base_grand_total) as grand,
								{dd[1]}
					  sum(DISTINCT ats.target_amount) as target_amount_sum,
					( sum(si.base_grand_total) / sum(DISTINCT ats.target_amount) ) * 100 as achieved


                    from 
                      `tabSales Invoice` si
                      left join `tabAmilma Target Setting` ats on si.company = ats.company_name 
					  and
						ats.target_from between '{filters.get("from_date")}' and '{filters.get("to_date")}'
								
								
								
								{dd[2]}


                      where si.docstatus = 1 and ats.type = 'Secondary' and
                      si.company = '{filters.get("company")}' and 
						si.posting_date between '{filters.get("from_date")}' and '{filters.get("to_date")}'
						{value}

                      
                    
                     """,as_dict=1)
                    #   group by si.customer 



	columns=[
		{
			"fieldname": "company",
			"label": "<b>Company</b>",
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
				Sum({start}.base_grand_total) AS {start}g,
				{start}ats.target_amount as {start}ats,
				(Sum({start}.base_grand_total) /{start}ats.target_amount ) * 100 as achieved{start}a,


				''' 

		colm.append(
					{'fieldname': f'{start}ats','label': f'<b> Target </b> for  {start}','fieldtype': 'Float','default' :0.00,'width':  150}
				)
		colm.append(
					{'fieldname': f'{start}g','label': f'<b> Amount </b> for {start}','fieldtype': 'Float','default' :0.00,'width':  150}
				)
		colm.append(
					{'fieldname': f'achieved{start}a','label': f'<b> Achieved % </b> for {start}','fieldtype': 'Float','default' :0.00,'width':  150}
				)


		query += f""" \n
				LEFT JOIN `tabSales Invoice` {start} ON si.name = {start}.name 
				and si.posting_date between '{year_start_date}' 
				and '{period_end_date}' 



				left join `tabAmilma Target Setting`  {start}ats ON si.company = {start}ats.company_name 
				and {start}ats.target_from between '{year_start_date}' 
				and '{period_end_date}' and  {start}ats.type = 'Secondary'



				   """


			# left join `tabAmilma Target Setting`  {start}ats ON si.customer = {start}ats.distributor 
			# 	and {start}ats .target_from between '{year_start_date}' 
			# 	and '{period_end_date}' 


		year_start_date = period_end_date + relativedelta(days=1)
		if period_end_date == year_end_date:
			break
	return [colm,row,query]

