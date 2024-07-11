// Copyright (c) 2024, Vivek and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales GST Filling"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "reqd": 1,
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "reqd": 1,
        },
        {
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "on_change": () => {
                var company = frappe.query_report.get_filter_value('company');
                if(company){
                    fetchCompanyAddress();
                }
                else{
                    frappe.query_report.set_filter_value('address',""); 
                }
                
            }
        },
        {
            "fieldname": "address",
            "label": __("Address"),
            "fieldtype": "Text",
            "read_only":1,
            "input_css": {"max-width": "700px","max-height":"150px"} // Adjust the max-width according to your preference
        }
        
    ]
};
function fetchCompanyAddress() {
    var company = frappe.query_report.get_filter_value('company');
    frappe.call({
        method: "amilma_custom.amilma_custom.report.sales_gst_filling.sales_gst_filling.get_address",
        args: {
            company: company
        },
        callback: function(r) {
            if (r.message) {
                frappe.query_report.set_filter_value('address', r.message);
            }
        }
    });
}

