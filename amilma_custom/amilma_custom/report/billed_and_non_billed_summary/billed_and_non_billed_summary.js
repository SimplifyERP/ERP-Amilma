// Copyright (c) 2023, Vivek and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Billed and non-billed summary"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": "Sree Amoha Food Gallery Pvt Ltd",
			"reqd": 1
			// "default": frappe.defaults.get_user_default("Company")
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
                {
                        "fieldname": "Customer_Group",
                        "label": __("Customer Group"),
                        "fieldtype": "Link",
                        "options": "Customer Group",

                },
                {
                        "fieldname": "OutletType",
                        "label": __("Outlet Type"),
                        "fieldtype": "Select",
                        "options":"\nAP-Amilma Prime\nAM-Amilma\nCO-Conversion\nPU-Pullout\nDB-Distributor"
                }
	]

};
