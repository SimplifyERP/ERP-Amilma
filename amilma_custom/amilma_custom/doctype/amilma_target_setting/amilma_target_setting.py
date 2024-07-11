# Copyright (c) 2023, Vivek and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime

from frappe.utils import now,getdate,today,format_date,nowdate,add_months


class AmilmaTargetSetting(Document):
    pass



@frappe.whitelist()
def get_month(from_date):
    start_date = datetime.strptime(from_date, '%Y-%m-%d')
    return start_date.month