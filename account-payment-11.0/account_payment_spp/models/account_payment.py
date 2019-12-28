# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    spp_id = fields.Many2one(
        'spp', 'Surat Permintaan Pembayaran',
        domain=[('state', 'in', ['approved', 'open', 'paid'])])
