import datetime as dt

from dateutil.relativedelta import *

import addons.decimal_precision as dp
from odoo import api, fields, models


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    doc_type = fields.Selection([
        ('K0', 'Form-BPPB'),
        ('K1', 'Form-K1'),
        ('K2', 'Form-K2'),
        ('K3', 'Form-K3'),
        ('K4', 'Form-K4')
    ], string='Doc Type', readonly=False, index=True, copy=False, default='K0')
    @api.model
    def _get_default_name(self):
        # return self.env['ir.sequence'].next_by_code('purchase.request')
        name_retval = '-'
        return name_retval

    @api.depends('line_ids.price_unit', 'line_ids.discount',
                 'line_ids.estimated_cost1', 'line_ids.estimated_cost2', 'line_ids.estimated_cost3')
    def _amount_all(self):
        for order in self:
            net_amount_total = est_amount_total = est_amount_total1 = est_amount_total2 = est_amount_total3 = 0.0
            for line in order.line_ids:
                est_amount_total += line.estimated_cost
                net_amount_total += line.net_price_subtotal
                est_amount_total1 += line.estimated_cost1
                est_amount_total2 += line.estimated_cost2
                est_amount_total3 += line.estimated_cost3
            order.update({
                'est_amount_total': est_amount_total,
                'net_amount_total': net_amount_total,
                'est_amount_total1': est_amount_total1,
                'est_amount_total2': est_amount_total2,
                'est_amount_total3': est_amount_total3,
            })

    name = fields.Char('Request Reference', required=True,
                       default='New', size=20, readonly=True,
                       track_visibility='onchange')
    date_approve = fields.Date('Approval Date', readonly=1, index=True, copy=False)
    opu_number = fields.Char('OPU Number', size=20, )
    opu_date = fields.Date("OPU Date")
    currency_id = fields.Many2one(related='company_id.currency_id',
                                  store=True, string='Currency',
                                  readonly=True, help='Currency')
    received_doc_date = fields.Date('Received Doc',
                                    help="Date when the user received the formulir/doc.",
                                    default=fields.Date.context_today)
    handover_doc_date = fields.Date('Handover Doc',
                                    help="Date when the user handover the formulir/doc.")
    handover_doc_dept = fields.Many2one('hr.department', string='Handover Dept')
    est_amount_total = fields.Monetary(string='Est Total', store=True, readonly=True, compute='_amount_all',
                                       default=0.0)
    net_amount_total = fields.Monetary(string='Net Total', store=True, readonly=True, compute='_amount_all',
                                       default=0.0)
    est_amount_total1 = fields.Float(string='Est.Total-1', store=True, readonly=True, compute='_amount_all',
                                     default=0.0)
    est_amount_total2 = fields.Float(string='Est.Total-2', store=True, readonly=True, compute='_amount_all',
                                     default=0.0)
    est_amount_total3 = fields.Float(string='Est.Total-3', store=True, readonly=True, compute='_amount_all',
                                     default=0.0)
    employee_id = fields.Many2one('hr.employee', string="Employee")
    is_procurement_ho = fields.Boolean(string='procurement of head office', help="procurement of head office")
    is_approve_2d = fields.Boolean(string='Approv 2 Director', help="Approv 2 Director")
    partner_id = fields.Many2one('res.partner', string='Bid Winner Vendor', help='bid winner vendor',)
                                 # compute='_choose_supplier_id',
                                 # store=True)

    assigned_to = fields.Many2one(
        'res.users', 'Approver', track_visibility='onchange',
        domain=lambda self: ['|', ('groups_id', 'in', self.env.ref(
            'purchase_request.group_purchase_request_manager').id),
                             ('groups_id', 'in', self.env.ref(
                                 'purchase_request.group_purchase_request_user').id)
                             ]
    )

    # TODO: Filter Bid Winnder Supplier dari ID yang ada di line_ids, belum selesai 20191102
    @api.onchange('line_ids.partner_id1', 'line_ids.partner_id2', 'line_ids.partner_id3')
    @api.multi
    def _choose_supplier_id(self):
        ids = []
        for rec in self.line_ids:
            if rec.partner_id1:
                ids += [rec.partner_id1.id]
            if rec.partner_id2:
                ids += [rec.partner_id2.id]
            if rec.partner_id3:
                ids += [rec.partner_id3.id]
        return {'domain': {'partner_id': [('id', 'in', ids)]}}

    @api.onchange('partner_id')
    def _partner_id_onchange(self):
        for rec in self.line_ids:
            if rec.partner_id1.id == self.partner_id.id:
                rec.price_unit = rec.estimated_cost1
            elif rec.partner_id2.id == self.partner_id.id:
                rec.price_unit = rec.estimated_cost2
            elif rec.partner_id3.id == self.partner_id.id:
                rec.price_unit = rec.estimated_cost3

    @api.multi
    def button_approved(self):
        super(PurchaseRequest, self).button_approved()
        return self.write({'date_approve': fields.Date.context_today(self)})

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            if vals.get('doc_type') == 'K0':
                vals['name'] = self.env['ir.sequence'].next_by_code('purchase.request.k0') or '/'
            elif vals.get('doc_type') == 'K1':
                vals['name'] = self.env['ir.sequence'].next_by_code('purchase.request.k1') or '/'
            elif vals.get('doc_type') == 'K3':
                vals['name'] = self.env['ir.sequence'].next_by_code('purchase.request.k3') or '/'
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('purchase.request') or '/'
        return super(PurchaseRequest, self).create(vals)

    @api.multi
    def copy(self, default=None):
        default = dict(default or {})
        self.ensure_one()

        if self.doc_type == 'K0':
            default.update({
                'state': 'draft',
                'name': self.env['ir.sequence'].next_by_code('purchase.request.k0'),
            })
        elif self.doc_type == 'K1':
            default.update({
                'state': 'draft',
                'name': self.env['ir.sequence'].next_by_code('purchase.request.k1'),
            })
        elif self.doc_type == 'K2':
            default.update({
            'state': 'draft',
            'name': self.env['ir.sequence'].next_by_code('purchase.request.k2'),
        })
        elif self.doc_type == 'K3':
            default.update({
                'state': 'draft',
                'name': self.env['ir.sequence'].next_by_code('purchase.request.k3'),
            })
        # default.update({
        #     'state': 'draft',
        #     'name': self.env['ir.sequence'].next_by_code('purchase.request'),
        # })
        return super(PurchaseRequest, self).copy(default)


