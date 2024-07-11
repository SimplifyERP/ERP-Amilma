# Copyright (c) 2023, Vivek and contributors
# For license information, please see license.txt

# Copyright (c) 2023, vps and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import today,getdate


def execute(filters=None):
	sd=filters.get("from_date")
	ed=filters.get("to_date")
	die = []
	condition = ""
	if filters.get("supplier"):
		condition = condition + f""" and po.supplier = '{filters.get("supplier")}' """
	if filters.get("Warehouse"):
		condition = condition + f""" and po.set_warehouse = '{filters.get("Warehouse")}' """
	for i in filters.get('Status'):
		if i == "Draft":
			die.append(0)
		if i == "Submitted":
			die.append(1)

	if len(tuple(die)) == 1:
		condition = condition + f" and po.docstatus = '{die[0]}' "
	if len(die) > 1 :
		condition  = condition + f" and po.docstatus in {tuple(die)}"

	# if len(die) > 0:
	# 	condition = condition + f""" and po.docstatus in '{filters.get("Warehouse")}' """



	# frappe.msgprint(f""" {str(filters.get('Status'))} """)


	data =   frappe.db.sql(f"""
            
                    select 
                      poi.item_code,
                      poi.item_name,
					  po.set_warehouse,
                      sum(poi.qty) as order_qty
                    
                    from 
                      `tabPurchase Order Item` poi
                     left join `tabPurchase Order` po on po.name =  poi.parent 
                     
                     where 
                        po.transaction_date between "{sd}" and "{ed}"
						and po.company ='{filters.get("company")}'

						 {condition} and po.docstatus != 2
                        
                     group by poi.item_code
                                
                                
                     """,as_dict=1)

	for i in data:
		if i['set_warehouse']:
			stockb = getStockBalance(i['item_code'],i['set_warehouse'],filters.get("company"))
			arbb = todayPO(i['item_code'],filters.get("company"))

			i['ava_bal'] = stockb
			i['cut_off'] = stockb - i['order_qty']

			# frappe.msgprint(str(arbb))
			# if arbb.qty != None:
			# 	i['cut_off'] = stockb - arbb['qty']
			# else:
			# 	i['cut_off'] = stockb - 0.0

		else:
			i['ava_bal'] = 0.0
			i['cut_off'] = 0.0


	columns = [
		{
			"fieldname": "item_code",
			"label": "<b>Item Code</b>",
			"fieldtype": "Link",
			"options":"Item",
			"width":  200
		},
		{
			"fieldname": "item_name",
			"label": "<b>Item Name</b>",
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
			"fieldname": "ava_bal",
			"label": "<b>Available Qty</b>",
			"fieldtype": "Float",
			"width":  200
		},
		{
			"fieldname": "cut_off",
			"label": "<b>cut off Qty</b>",
			"fieldtype": "Float",
			"width":  200
		}

	]
	return columns, data




@frappe.whitelist()
def customstockbalance(item_code,warehouse,company):
    dd = frappe.db.sql(f"""

                    SELECT    a.item_code   AS "Item",
                              a.item_name   AS "Item Name",
                              a.item_group  AS "Item Group",
                              a.brand       AS "Brand",
                              a.description AS "Description",
                              b.warehouse   AS "Warehouse",
                              b.actual_qty  AS "balance_qty",
                              c.company     AS "company"
                              
                    FROM      `tabItem` a
                    
                    LEFT JOIN `tabBin` b
                    ON        a.item_code = b.item_code
                    
                    LEFT JOIN `tabItem Default` c
                    ON        a.item_code = c.parent
                    
                    WHERE     a.item_code = '{item_code}'
                    AND       b.warehouse = "{warehouse}"
                    AND       c.company = '{company}'


                    """,as_dict=1)
    if len(dd) !=0  :
        return dd[0]


@frappe.whitelist()
def customstockbalanceWarehouse(item_code,warehouse,company):
    dd = frappe.db.sql(f"""
                    SELECT    a.item_code   AS "Item",
                              a.item_name   AS "Item Name",
                              a.item_group  AS "Item Group",
                              a.brand       AS "Brand",
                              a.description AS "Description",
                              b.warehouse   AS "Warehouse",
                              b.actual_qty  AS "balance_qty",
                              c.company     AS "company"
                              
                    FROM      `tabItem` a
                    
                    LEFT JOIN `tabBin` b
                    ON        a.item_code = b.item_code
                    
                    LEFT JOIN `tabItem Default` c
                    ON        a.item_code = c.parent
                    
                    WHERE     a.item_code = '{item_code}'
                    AND       b.warehouse = "{warehouse}"
                    AND       c.company = '{company}'

                    """,as_dict=1)
    if len(dd) !=0  :
        return dd[0]



@frappe.whitelist()
def getStockBalance(item_code, warehouse,company):
	balance_qty = frappe.db.sql("""select qty_after_transaction from `tabStock Ledger Entry`
		where item_code=%s and warehouse=%s and company=%s and is_cancelled='No'
		order by posting_date desc, posting_time desc, name desc
		limit 1""",(item_code,warehouse,company))
	return balance_qty[0][0] if balance_qty else 0.0



@frappe.whitelist()
def company_balance(item_code,company):
    dd = frappe.db.sql(f""" 
                    select 
                        default_warehouse 
                    from 
                        `tabItem Default` 
                    where 
                      parent = '{item_code}' 
                      and company = '{company}'
            """,as_dict=1)

    if len(dd) >= 1:
        return getStockBalance(item_code, dd[0]['default_warehouse'],company)
    else:
         return 0.0




@frappe.whitelist()
def todayPO(item_code,company):
    dd = frappe.db.sql(f"""  select 
                            poi.item_code,
                            sum(poi.qty) as qty ,
                            po.name
                          from `tabPurchase Order Item` as poi
                          left join `tabPurchase Order` as po
                          on poi.parent = po.name
                          where po.docstatus =1 and po.submitted_on = '{today()}' and poi.item_code = '{item_code}' and po.company = '{company}';
                          """,as_dict=1)
    return dd[0]


    