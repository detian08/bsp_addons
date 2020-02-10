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

    taxes_id = fields.Many2many('account.tax',
                                'partner_taxes_rel',
                                'part_id',
                                'tax_id',
                                string='Customer Taxes',
                                domain=[('type_tax_use', '=', 'sale'),
                                        ('tax_witholding', '=', False)])
    taxes_wth_id = fields.Many2many('account.tax',
                                    'partner_taxes_wth_rel',
                                    'part_id',
                                    'tax_id',
                                    string='Customer Withholding Taxes ',
                                    domain=[('type_tax_use', '=', 'sale'),
                                            ('tax_witholding', '=', True)])
    supplier_taxes_id = fields.Many2many('account.tax',
                                         'partner_supplier_taxes_rel',
                                         'part_id',
                                         'tax_id',
                                         string='Vendor Taxes',
                                         domain=[('type_tax_use', '=', 'purchase'),
                                                 ('tax_witholding', '=', False)])
    supplier_taxes_wth_id = fields.Many2many('account.tax',
                                             'partner_supplier_wth_taxes_rel',
                                             'part_id',
                                             'tax_id',
                                             string='Vendor Withholding Taxes ',
                                             domain=[('type_tax_use', '=', 'purchase'),
                                                     ('tax_witholding', '=', True)])


class AccountTax(models.Model):
    _inherit = 'account.tax'

    tax_witholding = fields.Boolean(help='Set this field to true if this tax is for tax witholding')

#
# class WhtTaxAccountInvoice(models.Model):
#     _inherit = 'account.invoice'
#
#     amount_wht = fields.Monetary(string='Withholding Tax Amount',
#                                  # store=True,
#                                  # readonly=True,
#                                  # compute='_compute_amount_wht',
#                                  track_visibility='always')
#     amount_after_wht = fields.Monetary(string='Amount after Withholding Tax',
#                                        # store=True,
#                                        # readonly=True,
#                                        # compute='_compute_amount_wht',
#                                        track_visibility='always')
#     amount_before_wht = fields.Monetary(string='Amount before Withholding Tax',
#                                         # store=True,
#                                         # readonly=True,
#                                         # compute='_compute_amount_wht',
#                                         track_visibility='always')
#
#     # @api.one
#     # @api.depends('amount_total', 'amount_untaxed','partner_id')
#     def _compute_amount_wht(self):
#         amount_withht = 0
#         # for with_ht_item in self.partner_id.supplier_taxes_wth_id:
#         #     amount_withht += with_ht_item._compute_amount(self.amount_untaxed,
#         #                                                   self.amount_untaxed,
#         #                                                   1)
#         # return amount_withht
#
#     @api.one
#     @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'tax_line_ids.amount_rounding',
#                  'currency_id', 'company_id', 'date_invoice', 'type')
#     def _compute_amount(self):
#         debug = 0
#
# class WhtTaxAccountInvoiceLine(models.Model):
#     _inherit = 'account.invoice.line'
#
#
#     @api.multi
#     @api.depends('order_id.partner_id')
#     def _compute_amount_wht(self):
#         debug = 0
#
#     amount_wht_line = fields.Monetary(string='Withholding Tax Amount',
#                                  store=True,
#                                  # compute='_compute_amount_wht_line',
#                                  track_visibility='onchange')

class WhtTaxPurchaseOrder(models.Model):
    _inherit = "purchase.order"

    # amount_wht = fields.Monetary(string='Withholding Tax Amount',
    #                              store=True,
    #                              # compute='_compute_amount_wht',
    #                              track_visibility='onchange')
    # amount_after_wht = fields.Monetary(string='Amount after Withholding Tax',
    #                                    store=True,
    #                                    # compute='_compute_amount_wht',
    #                                    track_visibility='onchange')
    # amount_before_wht = fields.Monetary(string='Amount before Withholding Tax',
    #                                     store=True,
    #                                     # compute='_compute_amount_wht',
    #                                     track_visibility='onchange')
    #
    # # amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all', track_visibility='always')
    # # amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all')
    # # amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all')
    #
    # @api.multi
    # @api.depends('amount_untaxed', 'partner_id')
    # def _compute_amount_wht(self):
    #     debug = 0

class WhtTaxPurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"
    #
    #
    # amount_wht_line = fields.Monetary(string='Withholding Tax Amount',
    #                              store=True,
    #                              # compute='_compute_amount_wht_line',
    #                              track_visibility='onchange')
    # amount_after_wht_line = fields.Monetary(string='Amount after Withholding Tax',
    #                                    store=True,
    #                                    # compute='_compute_amount_wht_line',
    #                                    track_visibility='onchange')
    # amount_before_wht_line = fields.Monetary(string='Amount before Withholding Tax',
    #                                     store=True,
    #                                     # compute='_compute_amount_wht_line',
    #                                     track_visibility='onchange')

    @api.multi
    def _compute_tax_id(self):
        with_ht_tax = []
        if self:
            with_ht_tax = self[0].order_id.partner_id.supplier_taxes_wth_id
        for line in self:
            fpos = line.order_id.fiscal_position_id or line.order_id.partner_id.property_account_position_id
            # If company_id is set, always filter taxes by the company
            taxes = line.product_id.supplier_taxes_id.filtered(lambda r: not line.company_id or r.company_id == line.company_id)
            if with_ht_tax:
                taxes |= with_ht_tax
            # for tax_item in with_ht_tax:
            #     taxes(0,0,tax_item)
            line.taxes_id = fpos.map_tax(taxes, line.product_id, line.order_id.partner_id) if fpos else taxes