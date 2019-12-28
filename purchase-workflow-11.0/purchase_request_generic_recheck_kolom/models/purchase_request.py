from odoo import api, fields, models
from odoo.exceptions import Warning, ValidationError

class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    @api.multi
    def create(self, vals):
        if not vals.get('department_id'):
            raise ValidationError('please fill in the department column')
        if not vals.get('assigned_to'):
            raise ValidationError('please fill in the approver column')
        if not vals.get('line_ids'):
            raise ValidationError('please fill in the product column')
        return super(PurchaseRequest, self).create(vals)


class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'

    @api.onchange('product_id')
    def product_id_spec_onchange(self):
        if self.product_id:
            product = self.product_id
            rectext = []
            text_line = ""
            idx = 0
            for rec in product.attribute_line_ids:
                text_line = rec[idx].attribute_id.name + ' : ' + rec[idx].value_ids.name
                rectext.append(text_line)
            self.specifications = rectext