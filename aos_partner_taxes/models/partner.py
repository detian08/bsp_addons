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
class WhtTaxAccountInvoice(models.Model):
    _inherit = 'account.invoice'

    amount_wht = fields.Monetary(string='Withholding Tax Amount',
                                 store=True,
                                 readonly=True,
                                 compute='_compute_amount_wht',
                                 track_visibility='always')
    amount_other_tax = fields.Monetary(string='Other Tax(es) Amount',
                                       store=True,
                                       readonly=True,
                                       compute='_compute_amount_wht',
                                       track_visibility='always')

    @api.multi
    @api.depends('amount_untaxed', 'partner_id')
    def _compute_amount_wht(self):
        for invoice in self:
            for wht_tax_item in invoice.partner_id.supplier_taxes_wth_id.filtered(lambda r: r.amount != 0):
                value = wht_tax_item.amount
                invoice.amount_wht += invoice.amount_untaxed * (value / 100.0)
            invoice.amount_other_tax = invoice.amount_tax - invoice.amount_wht
            clear_wht = False
            if not invoice.invoice_line_ids:
                clear_wht = True
            else:
                for line in invoice.invoice_line_ids:
                    if not line.invoice_line_tax_ids:
                        clear_wht = True
                    else:
                        wht_tax = line.invoice_line_tax_ids.filtered(lambda r: r.tax_witholding == True)
                        if not wht_tax:
                            clear_wht = True
            if clear_wht:
                invoice.amount_wht = 0
                invoice.amount_other_tax = invoice.amount_tax - invoice.amount_wht
            else:
                for wht_tax_item in wht_tax:
                    value = wht_tax_item.amount
                    invoice.amount_wht += invoice.amount_untaxed * (value / 100.0)
                invoice.amount_other_tax = invoice.amount_tax - invoice.amount_wht
        debug = 0


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

    amount_wht = fields.Monetary(string='Withholding Tax Amount',
                                 store=True,
                                 compute='_compute_amount_wht',
                                 track_visibility='onchange')
    amount_other_tax = fields.Monetary(string='Other Taxes',
                                       store=True,
                                       compute='_compute_amount_wht',
                                       track_visibility='onchange')

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
    @api.multi
    @api.depends('amount_untaxed', 'partner_id','amount_tax','order_line.taxes_id'  )
    def _compute_amount_wht(self):
        for order in self:
            for wht_tax_item in order.partner_id.supplier_taxes_wth_id.filtered(lambda r: r.amount != 0):
                value = wht_tax_item.amount
                order.amount_wht += order.amount_untaxed * (value / 100.0)
            order.amount_other_tax = order.amount_tax - order.amount_wht
            clear_wht = False
            if not order.order_line:
                clear_wht = True
            else:
                for line in order.order_line:
                    if not line.taxes_id:
                        clear_wht = True
                    else:
                        wht_tax = line.taxes_id.filtered(lambda r: r.tax_witholding == True)
                        if not wht_tax:
                            clear_wht = True
            if clear_wht:
                order.amount_wht = 0
                order.amount_other_tax = order.amount_tax - order.amount_wht
            else:
                for wht_tax_item in wht_tax:
                    value = wht_tax_item.amount
                    order.amount_wht += order.amount_untaxed * (value / 100.0)
                order.amount_other_tax = order.amount_tax - order.amount_wht
            debug = 0

    @api.multi
    @api.onchange('order_line.product_id', 'order_line.taxes_id')
    def _recompute_amount_wht(self):
        for wht_tax_item in self.partner_id.supplier_taxes_wth_id.filtered(lambda r: r.amount != 0):
            value = wht_tax_item.amount
            self.amount_wht += self.amount_untaxed * (value / 100.0)
        self.amount_other_tax = self.amount_tax - self.amount_wht
        clear_wht = False
        if not self.order_line:
            clear_wht = True
        else:
            for line in self.order_line:
                if not line.taxes_id:
                    clear_wht = True
                else:
                    wht_tax = line.taxes_id.filtered(lambda r: r.tax_witholding == True)
                    if not wht_tax:
                        clear_wht = True
        if clear_wht:
            self.amount_wht = 0
            self.amount_other_tax = self.amount_tax - self.amount_wht
        debug = 0


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
        other_tax = []
        if self:
            with_ht_tax = self[0].order_id.partner_id.supplier_taxes_wth_id
            other_tax = self[0].order_id.partner_id.supplier_taxes_id
        for line in self:
            fpos = line.order_id.fiscal_position_id or line.order_id.partner_id.property_account_position_id
            # If company_id is set, always filter taxes by the company
            taxes = line.product_id.supplier_taxes_id.filtered(
                lambda r: not line.company_id or r.company_id == line.company_id)
            if with_ht_tax  and line.product_id.type == 'service':
                taxes |= with_ht_tax
            if other_tax:
                taxes |= other_tax
            # for tax_item in with_ht_tax:
            #     taxes(0,0,tax_item)
            line.taxes_id = fpos.map_tax(taxes, line.product_id, line.order_id.partner_id) if fpos else taxes
