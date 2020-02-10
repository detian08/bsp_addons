from odoo import api, fields, models

class PurchaseOrderDept(models.Model):
    _inherit = "hr.department"

    # purchaseorder_ids = fields.Many2many('purchase.order', string='Purchase Order')

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.multi
    def _default_po_dept(self):
        self._set_po_dept()

    # @api.multi
    # @api.depends('name', 'partner_ref')
    # def name_get(self):
    #     result = []
    #     for po in self:
    #         name = po.name
    #         if po.partner_ref:
    #             name += ' ('+po.partner_ref+')'
    #         if self.env.context.get('show_total_amount') and po.amount_total:
    #             name += ': ' + formatLang(self.env, po.amount_total, currency_obj=po.currency_id)
    #         if self.env.context.get('show_department_name') and po.department_name:
    #             name += ': ' + self.department_name
    #         result.append((po.id, name))
    #     return result

    @api.onchange('name','id')
    def _get_po_dept(self):
        self._set_po_dept()

    @api.multi
    @api.depends('order_line')
    def _set_po_dept(self):
        selected_department = []
        for order in self:
            if order.order_line:
                department_name = ''
                order.department_name = department_name
                for line in order.order_line:
                    if line.purchase_request_lines:
                        for pr_lines in line.purchase_request_lines:
                            department_name = pr_lines.request_id.department_id.name
                if order.department_name:
                    order.department_name = order.department_name +',' + department_name
                else:
                    order.department_name = department_name
        # self.department_ids = selected_department.ids

    department_name = fields.Char( string='Departement',
                                   default=_default_po_dept,
                                   track_visibility='onchange',
                                   compute='_set_po_dept')
    rfq_name = fields.Char(string='RFQ Number', copy=False, readonly=True)

    @api.multi
    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        for purchase in self :
            purchase.write({
                'rfq_name': purchase.name,
                'name': self.env['ir.sequence'].next_by_code('purchase.order'),
            })
        return res

    @api.model
    def create(self, vals):
        sequence_id = self.env.ref('bsp_cosmetics.seq_purchase_rfq')
        vals['name'] = sequence_id.next_by_id()
        return super(PurchaseOrder, self).create(vals)

class Partner(models.Model):
    _inherit = 'res.partner'

    # street = fields.Char(required=True)
    # vat = fields.Char(required=True)
    # city = fields.Char(required=True)
    # country_id = fields.Many2one(required=True)
    # phone = fields.Char(required=True)
    # child_ids = fields.One2many(required=True)
    # bank_ids = fields.One2many(required=True)
    # # industry_id = fields.Many2one()
    # company_id = fields.Many2one(required=True)
    # property_supplier_payment_term_id = fields.Many2one(required=True)

    # property_account_receivable_advance_id = fields.Many2one(required=True)
    # property_account_payable_advance_id = fields.Many2one(required=True)

    def compute_get_adv_ap(self):
        val = ''
        ir_property_obj = self.env['ir.property']
        val = ir_property_obj.get('property_account_payable_advance_id', 'res.partner')
        return val

    def compute_get_adv_ar(self):
        val = ''
        ir_property_obj = self.env['ir.property']
        val = ir_property_obj.get('property_account_receivable_advance_id', 'res.partner')
        return val

    @api.onchange('name')
    def _set_advance_account(self):
        ir_property_obj = self.env['ir.property']
        account_master = self.env['account.account'].search([('company_id', '=', self.company_id.id),
                                                             ('name', '=', 'Prepayments')])
        if not self.property_account_receivable_advance_id:
            # account_data = ir_property_obj.get('property_account_receivable_advance_id','res.partner')
            # self.property_account_receivable_advance_id = account_data.id
            if account_master:
                self.property_account_receivable_advance_id = account_master.id
            debug = True
        if not self.property_account_payable_advance_id:
            debug = True
            # account_data = ir_property_obj.get('property_account_payable_advance_id','res.partner')
            # self.property_account_payable_advance_id = account_data.id
            if account_master:
                self.property_account_payable_advance_id = account_master.id

    @api.onchange('id')
    def update_adv_account(self):
        self._set_advance_account()

    property_account_payable_advance_id = fields.Many2one(
        'account.account', "Account Advance Payable",
        domain=[
            ('internal_type', '=', 'other'),
            ('deprecated', '=', False),
        ],
        company_dependent=True,
        default=compute_get_adv_ap,
        track_visibility='onchange'
    )
    property_account_receivable_advance_id = fields.Many2one(
        'account.account', "Account Advance Receivable",
        domain=[
            ('internal_type', '=', 'other'),
            ('deprecated', '=', False),
        ], company_dependent=True,
        default=compute_get_adv_ar,
        track_visibility='onchange'
    )


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.onchange('attribute_line_ids')
    def _set_advance_account_variant(self):
        ir_property_obj = self.env['ir.property']
        account_master = self.env['account.account'].search([('company_id', '=', self.company_id.id),
                                                             ('name', '=', 'Expenses')])
        if not self.sudo().property_account_expense_id:
            if account_master:
                self.property_account_expense_id = account_master.id
            debug = True

    @api.onchange('id', 'name', 'default_code')
    def _set_advance_account(self):
        ir_property_obj = self.env['ir.property']
        account_master = self.sudo().env['account.account'].search([('company_id', '=', self.company_id.id),
                                                                    ('name', '=', 'Expenses')])
        if not self.sudo().property_account_expense_id.id:
            if account_master:
                self.property_account_expense_id = account_master.id
            debug = True

    @api.multi
    def _default_expense(self):
        account_master = self.sudo().env['account.account'].search([('company_id', '=', self.company_id.id),
                                                                    ('name', '=', 'Expenses')])
        if not self.sudo().property_account_expense_id.id:
            if account_master:
                self.property_account_expense_id = account_master.id
            debug = True

    # default_code = fields.Char(required=True)
    company_id = fields.Many2one(required=True)
    property_account_expense_id = fields.Many2one('account.account',
                                                  company_dependent=True,
                                                  string="Expense Account",
                                                  oldname="property_account_expense",
                                                  domain=[('deprecated', '=', False)],
                                                  help="The expense is accounted for when a vendor bill is validated, except in anglo-saxon accounting with perpetual inventory valuation in which case the expense (Cost of Goods Sold account) is recognized at the customer invoice validation. If the field is empty, it uses the one defined in the product category.",
                                                  track_visibility='onchange',
                                                  copy=True,
                                                  required=True,
                                                  default=_default_expense)


