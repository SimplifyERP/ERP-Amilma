import frappe
from frappe.utils import now,getdate,today
from hrms.hr.doctype.leave_application.leave_application import LeaveApplication
from hrms.hr.doctype.leave_application.leave_application import (
	get_leave_balance_on,
	get_leaves_for_period,
)
from typing import Dict, List, Optional, Tuple



class CustomLeaveApplication(LeaveApplication):

    def validate(self):
        frappe.errprint(self.get_leave_balance)
        return super().validate()
    

    def get_leave_balance(self):
        leaves_taken = (get_leaves_for_period(self.employee, self.leave_type, self.from_date, self.to_date) * -1)
        new_allocation, expired_leaves, carry_forwarded_leaves = self.get_allocated_and_expired_leaves(self.from_date, self.to_date, self.employee, self.leave_type)

    def get_allocated_and_expired_leaves(from_date: str, to_date: str, employee: str, leave_type: str) -> Tuple[float, float, float]:
        new_allocation = 0
        expired_leaves = 0
        carry_forwarded_leaves = 0

        records = get_leave_ledger_entries(from_date, to_date, employee, leave_type)

        for record in records:
            # new allocation records with `is_expired=1` are created when leave expires
            # these new records should not be considered, else it leads to negative leave balance
            if record.is_expired:
                continue

            if record.to_date < getdate(to_date):
                # leave allocations ending before to_date, reduce leaves taken within that period
                # since they are already used, they won't expire
                expired_leaves += record.leaves
                expired_leaves += get_leaves_for_period(employee, leave_type, record.from_date, record.to_date)

            if record.from_date >= getdate(from_date):
                if record.is_carry_forward:
                    carry_forwarded_leaves += record.leaves
                else:
                    new_allocation += record.leaves

        return new_allocation, expired_leaves, carry_forwarded_leaves    
    

def get_leave_ledger_entries(from_date: str, to_date: str, employee: str, leave_type: str) -> List[Dict]:
	ledger = frappe.qb.DocType("Leave Ledger Entry")
	records = (
		frappe.qb.from_(ledger)
		.select(
			ledger.employee,
			ledger.leave_type,
			ledger.from_date,
			ledger.to_date,
			ledger.leaves,
			ledger.transaction_name,
			ledger.transaction_type,
			ledger.is_carry_forward,
			ledger.is_expired,
		)
		.where(
			(ledger.docstatus == 1)
			& (ledger.transaction_type == "Leave Allocation")
			& (ledger.employee == employee)
			& (ledger.leave_type == leave_type)
			& (
				(ledger.from_date[from_date:to_date])
				| (ledger.to_date[from_date:to_date])
				| ((ledger.from_date < from_date) & (ledger.to_date > to_date))
			)
		)
	).run(as_dict=True)

	return records

