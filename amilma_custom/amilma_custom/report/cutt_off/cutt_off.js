// Copyright (c) 2023, Vivek and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Cutt Off"] = {
	"filters": [

		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default":frappe.datetime.month_start(),
			"reqd": 1,
			"width": "60px"
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.month_end(),
			"reqd": 1,
			"width": "60px"
		},
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"reqd": 1,
			"default": frappe.defaults.get_user_default("Company"),
		},
		{
			"fieldname": "item_group",
			"label": __("Item Group"),
			"fieldtype": "Link",
			"options": "Item Group",
		},
                {
                        "fieldname":"order_date",
                        "label": __("order_date"),
                        "fieldtype": "Date",
                        "default": frappe.datetime.month_end(),
                        "reqd": 1,
                        "width": "60px"
                },
                {
                        "fieldname":"days_before",
                        "label": __("Day Before"),
                        "fieldtype": "Select",
			"options": "15\n30",
                        "reqd": 1,
                        "width": "60px"
                },


	]
};
