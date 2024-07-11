frappe.ui.form.on("Sales Order",{
    refresh:function(frm){
        if(!frm.doc.__islocal){
            if(frm.doc.custom_api_method_marked ==1){
                if(frm.doc.company){
                    if(frm.doc.total > 0.0){
                        frappe.db.get_value('Sales Taxes and Charges Template',{'company':frm.doc.company},['name'],function(value){
                            frm.set_value('taxes_and_charges',value.name)
                            frm.save()
                        })
                    }
                }
            }  
        }
    }
})