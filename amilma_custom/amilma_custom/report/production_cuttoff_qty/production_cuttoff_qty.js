// Copyright (c) 2023, Vivek and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Production Cuttoff Qty"] = {
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
			"fieldname": "supplier",
			"label": __("Supplier"),
			"fieldtype": "Link",
			"options": "Supplier",
		},
		{
			"fieldname": "Warehouse",
			"label": __("Warehouse"),
			"fieldtype": "Link",
			"options": "Warehouse",
			"get_query": function() {
				const company = frappe.query_report.get_filter_value('company');
				return {
					filters: [
						 ['company','=', company]
					]
				}
			}
		},
		{
			"fieldname": "Status",
			"label": __("Status"),
			"fieldtype": "MultiSelectList",
			"options": ['Draft',"Submitted"],
		},

	]
};
