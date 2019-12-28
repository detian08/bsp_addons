from odoo import api, fields, models, _


class OperationType(models.Model):
    _inherit = 'stock.picking.type'

    department_ids = fields.Many2many('hr.department', string='Eligible Department')



class EligibleDept(models.Model):
    _inherit = "hr.department"

    operationtype_ids = fields.Many2many('stock.picking.type', string='Eligible Picking Type')
