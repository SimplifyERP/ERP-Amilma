from __future__ import unicode_literals
from frappe import publish_progress
import frappe
import json


@frappe.whitelist()
def get_items_without_has_batch_in_item_group(group, series):
    if not group or not series:
        return 0
    counter = 0
    for item in frappe.db.get_list('Item', filters={'item_group': group, 'has_batch_no': 0}, fields=['item_code', 'item_name'], order_by='item_code', as_list=False):
        counter+=1
    return counter

def set_item_batch_properities(item_code, series):
    frappe.db.set_value('Item', item_code, {
        'has_batch_no': 1,
        'create_new_batch': 1,
        'batch_number_series': series
    })

def create_new_batch(item_code):
    batch_no = frappe.get_doc(dict(
	    doctype='Batch',
		item=item_code)).insert().name
    
    return batch_no

def update_stock_ledger(item_code):
    batch_no =''
    size = len(frappe.db.get_list('Stock Ledger Entry', filters={'item_code': item_code}, fields=['name', 'actual_qty', 'qty_after_transaction', 'voucher_type', 'voucher_detail_no', 'voucher_no'], order_by='name', as_list=False))
    if size > 0:
        batch_no = create_new_batch(item_code)
        for entry in frappe.db.get_list('Stock Ledger Entry', filters={'item_code': item_code}, fields=['name', 'actual_qty', 'qty_after_transaction', 'voucher_type', 'voucher_detail_no', 'voucher_no'], order_by='name', as_list=False):
            frappe.db.set_value('Stock Ledger Entry', entry.name, {
                'batch_no': batch_no
            })
            if entry.voucher_type == 'Stock Reconciliation':
                srd = frappe.get_doc('Stock Reconciliation', entry.voucher_no)
                if srd.purpose == 'Opening Stock' and entry.actual_qty == 0:
                    frappe.db.set_value('Stock Ledger Entry', entry.name, {
                        'actual_qty': entry.qty_after_transaction
                })      

         


@frappe.whitelist()
def handle_convert_non_batch_to_has_batch(group, series):
    if not group or not series:
        return 0
    counter = 0
    size = len(frappe.db.get_list('Item', filters={'item_group': group, 'has_batch_no': 0}, fields=['item_code', 'item_name'], order_by='item_code', as_list=False))
    for item in frappe.db.get_list('Item', filters={'item_group': group, 'has_batch_no': 0}, fields=['item_code', 'item_name'], order_by='item_code', as_list=False):
        if counter > -1:
            set_item_batch_properities(item.item_code, series)
            update_stock_ledger(item.item_code)
            counter+=1
            
            progress = counter / size * 100
            frappe.publish_progress(float(counter*100)/size, title = "Processing Items...")
    
    return counter
