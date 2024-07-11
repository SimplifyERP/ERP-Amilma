import frappe
from frappe.utils import now,getdate,today
import json
import base64
from frappe.utils.file_manager import save_file


@frappe.whitelist()
def log_employee_checkin(log_type, email, latitude, longitude, live_location,image,route,work_done):
    emp =  frappe.db.get_value('Employee',{'user_id': str(email)},'name')
    
    exists = frappe.db.sql(f"""  
            SELECT
                emp.name,
                emp.time
            FROM `tabEmployee Checkin` emp
            WHERE emp.employee = '{emp}' 
            AND DATE_FORMAT(emp.time, '%Y-%m-%d') = DATE_FORMAT('{frappe.utils.now()}', '%Y-%m-%d')
            AND emp.log_type = "{log_type}"
        """, as_dict=1)
    if len(exists)>=1:
        return{'status': 'error','message': f'Entry already exists for {emp} with log_type {log_type}'}
    if len(exists) <= 0:
        emch = frappe.get_doc({
            'doctype': 'Employee Checkin',
            'employee': emp,
            'log_type': log_type,
            'time': frappe.utils.now(),
            'custom_punch_date':getdate(today()),
            'latitude': latitude,
            'longitude': longitude,
            'live_location': json.dumps({"type":"FeatureCollection","features":[{"type":"Feature","properties":{},"geometry":{"type":"Point","coordinates":[longitude,latitude]}}]}),
        })
        emch.insert(ignore_permissions=True)
        frappe.db.commit()

        get_checkin_id = frappe.db.get_value('Employee Checkin',{'employee':emp,'custom_punch_date':getdate(today()),'log_type':log_type},['name'])
        if get_checkin_id:
            decoded_data=base64.b64decode((image))
            update_checkin = frappe.get_doc('Employee Checkin',get_checkin_id)
            file_name = f"{update_checkin.employee_name.replace(' ', '_')}_image.png"
            file_url = save_file(file_name, decoded_data, 'Employee Checkin', get_checkin_id, is_private=0)
            update_checkin.custom_image = file_url.file_url
            if update_checkin.log_type == "IN":
                update_checkin.custom_employee_route = route
            elif update_checkin.log_type == "OUT":
                update_checkin.custom_work_done = work_done    
            update_checkin.save(ignore_permissions=True)
            frappe.db.commit()

        return{'status': 'success','message': f"Successfully saved Employee Checkin with name: {emch.name}"}