class Company(models.Model):
    _inherit = 'res.company'

    # street = fields.Char(required=True)
    # vat = fields.Char(required=True, string="NPWP")
    # city = fields.Char(required=True)
    # country_id = fields.Many2one(required=True)
    # phone = fields.Char(required=True)
    # parent_id = fields.Many2one(required=True)


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


class StockPickingBSP(models.Model):
    _inherit = 'stock.picking'
    date_done = fields.Datetime(string='Date of Receive', readonly=False, )
    receiving_dept = fields.Many2one('hr.department', string='Departement Penerima')
    receiving_employee = fields.Many2one('hr.employee', string='Karyawan Penerima')

    @api.multi
    def _add_filter_item_by_po(self, po_pointer_data):
        debug = True

    @api.onchange('receiving_dept')
    def _filter_empl_by_dept(self):
        domain_val = {}
        if self.receiving_dept:
            # get list of employee
            list_of_employee = []
            list_of_employee = self.sudo().env['hr.employee'].search([('department_id','=',self.receiving_dept.id)]).ids
            if list_of_employee:
                domain_val = {'domain': {'receiving_employee': [('id', 'in', list_of_employee)]}}
                return domain_val

    @api.onchange('origin')
    def _order_id_onchange(self):
        test = 0
        po_pointer = self.env['purchase.order'].search([('name', '=', self.origin)])
        debug = True
        if po_pointer.id:
            # self.move_lines = [(5,0,0)]
            self._add_filter_item_by_po(po_pointer)


class PurchaseRequisitionBSP(models.Model):
    _inherit = "purchase.requisition.line"

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id
            self.product_qty = 1.0
            # if not self.price_unit:
            po_pointer = self.sudo().env['purchase.order'].search([('order_line.product_id.id','=',self.product_id.id),
                                                                   ('state','in',['purchase','done','approved'])]).sorted(key='date_order', reverse=True)
            if po_pointer:
                # po_pointer.sorted(key='price_unit', reverse=True)[0]
                self.price_unit = po_pointer[0].order_line[0].price_unit
            debug = True
        if not self.account_analytic_id:
            self.account_analytic_id = self.requisition_id.account_analytic_id
        if not self.schedule_date:
            self.schedule_date = self.requisition_id.schedule_date

class StockPickingBSP(models.Model):
    _inherit = 'stock.picking'
    # scheduled_date = fields.Datetime(
    #         'Scheduled Date',
    #         compute='_compute_scheduled_date',
    #         inverse='_set_scheduled_date', store=True,
    #         index=True,
    #         track_visibility='onchange',
    #         states={'done': [('readonly', True)],
    #                 'cancel': [('readonly', True)],
    #                 'draft': [('readonly',False)]},
    #         help="Scheduled time for the first part of the shipment to be processed. Setting manually a value here would set it as expected date for all the stock moves.")

    def search(self, args, offset=0, limit=None, order=None, count=False):
        dept_filter = []
        if self.sudo().env.user.employee_ids:
            for employee_val in self.env.user.employee_ids:
                for dept_val in employee_val.department_id:
                    dept_filter.append(dept_val.id)
        if dept_filter:
            eligible_operation_types_ids = self.sudo().env['stock.picking.type'].search([('department_ids', 'in', dept_filter)]).ids
            if eligible_operation_types_ids:
                args.append(('picking_type_id', 'in', eligible_operation_types_ids))
                return super(StockPickingBSP, self).search(args, offset=0, limit=None, order=order, count=False)
            else:
                return super(StockPickingBSP, self).search(args, offset=0, limit=None, order=order, count=False)
        else:
            return super(StockPickingBSP, self).search(args, offset=0, limit=None, order=order, count=False)


class StockMoveBSP(models.Model):
    _inherit = 'stock.move'

    location_prod_avail_qty = fields.Float('Available Quantity',
                                           compute='_compute_avail_qty',
                                           # inverse='_set_product_qty',
                                           digits=0,
                                           store=False,
                                           compute_sudo=True,
                                           help='Available quantity in the source location')
    location_prod_avail_uom = fields.Many2one('product.uom', 'Unit of Measure')
    @api.onchange('product_id')
    def _onchange_eligible_product(self):
        if self.picking_id.origin:
            # get elibile product
            domain_val = {}
            po_pointer = self.sudo().env['purchase.order'].search([('name','=',self.picking_id.origin)])
            product_ids = []
            for line in po_pointer.order_line:
                product_ids.append(line.product_id.id)
            if po_pointer.ids:
                # return {'domain': {'product_uom': [('category_id', '=', product.uom_id.category_id.id)]}}
                domain_val = {'domain': {'product_id': [('id', 'in', product_ids)]}}
                return domain_val

    @api.multi
    def _compute_avail_qty(self):
        for line_item in self:
            if line_item.product_id:
                source_qty = 0
                # get source location
                source_uom = line_item.product_uom
                line_item.location_prod_avail_qty = source_qty
                line_item.location_prod_avail_uom = source_uom
            # debug = True
            # if po_pointer.
