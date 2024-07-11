import frappe
import base64
from frappe.utils.file_manager import save_file
from frappe.utils import nowdate
from frappe import _
from hrms.hr.utils import get_holiday_dates_for_employee



@frappe.whitelist()
def get_employee_details(user_id):
    status = ""
    web_url = "http://erp.amilmaicecreams.com"
    
    emp_details = frappe.get_value('Employee', {'user_id': user_id, 'status': 'Active'}, ['name'])
    
    if emp_details:
        status = True
        employee = frappe.get_doc('Employee', emp_details)
        employee_name = employee.employee_name
        emp_id = employee.name
        emp_designation = employee.designation or ""
        emp_image = employee.image
        if emp_image:
            image_url = web_url + emp_image
        else:
            image_url = ""
        
        today = nowdate()
        month_start_date = frappe.utils.data.get_first_day(today)
        month_end_date = frappe.utils.data.get_last_day(today)
        
        attendance_data = frappe.get_all('Attendance', 
            filters={
                'employee': emp_id,
                'attendance_date': ['between', (month_start_date, month_end_date)]
            },
            fields=['status', 'attendance_date']
        )
        
        present_days = len([att for att in attendance_data if att.status == 'Present'])
        absent_days = len([att for att in attendance_data if att.status == 'Absent'])
        holiday_days = len(get_holiday_dates_for_employee(emp_details,month_start_date,month_end_date))
        # holiday_days = len([att for att in attendance_data if att.status == 'Holiday'])
        leave_days = len([att for att in attendance_data if att.status == 'On Leave'])
    else:
        status = False
        present_days = absent_days = holiday_days = leave_days = 0
        employee_name = emp_id = emp_designation = image_url = ""

    profile_dashboard = {
        "personal_details": [
            {
                "name": employee_name,
                "employee_id": emp_id,
                "designation": emp_designation,
                "location": "Rasipuram",
                "image": image_url
            }
        ],
        "performance": [
            {
                "rank": employee_name,
                "rating": emp_id,
                "placement": emp_designation,
                "t vs a": "Rasipuram",
                "freezer avg": image_url
            }
        ],
        "attendance_count": [
            {
                "present_days": present_days ,
                "absent_days": absent_days,
                "holiday": holiday_days,
                "leave": leave_days
            }
        ]
    }

    return {'status': status, 'message': _('Successfully'), 'Profile Dashboard': profile_dashboard}

#the below code is updating the employee profile image employee MIS in ERPNEXT
@frappe.whitelist()
def set_profile_image_emp_mis(user_id,image):
    try:
        get_emp_id = frappe.db.get_value('Employee',{'user_id':user_id,'status':"Active"},['name'])
        if get_emp_id:
            decoded_data=base64.b64decode((image))
            employee = frappe.get_doc('Employee', get_emp_id)
            file_name = f"{employee.employee_name.replace(' ', '_')}_image.png"
            file_url = save_file(file_name, decoded_data, 'Employee', get_emp_id, is_private=0)
            employee.image = file_url.file_url
            employee.save(ignore_permissions=True)
            frappe.db.commit()
            return {"status":"True","message":"Image Updated"}
    except:
        return {"status":"false","message":"Image Not Updated"}
   