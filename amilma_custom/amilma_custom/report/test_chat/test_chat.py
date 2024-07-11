# Copyright (c) 2023, Vivek and contributors
# For license information, please see license.txt

import frappe



from frappe import _

def execute(filters=None):
    # get the warehouse and date range from the filters
    warehouse = filters.get('warehouse')
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')

    # get the sales orders and sales invoices for the date range and warehouse
    sales_orders = frappe.db.sql(f"""
        SELECT item_code, SUM(qty) as ordered_qty
        FROM `tabSales Order Item`
        WHERE warehouse='{warehouse}' AND
            docstatus=1 AND
            transaction_date BETWEEN '{from_date}' AND '{to_date}'
        GROUP BY item_code
    """, as_dict=True)

    sales_invoices = frappe.db.sql(f"""
        SELECT item_code, SUM(qty) as invoiced_qty
        FROM `tabSales Invoice Item`
        WHERE warehouse='{warehouse}' AND
            docstatus=1
        GROUP BY item_code
    """, as_dict=True)

    # get the stock balance for the warehouse and each item
    stock_balances = frappe.db.sql(f"""
        SELECT item_code, actual_qty as stock_balance
        FROM `tabStock Ledger Entry`
        WHERE warehouse='{warehouse}' AND
            posting_date < '{to_date}'
        GROUP BY item_code
    """, as_dict=True)

    # create a dictionary to store the results
    cutoff_quantities = {}

    # calculate the cutoff quantity for each item
    for item in sales_orders:
        item_code = item.item_code
        ordered_qty = item.ordered_qty
        invoiced_qty = 0
        stock_balance = 0

        # find the corresponding sales invoice quantity and stock balance for the item
        for invoice in sales_invoices:
            if invoice.item_code == item_code:
                invoiced_qty = invoice.invoiced_qty
                break

        for stock_balance_item in stock_balances:
            if stock_balance_item.item_code == item_code:
                stock_balance = stock_balance_item.stock_balance
                break

        # calculate the cutoff quantity as the available quantity minus the ordered and invoiced quantities
        available_qty = stock_balance - invoiced_qty
        cutoff_qty = available_qty - ordered_qty

        cutoff_quantities[item_code] = cutoff_qty

    # create the report data
    data = []
    for item_code, cutoff_qty in cutoff_quantities.items():
        data.append({
            'item_code': item_code,
            'cutoff_qty': cutoff_qty
        })

    # return the report columns and data
    columns = [
        {'label': _('Item Code'), 'fieldname': 'item_code', 'fieldtype': 'Link', 'options': 'Item'},
        {'label': _('Cutoff Quantity'), 'fieldname': 'cutoff_qty', 'fieldtype': 'Float'}
    ]

    return columns, data
