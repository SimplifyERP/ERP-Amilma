frappe.ui.form.on("Purchase Order",{
    // refresh:function(frm){
    //     if(!frm.doc.__islocal){
    //         if(frm.doc.custom_api_method_marked ==1){
    //             if(frm.doc.company){
    //                 if(frm.doc.total > 0.0){
    //                     frappe.db.get_value('Purchase Taxes and Charges',{'company':frm.doc.company},['name'],function(value){
    //                         frm.set_value('taxes',value.name)
    //                         frm.save()
    //                     })
    //                 }
    //             }
    //         }  
    //     }
    // }
})