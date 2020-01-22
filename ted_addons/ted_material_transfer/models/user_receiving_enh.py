from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare


class UserReceivingEnh(models.Model):
    _inherit = 'material.transfer'

    @api.onchange('order_id')
    def _order_id_onchange(self):
        if self.order_id:
            order = self.order_id
            dept_ids = [-1]
            pr_ids = [-1]
            # to-do: add logic for receiving employee
            # executed by: ted
            # executed at: 20191104
            emp_ids = [-1]
            # finished at: -
            for oline in order.order_line:
                prlines = oline.purchase_request_lines
                if len(prlines) > 0:
                    if not self.department_id:
                        self.department_id = prlines.request_id.department_id.id
                    dept_ids += [x.department_id.id for x in prlines if x]
                    pr_ids += [x.request_id.id for x in prlines if x]
                    emp_ids += [x.request_id.employee_id for x in prlines if x]
            if self.department_id:
                return {'domain': {'department_id': [('id', 'in', dept_ids)]}}
            # else:
            #     if len(pr_ids) > 0:
            #         self.request_id = pr_ids[0]
            #     return {'domain': {'request_id': [('id', 'in', pr_ids)]}}
            elif self.request_id:
                if len(pr_ids) > 0:
                    self.request_id = pr_ids[0]
                return {'domain': {'request_id': [('id', 'in', pr_ids)]}}
            elif self.employee_id:
                if len(pr_ids) > 0:
                    self.employee_id = emp_ids[0]
                return {'domain': {'request_id': [('id', 'in', emp_ids)]}}
            else:
                return {}
        else:
            return {}

    @api.onchange('department_id')
    def _department_id_onchange(self):
        if self.department_id:
            pr_ids = [-1]
            emp_ids = [-1]
            order = self.order_id
            for oline in order.order_line:
                prlines = oline.purchase_request_lines
                if len(prlines) > 0:
                    if not self.request_id:
                        self.request_id = prlines.request_id.id
                    pr_ids += [x.request_id.id for x in prlines if x]
                    emp_ids += [x.request_id.employee_id for x in prlines if x]
            # return {'domain': {'request_id': [('id', 'in', pr_ids), ('department_id', '=', self.department_id.id)]}}
            if self.request_id:
                if len(pr_ids) > 0:
                    self.request_id = pr_ids[0]
                return {'domain': {'request_id': [('id', 'in', pr_ids)]}}
            elif self.employee_id:
                if len(pr_ids) > 0:
                    self.employee_id = emp_ids[0]
                return {'domain': {'request_id': [('id', 'in', emp_ids)]}}
            else:
                return {}
        else:
            return {}

    @api.onchange('request_id')
    def _request_id_onchange(self):
        if self.order_id and self.request_id:
            emp_ids = [-1]
            self._add_product_material_transfer_lines(self.request_id)
            order = self.order_id
            for order_line in order.order_line:
                pr_lines = order_line.purchase_request_lines
                if len(pr_lines) > 0:
                    if not self.employee_id:
                        self.employee_id = pr_lines.request_id.employee_id
                    emp_ids += [x.request_id.employee_id for x in pr_lines if x]
        else:
            return {}

    employee_id = fields.Many2one('hr.employee', string="Receiving Employee")
    sender_employee_id = fields.Many2one('hr.employee', string="Sender Employee")
