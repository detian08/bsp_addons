from odoo import models, api, fields


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    kontrabon_id = fields.Many2one("kontra.bon", "Bill of Kontra Bon")

    @api.onchange('kontrabon_id')
    def onchange_kontrabon_id(self):
        if self.kontrabon_id:
            amount_payment_total = 0.0
            invoices = []
            for line in self.kontrabon_id.invoice_line_ids:
                if line.amount_payment > 0 :
                    invoices.append(line.invoice_id)
                    amount_payment_total += line.amount_payment

            # payment = self.env['account.payment']
            self.update({
                'amount': amount_payment_total,
                'invoice_ids' : invoices,
                'partner_id' : self.kontrabon_id.partner_id
            })

