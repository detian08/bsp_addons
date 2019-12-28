# -*- encoding: utf-8 -*-
from odoo import models, api, fields


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.onchange('product_id')
    def set_partner(self):
        for each in self:
            if each.product_id:
                each.product_id.write({'order_partner_id': each.order_id.partner_id.id})

    purchase_date = fields.Datetime(comodel_name='purchase.order', string='Purchase Date',
                                    related='order_id.date_order', store=True)
    state = fields.Selection(comodel_name='purchase.order', string='State', related='order_id.state')