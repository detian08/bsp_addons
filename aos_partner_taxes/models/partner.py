# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _

class ResPartner(models.Model):    
    _inherit = "res.partner"
    
    day_tt = fields.Char('Day Transfer')
    day_invoice = fields.Char('Day Invoice')
    vendor_tax = fields.Char('Vendor Tax No.')
    pkp_no = fields.Char('PKP No.')
    admin_tax_name = fields.Char('Admin Tax Name')
    admin_tax_email = fields.Char('Admin Tax Email')
    admin_tax_wp = fields.Char('WP')
    
    taxes_id = fields.Many2many('account.tax', 'partner_taxes_rel', 'part_id', 'tax_id', string='Customer Taxes',
        domain=[('type_tax_use', '=', 'sale'),('tax_witholding','=',False)])
    taxes_wth_id = fields.Many2many('account.tax', 'partner_taxes_wth_rel', 'part_id', 'tax_id', string='Customer Taxes Withholding',
        domain=[('type_tax_use', '=', 'sale'),('tax_witholding','=',True)])
    supplier_taxes_id = fields.Many2many('account.tax', 'partner_supplier_taxes_rel', 'part_id', 'tax_id', string='Vendor Taxes',
        domain=[('type_tax_use', '=', 'purchase'),('tax_witholding','=',False)])
    supplier_taxes_wth_id = fields.Many2many('account.tax', 'partner_supplier_wth_taxes_rel', 'part_id', 'tax_id', string='Vendor Taxes Withholding',
        domain=[('type_tax_use', '=', 'purchase'),('tax_witholding','=',True)])
    
class AccountTax(models.Model):
    _inherit = 'account.tax'
     
    tax_witholding = fields.Boolean(help='Set this field to true if this tax is for tax witholding')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
