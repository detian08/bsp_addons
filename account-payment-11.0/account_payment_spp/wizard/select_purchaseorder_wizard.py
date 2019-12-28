# -*- coding: utf-8 -*-

from odoo import _, models, fields, api


class SelectPurchaseOrder(models.TransientModel):
    _name = 'select.purchase.order'

    purchaseorder_ids = fields.Many2many('purchase.order', string='Purchase Order')

    @api.multi
    def select_purchaseorders(self):
        spp_id = self.env['spp'].browse(self._context.get('active_id', False))
        if self.payment_type == 'BILL':
            for order in self.purchaseorder_ids:
                self.env['spp.line.bill'].create({
                    'purchaseorder_id': order.id,
                    'spp_id': spp_id.id
                })
        else:
            for order in self.purchaseorder_ids:
                self.env['spp.line'].create({
                    'purchaseorder_id': order.id,
                    'spp_id': spp_id.id
                })
        # spp_id._update_link_account_invoice(spp_id.id)
