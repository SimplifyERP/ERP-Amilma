import frappe


@frappe.whitelist()
def update_sales_invoice_status():
    sales_invoice_status = frappe.db.sql("""  select status from `tabSales Invoice` where name = "SA-SI-D-24-2273" """)
    print(sales_invoice_status)