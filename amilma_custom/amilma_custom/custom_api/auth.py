import frappe
from frappe.utils.password import check_password,get_decrypted_password

# ,route='/api/mobile/login'
@frappe.whitelist(allow_guest=True)
def check_user_login(username,password):
    image_url = ""
    web_url = ""
    try:
        user = frappe.get_doc("User", username)
        web_url = "http://erp.amilmaicecreams.com"
        emp_details = frappe.db.get_value('Employee',{'user_id':username,'status':'Active'},['name'])
        if emp_details:
            employee = frappe.get_doc('Employee',emp_details)
            emp_image = employee.image
            if emp_image:
                image_url = web_url + emp_image
            else:
                image_url = ""   
            if user and check_password(user.name,password):
                return {
                    "Status" : True,
                    "Message" : "Successfully login",
                    "userinfo" : {
                            "full_name" : user.full_name,
                            "user_name" : username,
                            "user_email" : user.email,
                            "image":image_url,
                            "emp_id":emp_details
                    },
                }
    except Exception as e:
        # log the error
        frappe.log_error(message=str(e))
        return {
                "Status" : False,
                "Message" : "Login failed",
                "Exception":str(e),
                }