// Copyright (c) 2024, Vivek and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["SKU Wise Distributor Purchase vs Sales Summary"] = {
	"filters": [
		
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


	]
};
