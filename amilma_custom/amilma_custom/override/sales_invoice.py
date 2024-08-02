import frappe
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice


class CustomSalesInvoice(SalesInvoice):

    def before_save(self):
        bulk_items_present = False
        valid_items_present = False
        item_group_present= False
        if self.company != "Sree Amoha Food Gallery Pvt Ltd":
            offer_1 = frappe.db.get_value("Item", {"disabled": 0, "custom_offer_item": 1}, ["name"])
            offer_2 = frappe.db.get_value("Item", {"disabled": 0, "custom_second_offer_item": 1}, ["name"])

            frappe.cache().hset("sales_invoice_offers", "offer_1", offer_1)
            frappe.cache().hset("sales_invoice_offers", "offer_2", offer_2)

            offer_1_present = False
            offer_2_present = False

            for item in self.items:
                if item.item_code == offer_1:
                    offer_1_present = True
                if item.item_code == offer_2:
                    offer_2_present = True

                item_group = frappe.db.get_value("Item", item.item_code, "item_group")
                sub_group = frappe.db.get_value("Item", item.item_code, "sub_group")
                if item_group in ["ICE CREAMS", "ENDLESS"] and sub_group != "BULK":
                    valid_items_present = True  
                if sub_group == "BULK":
                    bulk_items_present = True    

                if item_group not in ["ICE CREAMS", "ENDLESS"]:
                    item_group_present = True

            if not valid_items_present:
                return

            offer_1_item_details = frappe.get_doc("Item",offer_1)
            offer_2_item_details = frappe.get_doc("Item",offer_2)

            # Add or remove items based on the total value
            if bulk_items_present:
                self.items = [item for item in self.items if item.item_code not in [offer_1, offer_2]]
            elif item_group_present:    
                self.items = [item for item in self.items if item.item_code not in [offer_1, offer_2]]
            elif valid_items_present:    
                if self.total > 3000 and self.total < 4999:
                    if not offer_1_present:
                        self.items = [item for item in self.items if item.item_code != offer_2]
                        new_item = self.append('items', {})
                        new_item.item_code = offer_1_item_details.name
                        new_item.item_name = offer_1_item_details.item_name
                        new_item.qty = 1
                        new_item.description =offer_1_item_details.description
                        new_item.uom = offer_1_item_details.stock_uom
                        new_item.conversion_factor = 0.0
                        new_item.rate = 0.0
                        new_item.amount = 0.0
                        new_item.base_rate = 0.0
                        new_item.base_amount = 0.0
                    else:
                        self.items = [item for item in self.items if item.item_code != offer_2]

                elif self.total >= 5000 and self.total < 10000:
                    if not offer_2_present:
                        self.items = [item for item in self.items if item.item_code != offer_1]
                        new_item = self.append('items', {})
                        new_item.item_code = offer_2_item_details.name
                        new_item.item_name = offer_2_item_details.item_name
                        new_item.qty = 1
                        new_item.description = offer_2_item_details.description
                        new_item.uom = offer_2_item_details.stock_uom
                        new_item.conversion_factor = 0.0
                        new_item.rate = 0.0
                        new_item.amount = 0.0
                        new_item.base_rate = 0.0
                        new_item.base_amount = 0.0
                    else:
                        self.items = [item for item in self.items if item.item_code != offer_1]

                elif self.total > 10000:
                    if not offer_2_present:
                        self.items = [item for item in self.items if item.item_code != offer_2]
                        new_item = self.append('items', {})
                        new_item.item_code = offer_2_item_details.name
                        new_item.item_name = offer_2_item_details.item_name
                        new_item.qty = 2
                        new_item.description = offer_2_item_details.description
                        new_item.uom = offer_2_item_details.stock_uom
                        new_item.conversion_factor = 0.0
                        new_item.rate = 0.0
                        new_item.amount = 0.0
                        new_item.base_rate = 0.0
                        new_item.base_amount = 0.0
                    else:
                        self.items = [item for item in self.items if item.item_code != offer_1]        
                self.run_method("set_missing_values")
            else:
                self.items = [item for item in self.items if item.item_code != offer_1 and item.item_code != offer_2]


