# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from datetime import date

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    amount_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percentage', 'Percentage of balance')
    ], required=True, default='fixed')

    amount_percentage = fields.Float('Percentage(%)')
    total_tagihan = fields.Float(string="Total Tagihan", store=False)
    rekanan = fields.Char(string="Vendor", store=False)


    @api.onchange('amount_percentage', 'amount_type', 'amount')
    def _compute_advance_amount(self):
        total_tagihan = self.purchase_id.amount_total
        rekanan = self.partner_id.name
        if (len(self.partner_id.bank_ids)>0):
            rekanan += "\n"
            for line in self.partner_id.bank_ids:
                rekanan += " \n Bank: "
                rekanan += line.bank_id.name
                rekanan += ' No Rek: '
                rekanan += line.acc_number
        self.update({'total_tagihan': total_tagihan, 'rekanan': rekanan})
        if self.purchase_id:
            if self.amount_type == "percentage":
                if self.amount_percentage <= 100:
                    amount = self.purchase_id.amount_total * (self.amount_percentage / 100)
                    self.update({'amount':amount})

                else:
                    self.update({'amount_percentage': 0})
                    self.update({'amount': 0})
                    return {
                        'warning': {
                            'title': 'PERHATIAN !',
                            'message': 'CICILAN HARUS DIBAWAH 100%',
                        }
                    }

            else:
                self.update({'amount_percentage': 0})
                if self.amount > self.purchase_id.amount_total:
                    self.update({'amount_percentage': 0, 'amount': 0})
                    return {
                        'warning': {
                            'title': 'PERHATIAN !',
                            'message': 'PEMBAYARAN MELEBIHI JUMLAH TAGIHAN',
                        }
                    }

    @api.multi
    def post(self):
        self.payment_date = date.today().strftime('%Y-%m-%d')
        return super(AccountPayment, self).post()