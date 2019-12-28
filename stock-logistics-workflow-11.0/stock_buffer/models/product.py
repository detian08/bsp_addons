from odoo import fields, models


class Product(models.Model):
    _inherit = 'product.template'

    qty_buffer = fields.Float(string='Buffer Qty', help='Monthly Buffer Qty')