
import frappe
from frappe.utils import getdate
from datetime import datetime, timedelta

def execute(filters=None):
    from_date = datetime.strptime(filters.get("from_date"), '%Y-%m-%d')
    to_date = datetime.strptime(filters.get("to_date"), '%Y-%m-%d')
   
    # Define the date range
    date_range = [from_date + timedelta(days=x) for x in range((to_date - from_date).days + 1)]
    formatted_dates = [date.strftime("%d/%b") for date in date_range]

    # Fetch distinct list of all items
    all_items = frappe.get_all("Item", fields=["item_code", "item_name"])

    # Fetching purchase data from the database
    purchase_data = frappe.db.sql(f"""
        SELECT
            item.item_code,
            DATE_FORMAT(s.posting_date, '%%d/%%b') AS posting_date,
            SUM(si.qty) AS quantity
        FROM
            `tabItem` item
        LEFT JOIN
            `tabPurchase Invoice Item` si ON si.item_code = item.item_code
        LEFT JOIN
            `tabPurchase Invoice` s ON s.name = si.parent
        WHERE
            s.docstatus = 1
            AND s.is_return = 0
            AND DATE(s.posting_date) >= '{from_date.strftime("%Y-%m-%d")}'
            AND DATE(s.posting_date) <= '{to_date.strftime("%Y-%m-%d")}'
        GROUP BY
            item.item_code, DATE_FORMAT(s.posting_date, '%%d/%%b')
    """, as_dict=True)

    # Fetching sales data from the database
    sales_data = frappe.db.sql(f"""
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
            AND DATE_FORMAT(s.posting_date, '%%d/%%b') IN ({', '.join(['%s']*len(formatted_dates))})
        GROUP BY
            si.item_code, si.item_name, posting_date
    """, tuple(formatted_dates), as_dict=True)

    # Organizing purchase data into a dictionary for easy manipulation
    purchase_dict = {}
    for row in purchase_data:
        item_code = row['item_code']
        posting_date = row['posting_date']
        if item_code not in purchase_dict:
            purchase_dict[item_code] = {date: 0 for date in formatted_dates}
        purchase_dict[item_code][posting_date] = row['quantity']

    # Organizing sales data into a dictionary for easy manipulation
    sales_dict = {}
    for row in sales_data:
        item_code = row['item_code']
        posting_date = row['posting_date']
        if item_code not in sales_dict:
            sales_dict[item_code] = {date: 0 for date in formatted_dates}
        sales_dict[item_code][posting_date] = row['quantity']

    # Fetching opening stock from the Stock Ledger Entry for the specified date range
    opening_stock_data = frappe.db.sql(f"""
        SELECT
            sle.item_code,
            SUM(sle.actual_qty) AS opening_stock
        FROM
            `tabStock Ledger Entry` sle
        WHERE
            sle.posting_date < '{from_date.strftime("%Y-%m-%d")}'
        GROUP BY
            sle.item_code
    """, as_dict=True)

    opening_stock_dict = {d['item_code']: d['opening_stock'] for d in opening_stock_data}

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
        },
        {
            "fieldname": "opening_stock",
            "label": "<b>Opening Stock</b>",
            "fieldtype": "Float",
            "width": 200
        }
    ]

    for date in formatted_dates:
        columns.append(
           {
            "fieldname": date + "_sales",
            "label": f"<b>{date} </b>",
            "fieldtype": "Float",
            "width": 100
            }
        )
    total_purchase_quantity_column = {
        "fieldname": "total_purchase_quantity",
        "label": "<b>Total Purchase Quantity</b>",
        "fieldtype": "Float",
        "default": 0,
        "width": 150,
    }
    columns.append(total_purchase_quantity_column)

    purchase_total_column = {
        "fieldname": "opening_stock_plus_purchase_total",
        "label": "<b>Opening Stock + Purchase Total</b>",
        "fieldtype": "Float",
        "default": 0,
        "width": 150,
    }
    columns.append(purchase_total_column)
    
    

    for date in formatted_dates:
        columns.append(
            {
                "fieldname": date,
                "label": f"<b>{date}</b>",
                "fieldtype": "Float",
                "width": 100
            }
        )
    

    total_sales_quantity_column = {
        "fieldname": "total_sales_quantity",
        "label": "<b>Total Sales Quantity</b>",
        "fieldtype": "Float",
        "default": 0,
        "width": 150,
    }
    columns.append(total_sales_quantity_column)

    closing_stock_column = {
        "fieldname": "closing_stock",
        "label": "<b>Closing Stock</b>",
        "fieldtype": "Float",
        "default": 0,
        "width": 150,
    }
    columns.append(closing_stock_column)

    # Organizing data into a dictionary for easy manipulation
    final_data = {}
    for item in all_items:
        item_code = item['item_code']
        item_name = item['item_name']  # Fetch item name from the database result
        opening_stock = opening_stock_dict.get(item_code, 0)
        if item_code not in final_data:
            final_data[item_code] = {'item_name': item_name, 'opening_stock': opening_stock, 'total_purchase_quantity': 0, 'total_sales_quantity': 0, 'dates': {date: 0 for date in formatted_dates}}
        
        # Initialize the quantities to zero for all dates
        for date in formatted_dates:
            final_data[item_code]['dates'][date] = 0

    # Update data with fetched purchase values
    for row in purchase_data:
        item_code = row['item_code']
        final_data[item_code]['dates'][row['posting_date']] = row['quantity']
        final_data[item_code]['total_purchase_quantity'] += row['quantity']

    # Update data with fetched sales values
    for row in sales_data:
        item_code = row['item_code']
        final_data[item_code]['dates'][row['posting_date']] += row['quantity']
        final_data[item_code]['total_sales_quantity'] += row['quantity']

    # Formatting data into the desired structure
    formatted_data = []
    for item_code, values in final_data.items():
        row = {'item_code': item_code, 'item_name': values['item_name'], 'opening_stock': values['opening_stock'], 'total_purchase_quantity': values['total_purchase_quantity'], 'total_sales_quantity': values['total_sales_quantity']}
        row['opening_stock_plus_purchase_total'] = values['opening_stock'] + values['total_purchase_quantity']
        # row['total_sales_quantity'] = values['total_sales_quantity']
        row['closing_stock'] = values['total_purchase_quantity'] - values['total_sales_quantity']
        for date, quantity in values['dates'].items():
            row[date] = quantity
            # Add item against quantity below the respective date
            if date == datetime.now().strftime("%d/%b"):
                row[date + '_item'] = f"{item_code}: {quantity}"
        formatted_data.append(row)
    
    return columns, formatted_data




