// Copyright (c) 2023, Vivek and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Primary target sales"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"reqd": 1,
			"default": frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default":frappe.datetime.year_start(),
			"reqd": 1,
			"width": "60px"
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.year_end(),
			"reqd": 1,
			"width": "60px"
		},
		{
			"fieldname": "Customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer",

		},
	]
};
