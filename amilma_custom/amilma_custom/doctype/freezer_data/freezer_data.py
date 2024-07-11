# Copyright (c) 2023, Vivek and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class FreezerData(Document):
	# the below code is validate the freezer deposit amount
	def validate(self):
		if self.freezer_deposit == 0.0:
			self.freezer_deposit_status = "No"
		elif self.freezer_deposit > 0.0:
			self.freezer_deposit_status = "Yes"



