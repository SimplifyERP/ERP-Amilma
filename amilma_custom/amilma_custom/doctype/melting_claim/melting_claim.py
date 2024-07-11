# Copyright (c) 2023, Vivek and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class MeltingClaim(Document):
	def validate(self):
		over_all_total_qty = 0.0
		over_all_total_amount = 0
		for claim in self.melting_claim_items:
			get_uom_and_pieces = frappe.db.get_value('Item',{'name':claim.item},['stock_uom','no_of_pieces'])
			if get_uom_and_pieces[0] == "Box":
				get_item_price = frappe.db.get_value('Item Price',{'item_code':claim.item,'price_list':"Distributor Price",'selling':1},['price_list_rate'])
				if get_item_price:
					if get_uom_and_pieces[1]:
						get_rate = get_item_price / float(get_uom_and_pieces[1])
						claim.rate = get_rate or 0
						claim.amount = float(claim.rate) * float(claim.req_qty) or 0

						over_all_total_amount += claim.amount
						self.net_total = over_all_total_amount

						over_all_total_qty += float(claim.req_qty)
						self.total_qty = over_all_total_qty
					else:
						frappe.throw(_('In Item No.of.Pieces Not Entered it is empty so not calculated the rate'))	
				else:
					frappe.throw(_('Item Price List Not Created'))		
			else:
				frappe.throw(_('Item UOM has no Box Please Check the Item UOM'))

@frappe.whitelist()
def get_item_rate(item):
	get_uom_and_pieces = frappe.db.get_value('Item',{'name':item},['stock_uom','no_of_pieces'])
	if get_uom_and_pieces[0] == "Box":
		get_item_price = frappe.db.get_value('Item Price',{'item_code':item,'price_list':"Distributor Price",'selling':1},['price_list_rate'])
		if get_item_price:
			if get_uom_and_pieces[1]:
				get_rate = get_item_price / float(get_uom_and_pieces[1])
			else:
				frappe.throw(_('In Item No.of.Pieces Not Entered it is empty so not calculated the rate'))	
		else:
			frappe.throw(_('Item Price, Price List only in Distributor Price'))	
		return get_rate
	else:
		frappe.throw(_('Item UOM Not set Box Type Please Set Box Type UOM'))	
		