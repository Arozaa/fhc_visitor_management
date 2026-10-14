"""Host Department DocType Controller."""

import frappe
from frappe.model.document import Document


class HostDepartment(Document):
    def validate(self):
        # Ensure department code is uppercase
        if self.department_code:
            self.department_code = self.department_code.upper().strip()
