# -*- coding: utf-8 -*-
# (C) 2018 Smile (<http://www.smile.fr>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    property_account_payable_advance_id = fields.Many2one(
        'account.account', "Account Advance Payable",
        domain=[
            ('internal_type', '=', 'other'),
            ('deprecated', '=', False),
        ], company_dependent=True)
    property_account_receivable_advance_id = fields.Many2one(
        'account.account', "Account Advance Receivable",
        domain=[
            ('internal_type', '=', 'other'),
            ('deprecated', '=', False),
        ], company_dependent=True)

    # def compute_get_adv_ap(self):
    #     val = ''
    #     ir_property_obj = self.env['ir.property']
    #     val = ir_property_obj.get('property_account_payable_advance_id', 'res.partner')
    #     return val
    #
    # def compute_get_adv_ar(self):
    #     val = ''
    #     ir_property_obj = self.env['ir.property']
    #     val = ir_property_obj.get('property_account_receivable_advance_id', 'res.partner')
    #     return val
    #
    # @api.onchange('name')
    # def _set_advance_account(self):
    #     ir_property_obj = self.env['ir.property']
    #     if not self.property_account_receivable_advance_id:
    #         self.property_account_receivable_advance_id = ir_property_obj.get('property_account_receivable_advance_id',
    #                                                                           'res.partner')
    #     if not self.property_account_payable_advance_id:
    #         self.property_account_payable_advance_id = ir_property_obj.get('property_account_payable_advance_id',
    #                                                                        'res.partner')
    # # @api.model
    # # def create(self, vals):
    # #     res = super(ResPartner,self).create(vals)
    # #     ir_property_obj = self.env['ir.property']
    # #     if not self.property_account_receivable_advance_id:
    # #         self.property_account_receivable_advance_id = ir_property_obj.get('property_account_receivable_advance_id',
    # #                                                                           'res.partner')
    # #     if not self.property_account_payable_advance_id:
    # #         self.property_account_payable_advance_id = ir_property_obj.get('property_account_payable_advance_id',
    # #                                                                        'res.partner')
    #
    #
    # property_account_payable_advance_id = fields.Many2one(
    #     'account.account', "Account Advance Payable",
    #     domain=[
    #         ('internal_type', '=', 'other'),
    #         ('deprecated', '=', False),
    #     ],
    #     company_dependent=True,
    #     default=compute_get_adv_ap,
    #     track_visibility='onchange'
    # )
    # property_account_receivable_advance_id = fields.Many2one(
    #     'account.account', "Account Advance Receivable",
    #     domain=[
    #         ('internal_type', '=', 'other'),
    #         ('deprecated', '=', False),
    #     ], company_dependent=True,
    #     default=compute_get_adv_ar,
    #     track_visibility='onchange'
    # )
