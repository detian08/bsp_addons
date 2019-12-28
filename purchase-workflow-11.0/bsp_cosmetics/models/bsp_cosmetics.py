from odoo import api, fields, models

class Partner(models.Model):
    _inherit = 'res.partner'

    street = fields.Char(required=True)
    vat = fields.Char(required=True)
    city = fields.Char(required=True)
    country_id = fields.Many2one(required=True)
    phone = fields.Char(required=True)
    child_ids = fields.One2many(required=True)
    bank_ids = fields.One2many(required=True)
    industry_id = fields.Many2one(required=True)
    company_id = fields.Many2one(required=True)
    property_supplier_payment_term_id = fields.Many2one(required=True)
    property_account_receivable_advance_id = fields.Many2one(required=True)
    property_account_payable_advance_id = fields.Many2one(required=True)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    default_code = fields.Char(required=True)
    company_id = fields.Many2one(required=True)
    property_account_expense_id = fields.Many2one(required=True)


class Company(models.Model):
    _inherit = 'res.company'

    street = fields.Char(required=True)
    vat = fields.Char(required=True, string="NPWP")
    city = fields.Char(required=True)
    country_id = fields.Many2one(required=True)
    phone = fields.Char(required=True)
    parent_id = fields.Many2one(required=True)


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    department_id = fields.Many2one(required=True)
    assigned_to = fields.Many2one(required=True)


class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'

    product_id = fields.Many2one(required=True)
    product_qty = fields.Float(required=True)

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


class AccountPayment(models.Model):
    _inherit = 'account.payment'
    _order = 'payment_date asc'