class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'

    @api.depends('net_price', 'product_qty', 'discount', 'price_unit', 'standart_price',
                 'qty_usage_last_month1', 'qty_usage_last_month2', 'qty_usage_last_month3')
    def _compute_amount(self):
        """
        Compute the amounts of the PR line.
        """
        for line in self:
            net_price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            estimated_cost = line.product_qty * line.price_unit
            net_price_subtotal = line.product_qty * net_price
            diff_price = line.standart_price - net_price
            diff_price_percentage = 0
            qty_avg_usage = (line.qty_usage_last_month1 + line.qty_usage_last_month2 + line.qty_usage_last_month3) / 3
            if line.standart_price > 0:
                diff_price_percentage = ((line.standart_price - net_price) / line.standart_price)
            line.update({
                'net_price': net_price,
                'estimated_cost': estimated_cost,
                'net_price_subtotal': net_price_subtotal,
                'diff_price': diff_price,
                'diff_price_percentage': diff_price_percentage,
                'qty_avg_usage': qty_avg_usage,
            })

    @api.onchange('product_id')
    def _set_buffer_qty_strandard_price(self):
        qty = standard_price = 0.0
        if self.product_id:
            product = self.env['product.product']
            objproduct = product.browse(self.product_id.id)
            if objproduct.qty_buffer:
                qty = objproduct.qty_buffer
            if objproduct.standard_price:
                standard_price = objproduct.standard_price
            self.update({'qty_buffer': qty,
                         'standart_price': standard_price})

    @api.onchange('product_id')
    def product_id_onchange(self):
        if self.product_id:
            product = self.product_id
            self.product_uom_id = product.uom_id.id
            return {'domain': {'product_uom_id': [('category_id', '=', product.uom_id.category_id.id)]}}

    price_unit = fields.Float('Price Unit', track_visibility='onchange', digits=dp.get_precision('Price Unit'),
                              default=0.0)
    discount = fields.Float(string='Discount(%)', track_visibility='onchange', digits=dp.get_precision('Discount'),
                            default=0.0)
    net_price = fields.Float('Net.Price', track_visibility='onchange', default=0.0)
    standart_price = fields.Float('Standart Price', track_visibility='onchange', default=0.0)
    net_price_subtotal = fields.Float('SubTotal (Net.Price)', store=True, readonly=True, compute='_compute_amount',
                                      default=0.0)
    diff_price = fields.Float('Diff.Price', store=True, readonly=True, compute="_compute_amount",
                              digits=dp.get_precision('Price Unit'), default=0.0)
    diff_price_percentage = fields.Float('Diff.Price(%)', store=True, readonly=True, compute="_compute_amount",
                                         digits=dp.get_precision('Discount'), default=0.0)
    last_service = fields.Date(string='Last Service', help='Date Last Service history')

    partner_id1 = fields.Many2one('res.partner', string='Vendor1', help='Vendor alternative name',
                                  domain=[('supplier', '=', True)])
    partner_id2 = fields.Many2one('res.partner', string='Vendor2', help='Vendor alternative name',
                                  domain=[('supplier', '=', True)])
    partner_id3 = fields.Many2one('res.partner', string='Vendor3', help='Vendor alternative name',
                                  domain=[('supplier', '=', True)])

    @api.multi
    def _compute_supplier_id(self):
        for rec in self:
            if rec.request_id.partner_id:
                rec.supplier_id = rec.request_id.partner_id
            else:
                if rec.product_id:
                    if rec.product_id.seller_ids:
                        rec.supplier_id = rec.product_id.seller_ids[0].name

    # overwrite field suppplier_id
    supplier_id = fields.Many2one('res.partner',
                                  string='Preferred supplier',
                                  compute="_compute_supplier_id")

    estimated_cost1 = fields.Float(string='Est.Cost1', help='Estimate cost', default=0.0)
    estimated_cost2 = fields.Float(string='Est.Cost2', help='Estimate cost', default=0.0)
    estimated_cost3 = fields.Float(string='Est.Cost3', help='Estimate cost', default=0.0)

    reason_for_request = fields.Text(string='Reason For Request')
    qty_avg_usage = fields.Float(string='Avg Usage Qty', store=True, readonly=True, compute="_compute_amount",
                                 help='Monthly avarage usage qty', default=0.0)
    qty_buffer = fields.Float(string="Buffer Qty", help='Buffer Qty')
    qty_usage_last_month1 = fields.Float(string="Qty Usage M1", help='Qty Usage Last Month (M-1)', default=0.0)
    qty_usage_last_month2 = fields.Float(string="Qty Usage M2", help='Qty Usage Last Month (M-2)', default=0.0)
    qty_usage_last_month3 = fields.Float(string="Qty Usage M3", help='Qty Usage Last Month (M-3)', default=0.0)
    qty_available = fields.Float(string='Last Stock', help='Last Stock Available', default=0.0)
    doc_type = fields.Selection('purchase.request', string='Doc Type', related='request_id.doc_type', store=True)


    @api.multi
    def action_purchase_product_prices(self):
        rel_view_id = self.env.ref(
            'purchase_request_generic.last_product_purchase_prices_view')
        partner_ids = []
        if self.partner_id1.id:
            partner_ids.append(self.partner_id1.id)
        if self.partner_id2.id:
            partner_ids.append(self.partner_id2.id)
        if self.partner_id3.id:
            partner_ids.append(self.partner_id3.id)
        if len(partner_ids) > 0:
            purchase_lines = self.env['purchase.order.line'].search([('product_id', '=', self.product_id.id),
                                                                     ('partner_id', 'in', partner_ids)],
                                                                    order='create_date DESC').mapped('id')
        else:
            purchase_lines = self.env['purchase.order.line'].search([('product_id', '=', self.product_id.id)],
                                                                    order='create_date DESC').mapped('id')
        if not purchase_lines:
            raise Warning("No purchase history found.!")
        else:
            return {
                'domain': [('id', 'in', purchase_lines)],
                'views': [(rel_view_id.id, 'tree')],
                'name': 'Purchase History',
                'res_model': 'purchase.order.line',
                'view_id': rel_view_id.id,
                'type': 'ir.actions.act_window',
                'target': 'new'
            }

    @api.multi
    def action_usage_product_last_3_month(self):
        stockpicking = self.env['stock.picking']
        for i in range(1, 4):
            to_date = self.request_id.date_start
            from_date = dt.datetime.strptime(to_date, '%Y-%m-%d') + relativedelta(months=-i)
            from_date = dt.date(from_date.year, from_date.month, 1)  # first day
            to_date = dt.datetime.strptime(to_date, '%Y-%m-%d')
            to_date = dt.date(to_date.year, to_date.month, 1) - relativedelta(days=1)  # last day
            from_date = from_date.strftime('%Y-%m-%d')
            to_date = to_date.strftime('%Y-%m-%d')
            ids = stockpicking.search([['company_id', '=', self.request_id.company_id.id],
                                       ['scheduled_date', '>=', from_date],
                                       ['scheduled_date', '<=', to_date],
                                       ['state', '=', 'done']]).ids
            if len(ids) > 0:
                stockmove = self.env['stock.move']
                objstockmove = stockmove.search([['picking_id', 'in', ids], ['product_id', '=', self.product_id.id]])
                qty = 0.0
                for move in objstockmove:
                    qty += move.product_uom._compute_quantity(move.product_uom_qty, self.product_uom_id,
                                                              rounding_method='HALF-UP')
                if i == 1:
                    self.write({'qty_usage_last_month1': qty})
                elif i == 2:
                    self.write({'qty_usage_last_month2': qty})
                elif i == 3:
                    self.write({'qty_usage_last_month3': qty})

        return True
