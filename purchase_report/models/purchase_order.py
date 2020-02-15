from odoo import fields, models, api, _
from datetime import datetime, timedelta

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    create2_uid = fields.Many2one('res.users', 'Create By')
    acknowledge_uid = fields.Many2one('res.users', 'Acknowledge')
    acknowledge2_uid = fields.Many2one('res.users', 'Acknowledge 2')
    approve_uid = fields.Many2one('res.users', 'Approved By')

    def get_date(self, date=''):
        if date :
            date = (date + timedelta(hours=7)).strftime('%Y-%m-%d')
        return date
