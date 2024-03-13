# Copyright (c) 2024, tejal kumbhar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class TaskListCompletion(Document):

	def on_update(self):
		self.changes_status_submit()
		self.check_all_complete()
		self.insert_result()

	@frappe.whitelist()
	def changes_status_submit(self):		
		if self.completion_status:			
			for i in self.get("task_completion_details"):
				doc = frappe.get_doc('Equipment Maintenance Order', self.maintenance_order)
				name = frappe.get_value("Maintanance Task List",
										filters={"parent": self.maintenance_order, "maintenance_task": i.parameter, "description": i.parameter_details, "assign_to": self.assign_to},
										fieldname=["name"])

				if name:                                                                      
					if self.completion_status == "Fully Completed":

						frappe.db.set_value('Maintanance Task List', name, 'maintenance_status', 'Completed')
						frappe.db.set_value('Maintanance Task List', name, 'last_completion_date', self.task_completion_date)
						frappe.db.set_value('Maintanance Task List', name, 'equipment_status', self.equipment_status)
					
					else:
						frappe.db.set_value('Maintanance Task List', name, 'maintenance_status', 'Partially Completed')

		
	@frappe.whitelist()
	def check_all_complete(self):
		if self.completion_status:
			doc = frappe.get_doc('Equipment Maintenance Order', self.maintenance_order)
			all_tasks_completed = all(task.maintenance_status == "Completed" for task in doc.get('maintanance_task_list'))

			if all_tasks_completed:

				frappe.db.set_value('Equipment Maintenance Order', self.maintenance_order, 'status', 'Completed')

			else:
				frappe.db.set_value('Equipment Maintenance Order', self.maintenance_order, 'status', 'Open')


	

	@frappe.whitelist()
	def insert_result(self):
		if self.completion_status == "Fully Completed":
			doc = frappe.get_doc('Equipment Maintenance Order', self.maintenance_order)
			if doc:
				for i in self.get("task_completion_details"):
					# Check if the item already exists in the list
					if not any(d.get('parameter') == i.parameter and 
							d.get('parameter_details') == i.parameter_details and 
							d.get('value') == i.value and 
							d.get('assigned_to') == self.assign_to for d in doc.results_of_task_completion):
						doc.append('results_of_task_completion', {
							"assigned_to": self.assign_to,    
							"parameter": i.parameter,
							"parameter_details": i.parameter_details,
							"value": i.value,
							"reading1": i.reading1,
							"reading2": i.reading2,
							"reading3": i.reading3,
							"reading4": i.reading4,
							"reading5": i.reading5,
						})
				doc.save()

