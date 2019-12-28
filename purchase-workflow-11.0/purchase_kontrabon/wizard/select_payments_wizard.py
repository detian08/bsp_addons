# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SelectPayments(models.TransientModel):
    _name = 'select.payments'

    payments_ids = fields.Many2many('account.invoice', string='Products')
    flag_order = fields.Char('Flag Order')

    @api.multi
    def select_payments(self):
            kontrabon_id = self.env['purchase.kontrabon'].browse(self._context.get('active_id', False))
            i = 1
            for payment in self.payments_ids:
                self.env['purchase.kontrabon.line'].create({
                    'line_item': i,
                    'invoice_date': payment.date_invoice,
                    'invoice_no': payment.number,
                    'invoice_amount': payment.amount_total_signed,
                    'remark': '',
                    'kontrabon_id':kontrabon_id.id
                })
                i += 1