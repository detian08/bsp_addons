# -*- coding: utf-8 -*-

from odoo import _, models, fields, api


class SelectInvoices(models.TransientModel):
    _name = 'select.invoices'

    invoice_ids = fields.Many2many('account.invoice',
                                   'kontra_bon_invoice_rel',
                                   'kontrabon_id', 'invoice_id',
                                   string='Bill/Inovice')

    @api.multi
    def select_invoices(self):
        kontrabon_id = self.env['kontra.bon'].browse(self._context.get('active_id', False))
        for invoice in self.invoice_ids:
            self.env['kontra.bon.line'].create({
                'invoice_id': invoice.id,
                'kontrabon_id': kontrabon_id.id,
                'amount_payment': invoice.residual
            })
        kontrabon_id._update_link_account_invoice(kontrabon_id.id)