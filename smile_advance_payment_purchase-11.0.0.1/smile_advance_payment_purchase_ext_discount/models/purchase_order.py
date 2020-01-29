# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AccountPayment(models.Model):
    _inherit = 'purchase.order'

    bsp_po_type = fields.Selection([
        ('general', 'General'),
        ('specific', 'Specific')
    ], 
    string='BSP Print PO Type',
    required=True, 
    default='general')

    total_pembelian = fields.Text('Harga Total Pembelian')
    cara_pembayaran = fields.Text('Cara Pembayaran')
    waktu_pelaksanaan = fields.Text('Waktu Pelaksanaan')
    lokasi_pelaksanaan = fields.Text('Lokasi Pelaksanaan')
    faktur_an = fields.Text('Faktur & Kwitansi a.n')