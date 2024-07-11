// Copyright (c) 2023, Vivek and contributors
// For license information, please see license.txt

frappe.ui.form.on('Amilma Target Setting', {
	target_to(frm){
		if(frm.doc.target_from){
			if(frm.doc.target_to){
				frappe.call({
					method:"amilma_custom.amilma_custom.doctype.amilma_target_setting.amilma_target_setting.get_month",
					args:{
						from_date:frm.doc.target_from,
					},
					callback(r){
						if(r.message){
							frm.set_value('month',r.message)
						}
					}
				})	
			}
		}
		else{
			frappe.throw(__("Please Select from date and then select the to date"));
		}
	}
});
