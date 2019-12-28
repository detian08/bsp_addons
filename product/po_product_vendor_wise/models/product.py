# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class ProductProduct(models.Model):
    _inherit = "product.product"
    
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if args is None:
            args = []

        if self.env.context.get('search_default_seller_id'):
            supplier_args = args + [('seller_ids.name.id', '=', self.env.context['search_default_seller_id'])]
            products = super(ProductProduct, self).name_search(name, args=supplier_args, operator=operator, limit=limit)
            if products:
                return products

        return super(ProductProduct, self).name_search(name, args=args, operator=operator, limit=limit)
