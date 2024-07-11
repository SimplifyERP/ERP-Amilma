
# # Copyright (c) 2024, Vivek and contributors
# # For license information, please see license.txt

import frappe
from frappe.utils import getdate
from datetime import datetime, timedelta

def execute(filters=None):
    from_date = datetime.strptime(filters.get("from_date"), '%Y-%m-%d')
    to_date = datetime.strptime(filters.get("to_date"), '%Y-%m-%d')
    company = filters.get("company")

    date_range = [from_date + timedelta(days=x) for x in range((to_date - from_date).days + 1)]
    formatted_dates = [date.strftime("%d/%b") for date in date_range]

    # Fetching data from the database
    data = frappe.db.sql(f"""
        SELECT
            si.item_code,
            si.item_name,
            DATE_FORMAT(s.posting_date, '%%d/%%b') AS posting_date,
            SUM(si.qty) AS quantity
        FROM
            `tabSales Invoice Item` si
        LEFT JOIN
            `tabSales Invoice` s ON s.name = si.parent
        LEFT JOIN
            `tabCustomer` c ON c.name = s.customer
        WHERE
            s.docstatus = 1
            AND s.is_return = 0
            AND s.company = '{company}'
            AND DATE_FORMAT(s.posting_date, '%%d/%%b') IN ({', '.join(['%s']*len(formatted_dates))})
        GROUP BY
            si.item_code, si.item_name, posting_date
    """, tuple(formatted_dates), as_dict=True)

    # Constructing columns
    columns = [
        {
            "fieldname": "item_code",
            "label": "<b>Item Code</b>",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "fieldname": "item_name",
            "label": "<b>Item Name</b>",
            "fieldtype": "Data",
            "width": 200
        }
    ]

    for date in formatted_dates:
        columns.append(
            {
                "fieldname": date,
                "label": f"<b>{date}</b>",
                "fieldtype": "Float",
                "width": 100
            }
        )
    
    total_quantity_column = {
        "fieldname": "total_quantity",
        "label": "<b>Total Quantity</b>",
        "fieldtype": "Float",
        "default": 0,
        "width": 150,
    }
    columns.append(total_quantity_column)

    # Organizing data into a dictionary for easy manipulation
    final_data = {}
    for row in data:
        item_code = row['item_code']
        item_name = row['item_name']  # Fetch item name from the database result
        if item_code not in final_data:
            final_data[item_code] = {'item_name': item_name, 'total_quantity': 0, 'dates': {date: 0 for date in formatted_dates}}
        final_data[item_code]['dates'][row['posting_date']] = row['quantity']
        final_data[item_code]['total_quantity'] += row['quantity']

    # Formatting data into the desired structure
    formatted_data = []
    for item_code, values in final_data.items():
        row = {'item_code': item_code, 'item_name': values['item_name'], 'total_quantity': values['total_quantity']}
        for date, quantity in values['dates'].items():
            row[date] = quantity
            # Add item against quantity below the respective date
            if date == datetime.now().strftime("%d/%b"):
                row[date + '_item'] = f"{item_code}: {quantity}"
        formatted_data.append(row)
    
    return columns, formatted_data
