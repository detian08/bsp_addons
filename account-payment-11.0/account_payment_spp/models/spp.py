import itertools
from _datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import Warning as UserError, ValidationError
import odoo.addons.decimal_precision as dp
from odoo.tools.float_utils import float_compare

_STATES = [
    ('draft', 'Draft'),
    ('to_approve', 'To be approved'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('open', 'Open'),
    ('paid', 'Paid'),
    ('cancel', 'Cancelled')
]

_PAYMENT_TYPE = [
    ('DP', 'Down Payment'),
    ('CBD', 'Cash Before Delivery'),
    ('BILL', 'Billing'),
    ('OTH', 'Other')
]


class SPP(models.Model):
    _name = "spp"
    _description = 'Surat Permohonan Pembayaran'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def _company_get(self):
        company_id = self.env['res.company']._company_default_get(self._name)
        return self.env['res.company'].browse(company_id.id)

    @api.model
    def _get_default_requested_by(self):
        return self.env['res.users'].browse(self.env.uid)

    def _compute_total(self):
        for record in self:
            record.total = sum(line.value for line in record.line_ids)

    @api.depends('spp_line_ids.amount_payment')
    @api.multi
    def _amount_all(self):
        amount_payment_total = 0.0
        for spp in self:
            amount_payment_total = sum(line.amount_payment for line in spp.spp_line_ids) or 0.0
            spp.amount_payment_total = amount_payment_total

    @api.depends('spp_line_ids.advance_payment_state')
    @api.one
    def _compute_state(self):
        if (self.state == 'approved' or self.state == 'open' or self.state == 'paid') and self.payment_type != 'BILL':
            line_state = self.spp_line_ids.mapped('advance_payment_state')
            if 'draft' in line_state:
                ostate = 'open'
            elif 'cancelled' in line_state and not ('draft' in line_state) and not ('posted' in line_state) and not (
                    'reconciled' in line_state):
                ostate = 'cancel'
            else:
                ostate = 'paid'
            self.comp_state = ostate
            self.env.cr.execute(
                'update spp set state=%s where id=%s',
                (self.comp_state, self.id))

    name = fields.Char(string="Number SPP", default='New', readonly=True, size=25)
    request_date = fields.Date(string="Request Date", default=datetime.now().date())
    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True,
                                 domain=[('type', 'in', ('bank', 'cash'))])
    partner_id = fields.Many2one("res.partner", string="Supplier/Vendor",
                                 required=True, domain=[('supplier', '=', True)])
    payment_type = fields.Selection(selection=_PAYMENT_TYPE,
                                    string='Payment Type',
                                    index=True,
                                    track_visibility='onchange',
                                    required=True,
                                    copy=False,
                                    default='DP')

    @api.onchange('payment_type')
    def _onchange_payment_type(self):
        test = 0

    spp_line_ids = fields.One2many("spp.line", "spp_id", "Payment of SPP")
    spp_line_bill_ids = fields.One2many("spp.line.bill", "spp_id", "Billing Items of SPP")
    memo = fields.Text("Memo")
    to_approve_allowed = fields.Boolean(
        compute='_compute_to_approve_allowed')
    requested_by = fields.Many2one('res.users',
                                   'Requested by',
                                   required=True,
                                   track_visibility='onchange',
                                   default=_get_default_requested_by)
    state = fields.Selection(selection=_STATES,
                             string='Status',
                             index=True,
                             track_visibility='onchange',
                             required=True,
                             copy=False,
                             default='draft')
    company_id = fields.Many2one('res.company', 'Company',
                                 required=True,
                                 default=_company_get,
                                 track_visibility='onchange')
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Currency')
    amount_payment_total = fields.Monetary(string="Total Payment Amount", compute='_amount_all',
                                           currency_field='currency_id', store=True)
    comp_state = fields.Char(string='compute state', compute='_compute_state', store=True)

    assigned_to = fields.Many2one(
        'res.users', 'Approver', track_visibility='onchange',
        domain=lambda self: ['|',
                             (
                                 'groups_id', 'in',
                                 self.env.ref('account_payment_spp.group_spp_manager').id),
                             (
                                 'groups_id', 'in',
                                 self.env.ref('account_payment_spp.group_spp_manager').id)]
    )

    # @api.onchange('comp_state')
    # def _onchange_comp_state(self):
    #     if self.comp_state:
    #         self.state = self.comp_state

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('SPP') or '/'
        result = super(SPP, self).create(vals)
        return result

    @api.multi
    def write(self, vals):
        result = super(SPP, self).write(vals)
        return result

    @api.multi
    def button_draft(self):
        return self.write({'state': 'draft'})

    @api.multi
    def button_mass_create_invoice(self):
        mass_retval = []
        if self.payment_type == 'BILL':
            for spp_line_bill in self.spp_line_bill_ids:
                spp_line_bill._amount_billing()
                if spp_line_bill.amount_invoice_paid < spp_line_bill.po_amount_total:
                    mass_retval.append(self._create_account_invoice_v2(spp_line_bill))
        else:
            raise ValidationError(
                _('Mass Create Invoice can be accessed only for Billing payment type'))
        retval_len = len(mass_retval)


    @api.multi
    def button_mass_payment_bill(self):
        test = 0
        payment_register_obj_pointer = self.env['account.register.payments']
        invoice_obj_pointer = self.env['account.invoice']
        payment_obj_pointer = self.env['account.payment']

        payment_list = payment_obj_pointer
        payment_dict = dict(spp_id=self.name)
        payment_dict.update(create=False, delete=False, menu=False)
        for spp_line_bill in self.spp_line_bill_ids:
            bill_ids = invoice_obj_pointer.search([('id', 'in', spp_line_bill.billing_ids.ids),
                                                   ('state', '=', 'open')])
            invoices = invoice_obj_pointer.browse([('id', 'in', bill_ids)])
            if bill_ids:
                amount_billed = payment_register_obj_pointer.sudo()._compute_payment_amount(bill_ids)
                payment_type = ('inbound' if amount_billed > 0 else 'outbound')
                payment_method_id = self.env['account.payment.method'].search([('code', '=', 'manual'),
                                                                               ('payment_type', '=', payment_type)])
                payment_vals = {
                    'journal_id': self.journal_id.id,
                    'payment_method_id': payment_method_id.id,
                    'payment_date': datetime.today(),
                    #     'communication': self.communication, # DO NOT FORWARD PORT TO V12 OR ABOVE
                    # 'invoice_ids': [(6, 0, spp_line_bill.billing_ids.ids)],
                    'invoice_ids': [(6, 0, bill_ids.ids)],
                    'payment_type': payment_type,
                    'amount': abs(amount_billed),
                    'currency_id': self.currency_id.id,
                    'partner_id': bill_ids[0].commercial_partner_id.id,
                    'partner_type': 'supplier',
                }
                payment_list += payment_obj_pointer.create(payment_vals)
            else:
                test = 0

        if payment_list:
            for payment_item in payment_list:
                payment_item_post_result = payment_item.post()
            payment_dict = dict(spp_id=self.name)
            payment_dict.update(create=False, delete=False, menu=False)
            return {
                'name': _('Payments'),
                'domain': [('state', '=', 'posted'), ('id', 'in', payment_list.ids)],
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.payment',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'context': payment_dict
            }
        else:
            raise ValidationError(
                _('Payment processing error'))

    @api.multi
    def button_payment_bill(self):
        test = 0
        #     get related billing data
        billing_ids = []
        for spp_line in self.spp_line_bill_ids:
            for bill in spp_line.billing_ids:
                if bill.state == 'open':
                    billing_ids.append(bill.id)
        if billing_ids:
            view_id = self.env['ir.model.data'].get_object_reference('account', 'invoice_supplier_tree')[1]
            billing_dict = dict(spp_id=self.name)
            billing_dict.update(create=False, delete=False, menu=False)
            return {
                'name': _('SPP Vendor Bills Payment'),
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'account.invoice',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'target': 'current',
                'domain': "[('state', '=', 'open'),('id', 'in', %s)]" % (billing_ids),
                'context': billing_dict
            }
        else:
            raise ValidationError(
                _('There is no Invoice that can be processed'))

    @api.multi
    def button_to_approve(self):
        self.to_approve_allowed_check()
        self._check_duplicate_po_reference()
        return self.write({'state': 'to_approve'})

    @api.multi
    def button_approved(self):
        return self.write({'state': 'approved'})

    @api.multi
    def button_rejected(self):

        return self.write({'state': 'rejected'})

    @api.multi
    def _prepare_advance_payment(self,
                                 partner_id,
                                 purchaseorder_id,
                                 bank_journal_id,
                                 payment_method_id,
                                 amount,
                                 spp_id):
        return {
            'is_advance_payment': True,
            'partner_id': partner_id,
            'purchase_id': purchaseorder_id,
            'spp_id': spp_id,
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'journal_id': bank_journal_id,
            'payment_method_id': payment_method_id,
            'amount': amount,
        }

    @api.multi
    def _prepare_account_invoice(self, partner_id, purchaseorder_id, date_invoice):
        return {
            'type': 'in_invoice',
            'partner_id': partner_id,
            'purchase_id': purchaseorder_id.id,
            'date_invoice': date_invoice,
        }

    @api.multi
    def _create_advance_payment(self, spp_line):
        # self,
        # partner_id,
        # purchaseorder_id,
        # bank_journal_id,
        # payment_method_id,
        # amount,
        # spp_id):
        vals = self._prepare_advance_payment(self.partner_id.id,
                                             spp_line.purchaseorder_id.id,
                                             self.journal_id.id,
                                             self.journal_id.outbound_payment_method_ids[0].id,
                                             spp_line.amount_payment,
                                             spp_line.spp_id.id
                                             )
        advance_payment = self.env['account.payment'].create(vals)

        # TODO: jika down payment dianggap langsung sudah di confirm, maka call post()
        #       jika tidak maka tidak perlu di panggil post(), lakukan 'confirm' di menu payment
        # advance_payment.post()

    @api.multi
    def _create_account_invoice(self, spp_line):
        vals = self._prepare_account_invoice(self.partner_id.id,
                                             spp_line.purchaseorder_id,
                                             self.request_date
                                             )
        account_invoice = self.env['account.invoice'].create(vals)
        account_invoice._onchange_partner_id()
        account_invoice.purchase_order_change()
        account_invoice._onchange_origin()
        account_invoice.action_invoice_open()
        return account_invoice

    @api.multi
    def _create_account_invoice_v2(self, spp_line_bill):
        invoice_pointer: object = self.env['account.invoice']
        invoice = invoice_pointer.sudo().create(
            {
                'partner_id': spp_line_bill.purchaseorder_id.partner_id.id,
                'purchase_id': spp_line_bill.purchaseorder_id.id,
                'account_id': spp_line_bill.purchaseorder_id.partner_id.property_account_payable_id.id,
                'date_invoice': self.request_date,
                'type': 'in_invoice'
            }
        )

        change_exec_result = invoice.purchase_order_change()
        compute_tax_result = invoice.compute_taxes()
        compute_exec_result = invoice._compute_amount()
        open_invoice_result = invoice.action_invoice_open()
        return invoice

        # invoice_output = account_invoice_pointer.create({
        #     'partner_id' = spp_line_bill.purchaseorder_id.partner_id.id,
        #     'purchase_id' = spp_line_bill.purchaseorder_id.id,
        #     'account_id'  =
        # })
        # account_invoice_line_pointer = self.env['account.invoice.line']
        # inv_lines_all = []
        # invoice_lines = self.env['account.invoice.line']
        # for po_line in spp_line_bill.purchaseorder_id.order_line:
        #     # po_line_inv_lines = self._prepare_invoice_line_from_po_line_spp(
        #     #     account_invoice_pointer,
        #     #     account_invoice_line_pointer,
        #     #     spp_line_bill)
        #
        #     invoice_line_data = account_invoice_pointer._prepare_invoice_line_from_po_line(po_line)
        #     po_line_inv_lines = account_invoice_line_pointer.create(invoice_line_data)
        #     for line in po_line_inv_lines:
        #         invoice_lines += line
        # if invoice_lines:
        #     po_invoice = account_invoice_pointer.sudo().create({
        #         'partner_id': spp_line_bill.purchaseorder_id.partner_id.id,
        #         'purchase_id': spp_line_bill.purchaseorder_id.id,
        #         'account_id': spp_line_bill.purchaseorder_id.partner_id.property_account_payable_id.id,
        #         'date_invoice': self.request_date,
        #         'invoice_line_ids': invoice_lines,
        #         'type': 'in_invoice'
        #     })
        #     if po_invoice:
        #         validate_result = po_invoice.purchase_order_change()
        #         return validate_result

    @api.multi
    def _prepare_invoice_line_from_po_line_spp(self,
                                               account_invoice_header_pointer,
                                               account_invoice_line_pointer,
                                               spp_line_bill):
        inv_lines = []
        qty = spp_line_bill.purchaseorder_id.qty_to_invoice
        if float_compare(qty, 0.0,
                         precision_rounding=spp_line_bill.purchaseorder_id.product_id.uom_id.rounding) <= 0:
            qty = 0.0
        for po_line in spp_line_bill.purchaseorder_id.order_line:
            taxes = po_line.taxes_id
            invoice_line_tax_ids = po_line.order_id.fiscal_position_id.map_tax(taxes)
            invoice_line = self.env['account.invoice.line']
            data = {
                'purchase_line_id': po_line.id,  # ID Line Item PO
                'name': po_line.name + ': ' + po_line.order_id.name,
                'origin': spp_line_bill.purchaseorder_id.name,
                'uom_id': po_line.product_id.uom_id.id,
                'product_id': po_line.product_id.id,
                'account_id': account_invoice_line_pointer.with_context(
                    {'journal_id': account_invoice_header_pointer.journal_id.id,
                     'type': 'in_invoice'})._default_account(),
                'price_unit': po_line.order_id.currency_id.with_context(
                    date=account_invoice_header_pointer.date_invoice).compute(po_line.price_unit,
                                                                              account_invoice_header_pointer.currency_id,
                                                                              round=False),
                'quantity': po_line.qty_to_invoice,
                'discount': 0.0,
                'account_analytic_id': po_line.account_analytic_id.id,
                'analytic_tag_ids': po_line.analytic_tag_ids.ids,
                'invoice_line_tax_ids': invoice_line_tax_ids.ids
            }
            account = invoice_line.get_invoice_line_account('in_invoice',
                                                            po_line.product_id,
                                                            po_line.order_id.fiscal_position_id,
                                                            self.env.user.company_id)
            if account:
                data['account_id'] = account.id
                inv_line = account_invoice_line_pointer.create(data)
                if inv_line:
                    inv_lines += inv_line
        return inv_lines

    def _prepare_account_invoice_line_spp(self, po_data_line):
        account_invoice_line_obj = self.env['account.invoice.line']
        inv_line_data = account_invoice_line_obj._prepare_invoice_line_from_po_line(po_data_line)
        return inv_line_data

    @api.multi
    def button_paid(self):
        if self.payment_type != 'BILL':
            for line in self.spp_line_ids:
                if (line.purchaseorder_id.amount_total - line.amount_payment) < 0.00:
                    raise ValidationError(
                        _('Verification Failed! Payment Amount'
                          ' not must be bigger than'
                          ' Amount Total.'))

            for line2 in self.spp_line_ids:
                # Get Advance Payment sesuai dengan nomor SPP ( Surat Permintaan Pembayaran )
                # yang statusnya tidak sama dengan cancelled
                adv_payment_for_po = line2.purchaseorder_id.advance_payment_ids.filtered(
                    lambda x: x.spp_id.id == line2.spp_id.id and x.state != 'cancelled')
                # jika Adv Payment belum pernah di buat, maka create Adv Payment yang baru
                if len(adv_payment_for_po) == 0:
                    self._create_advance_payment(line2)
                    # self._update_line_adv_payment_ref()
            return self.write({'state': 'open'})
        else:
            raise ValidationError(
                _('Verification Failed! Create Advance Payment cannot be accessed from Billing Payment Type'))

        # @api.multi
        # def button_invoice(self):
        #     test = 0
        #     for line in self.spp_line_bill_ids:
        #         if (line.purchaseorder_id.amount_total - line.amount_payment) < 0.00:
        #             raise ValidationError(
        #                 _('Verification Failed! Payment Amount'
        #                   ' not must be bigest from Amount Total.'))
        #
        #     for line2 in self.spp_line_ids:
        #         invoice = self._create_account_invoice_v2(line2)
        #         if invoice:
        #             line2.write({'invoice_id': invoice.id})
        #
        #     return self.write({'state': 'open'})

    @api.multi
    def button_cancel(self):
        # TODO: Tambahkan pengecekan state Advance Payment apakah sudah ada yang 'posted'
        #    jika sudah ada yang posted, maka SPP tidak bisa dicancel
        if self.filtered(lambda spp: SPP.state not in ['draft', 'approved']):
            raise UserError(
                _("Surat Permintaan Pembayaran must be in draft or approved state in order to be cancelled."))
        if self.payment_type == 'BILL':
            bill_invalid = self.spp_line_bill_ids.billing_ids.search('state', '=', 'paid')
            if bill_invalid:
                raise UserError(
                    _("There are several Vendor Bill(s) which state is already paid"))
            else:
                cancel_bill_result_list = []
                for bill in self.spp_line_bill_ids.billing_ids:
                    cancel_bill_retval = bill.action_invoice_cancel()
                    cancel_result_data = {
                        'bill_id': bill.id,
                        'bill_name': bill.name,
                        'retval': cancel_bill_retval
                    }
                    cancel_bill_result_list.append(cancel_result_data)
                return self.action_cancel()
        else:
            adv_invalid = self.spp_line_ids.advance_payment_ids.search('state', 'in', ['posted', 'reconciled'])
            if adv_invalid:

                raise UserError(
                    _("There are several Advance Payment(s) which state is already posted or reconciled"))
            else:
                cancel_adv_result_list = []
                for adv in self.spp_line_ids.advance_payment_ids:
                    cancel_adv_result = adv.cancel()
                    cancel_result_data = {
                        'advance_id': adv.id,
                        'advance_name': adv.name,
                        'retval': cancel_adv_result
                    }
                    cancel_adv_result_list.append(cancel_result_data)
                return self.action_cancel()

    @api.multi
    def action_cancel(self):
        # TODO: lengkapi dengan proses pembatalan pembayaran, jika SPP sdh dalam status dibayar ( tanya
        #  usernya ?)

        self.write({'state': 'cancel'})
        return True

    @api.multi
    def _check_duplicate_po_reference(self):
        for line in self.spp_line_ids:
            if self.spp_line_ids.search([('spp_id', '=', line.spp_id.id),
                                         ('purchaseorder_id', '=', line.purchaseorder_id.id),
                                         ('id', '!=', line.id)]):
                raise UserError(_(
                    "Duplicated Purchase Order detected. You probably encoded twice the same Surat Permintaan Pembayaran."))

    @api.multi
    def to_approve_allowed_check(self):
        for rec in self:
            if not rec.to_approve_allowed:
                raise UserError(
                    _("You can't request an approval for a Surat Permintaan Pembayaran "
                      "which is empty or zero amount payment. (%s)") % rec.name)

    @api.multi
    @api.depends('state', 'spp_line_ids.amount_payment', )
    def _compute_to_approve_allowed(self):
        for rec in self:
            rec.to_approve_allowed = (
                    rec.state == 'draft' and
                    any([not line.amount_payment == 0 for line in rec.spp_line_ids])
            )

    def _update_state(self, id, new_state):
        rec = self.env['spp'].browse(id)
        if rec.state == 'approved' or rec.state == 'open' or rec.state == 'paid':
            rec.state = new_state


class SPPLine(models.Model):
    _name = "spp.line"
    _description = "Surat Permintaan Pembayaran Lines"

    @api.depends('advance_payment_ids.state')
    def _update_adv_payment_ref(self):
        obj_adv_pymnt = self.advance_payment_ids
        if len(obj_adv_pymnt) > 0:
            line_state = []
            a = []
            for line in obj_adv_pymnt:
                if line.name:
                    ref = ''.join([line.name, '-', line.state])
                else:
                    ref = ''.join(['New', '-', line.state])
                line_state.append(line.state)
                a.append(ref)
            ref = ', '.join(a)
            if ref != '':
                self.advance_payment_reference = ref

        # @api.depends('amount_payment')
        # @api.one
        # def _copy_amount(self):
        #     self.amount_old_payment = self.amount_payment

    @api.depends('advance_payment_ids.state')
    def _update_adv_payment_state(self):
        obj_adv_pymnt = self.advance_payment_ids
        if len(obj_adv_pymnt) > 0:
            line_state = []
            for line in obj_adv_pymnt:
                line_state.append(line.state)
            if len(line_state) > 0:
                if 'draft' in line_state:
                    self.advance_payment_state = 'draft'
                elif 'cancelled' in line_state and not 'draft' in line_state \
                        and not 'posted' in line_state and not 'sent' in line_state and not 'reconciled' in line_state:
                    self.advance_payment_state = 'cancelled'
                elif 'posted' in line_state or 'reconciled' in line_state:
                    self.advance_payment_state = 'posted'

    spp_id = fields.Many2one("spp", string="Surat Permintaan Pembayaran", required=True, ondelete='cascade')
    payment_type = fields.Selection(selection=_PAYMENT_TYPE, related='spp_id.payment_type', invisible=True)
    purchaseorder_id = fields.Many2one("purchase.order", string="Purchase Order")
    date_order = fields.Datetime(related="purchaseorder_id.date_order", string="Order Date", readonly=True,
                                 store=True)
    currency_id = fields.Many2one("res.currency", related="purchaseorder_id.currency_id", string="Currency",
                                  readonly=True,
                                  store=True)
    amount_untaxed = fields.Monetary(related="purchaseorder_id.amount_untaxed", string="Untaxed Amount",
                                     readonly=True,
                                     store=True)
    amount_tax = fields.Monetary(related="purchaseorder_id.amount_tax", string="Tax", readonly=True, store=True)
    amount_total = fields.Monetary(related="purchaseorder_id.amount_total", string="Total", readonly=True,
                                   store=True)
    partner_id = fields.Many2one(related="spp_id.partner_id", string="Partner", readonly=True)
    state = fields.Selection(related="purchaseorder_id.state", string="Status", readonly=True, store=True)

    amount_payment = fields.Monetary(string="Payment Amount")
    comments = fields.Text(string="Comments")
    advance_payment_ids = fields.One2many(related="purchaseorder_id.advance_payment_ids", string="Advance payments",
                                          readonly=True)
    advance_payment_reference = fields.Char(string="Advance Payment Ref",
                                            compute="_update_adv_payment_ref",
                                            readonly=True, store=True)
    advance_payment_state = fields.Char(string="Advance Payment state",
                                        compute="_update_adv_payment_state",
                                        readonly=True, store=True)
    amount_total_advance_payment = fields.Monetary(string="Advance Payment Amount",
                                                   compute='_amount_advance_payment',
                                                   currency_field='currency_id', store=True)

    # payment_type = fields.Selection(selection=_PAYMENT_TYPE,
    #                                 string='Payment Type',
    #                                 index=True,
    #                                 track_visibility='onchange',
    #                                 required=True,
    #                                 copy=False,
    #                                 default='DP')

    def total_amount_by_item(self, ori):
        # self.write({'amount_payment': 0})
        apList = self.env['spp.line'].search([('purchaseorder_id', '=', self.purchaseorder_id.id)])
        total = sum(ap.amount_payment for ap in apList) or 0.0
        if ori and not self._origin.id:
            total += self.amount_payment
        return total

    def _amount_advance_payment(self):
        advance__payment_total = 0.0
        for rec in self:
            advance__payment_total = sum(ap.amount for ap in rec.purchaseorder_id.advance_payment_ids) or 0.0
            rec.amount_total_advance_payment = advance__payment_total

    def _check_amount_payment(self, ori):
        return (self.amount_total - self.total_amount_by_item(ori)) >= 0

    @api.onchange('amount_payment')
    def onchange_amount_payment(self):
        if self._check_amount_payment(True):
            return {}
        return {
            'warning': {
                'title': 'Error',
                'message': 'You have entered wrong value for amount'
            }
        }

    @api.constrains('amount_payment')
    def validation_amount_payment(self):
        validation_result = self._check_amount_payment(False)
        if validation_result != True:
            raise ValidationError('You have entered wrong value for amount')

    # @api.multi
    # def unlink(self):
    #     if self.filtered(lambda x: x.state in ('post', 'done')):
    #         raise UserError(
    #             _('You can not remove a sale order line.\nDiscard changes and try setting the quantity to 0.'))
    #     return super(SPPLine, self).unlink()

    @api.onchange('purchaseorder_id')
    def _onchange_allowed_purchaseorder_ids(self):
        result = {}

        # TODO: tambahkan untuk pengajuan SPP berikutnya tidak boleh dilakukan jika Invoice/Bill atas PO
        #       tersebut sudah ada dan belum dilunasi
        domain = self.get_domain_open_bill()
        po_data_search = self.env['purchase.order'].search(domain)
        # po_data_final = []
        invalid_po_id = []
        for po_id in po_data_search.ids:
            po_data = self.env['purchase.order'].browse(po_id)
            if self.spp_id.payment_type == 'BILL':
                if po_data.invoice_ids:  # jika sudah ada billing
                    inv_filter = po_data.invoice_ids.filtered(lambda inv: inv.state == 'open')  # cari yg masih open
                    if inv_filter:  # jika masih ada yg open
                        invalid_po_id.append(po_data.id)  # masukkan ke dalam list po yang tidak valid

        if invalid_po_id:
            po_data_final = po_data_search.filtered(lambda x: x.ids != invalid_po_id)
        else:
            po_data_final = po_data_search

        result['domain'] = {'purchaseorder_id': [('id', 'in', po_data_final.ids)]}

        # result['domain'] = {'purchaseorder_id': domain}
        return result

    @api.multi
    def get_domain_open_bill(self):
        # already assigned PO as item
        po_ids = self.spp_id.spp_line_ids.mapped('purchaseorder_id')

        # PO yang sudah di confirm
        domain = [('state', 'in', ['purchase'])]

        domain += [('invoice_status', 'in', [('to invoice'), ('no')])]
        if self.spp_id.payment_type == 'BILL':
            # tagihan baru boleh dibuat jika

            # sudah ada shipment
            domain += [('picking_count', '>', 0)]
            # belum ada billing atau billing sebelumnya sudah paid atau cancel

        if self.spp_id.partner_id:
            domain += ['|', ('partner_id', 'child_of', self.spp_id.partner_id.id),
                       ('partner_id', '=', self.spp_id.partner_id.id)
                       ]

        # A Purchase Order can be added only if Purchase Order is not already in the SPP
        if po_ids:
            domain += [('id', 'not in', po_ids.ids)]

        return domain


class SPPLineBill(models.Model):
    _name = "spp.line.bill"
    _description = "Surat Permintaan Pembayaran Lines - PO-Billing"

    @api.multi
    @api.depends('billing_ids')
    @api.onchange('billing_ids')
    def _update_billing_ref(self):
        billing_obj = self.billing_ids
        if len(billing_obj) > 0:
            for bill_line in billing_obj:
                if bill_line.name:
                    ref = ''.join([bill_line.name, '-', bill_line.state])
                else:
                    ref = ''.join(['New', '-', bill_line.state])
            ref = ', '.join([])
            if ref != '':
                self.advance_payment_reference = ref

    # @api.depends('billing_ids.state')
    # def _update_billing_state(self):
    #     test = 0

    @api.multi
    @api.depends('billing_ids')
    @api.onchange('billing_ids','comments')
    def _amount_billing(self):
        self.amount_total_billing = self.amount_invoice_paid = self.amount_invoice_draft = self.amount_invoice_open = 0
        if self.billing_ids:
            for bill_id in self.billing_ids:
                billing_obj = self.env['account.invoice'].search([('id', '=', bill_id.id)])
                for bill_line in billing_obj:
                    if bill_line.state == 'draft':
                        self.amount_invoice_draft += bill_line.amount_total
                    elif bill_line.state == 'open':
                        self.amount_invoice_open += bill_line.amount_total
                    elif bill_line.state == 'paid':
                        self.amount_invoice_paid = self.amount_invoice_paid + bill_line.amount_total - bill_line.residual
            self.amount_total_billing = self.amount_invoice_draft + self.amount_invoice_open + self.amount_invoice_paid

    spp_id = fields.Many2one("spp", string="Surat Permintaan Pembayaran", required=True, ondelete='cascade')
    payment_type = fields.Selection(selection=_PAYMENT_TYPE, related='spp_id.payment_type', invisible=True)
    # PO data
    purchaseorder_id = fields.Many2one("purchase.order", string="Purchase Order")
    date_order = fields.Datetime(related="purchaseorder_id.date_order", string="Order Date", readonly=True,
                                 store=True)
    currency_id = fields.Many2one("res.currency", related="purchaseorder_id.currency_id", string="Currency",
                                  readonly=True,
                                  store=True)
    po_amount_untaxed = fields.Monetary(related="purchaseorder_id.amount_untaxed", string="Untaxed Amount",
                                        readonly=True,
                                        store=True)
    po_amount_tax = fields.Monetary(related="purchaseorder_id.amount_tax", string="Tax", readonly=True, store=True)
    po_amount_total = fields.Monetary(related="purchaseorder_id.amount_total", string="Total", readonly=True,
                                      store=True)
    partner_id = fields.Many2one(related="spp_id.partner_id", string="Partner", readonly=True)
    state = fields.Selection(related="purchaseorder_id.state", string="Status", readonly=True, store=True)
    # billing data
    amount_invoice = fields.Monetary(string="Current Invoice Amount")
    amount_invoice_draft = fields.Monetary(string="Invoice Amount - Draft", compute="_amount_billing")
    amount_invoice_open = fields.Monetary(string="Invoice Amount - Open", compute="_amount_billing")
    amount_invoice_paid = fields.Monetary(string="Invoice Amount - Paid", compute="_amount_billing")
    comments = fields.Text(string="Comments", track_visibility = "onchange")

    billing_ids = fields.Many2many(related="purchaseorder_id.invoice_ids",
                                   string="Invoice",
                                   track_visibility="onchange",
                                   readonly=True)
    billing_reference = fields.Char(string="List of Billing",
                                    compute="_update_billing_ref",
                                    readonly=True, store=True)
    billing_state = fields.Char(string="Billing State",
                                compute="_update_billing_state",
                                readonly=True, store=True)
    amount_total_billing = fields.Monetary(string="All Invoice Amount",
                                           compute='_amount_billing')

    @api.multi
    def action_view_invoice(self):
        # po_obj = self.env['purchase.order']
        action = self.purchaseorder_id.env.ref('account.action_invoice_tree2')
        result = action.read()[0]
        result['context'] = {'type': 'in_invoice', 'default_purchase_id': self.purchaseorder_id.id}
        if not self.purchaseorder_id.invoice_ids:
            # Choose a default account journal in the same currency in case a new invoice is created
            journal_domain = [
                ('type', '=', 'purchase'),
                ('company_id', '=', self.purchaseorder_id.company_id.id),
                ('currency_id', '=', self.purchaseorder_id.currency_id.id),
            ]
            default_journal_id = self.purchaseorder_id.env['account.journal'].search(journal_domain, limit=1)
            if default_journal_id:
                result['context']['default_journal_id'] = default_journal_id.id
        else:
            # Use the same account journal than a previous invoice
            result['context']['default_journal_id'] = self.purchaseorder_id.invoice_ids[0].journal_id.id
            # # choose the view_mode accordingly
        if len(self.purchaseorder_id.invoice_ids) != 1:
            result['domain'] = "[('id', 'in', " + str(self.purchaseorder_id.invoice_ids.ids) + ")]"
        elif len(self.purchaseorder_id.invoice_ids) == 1:
            res = self.purchaseorder_id.env.ref('account.invoice_supplier_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = self.purchaseorder_id.invoice_ids.id
            if not self.purchaseorder_id.invoice_ids.id:
                result['res_id'] = 0
        result['context']['default_origin'] = self.purchaseorder_id.name
        result['context']['default_reference'] = self.purchaseorder_id.partner_ref
        return result

    @api.onchange('purchaseorder_id')
    def _onchange_allowed_purchaseorder_ids(self):
        result = {}

        # TODO: tambahkan untuk pengajuan SPP berikutnya tidak boleh dilakukan jika Invoice/Bill atas PO
        #       tersebut sudah ada dan belum dilunasi
        domain = self.get_domain_open_bill()
        po_data_search = self.env['purchase.order'].search(domain)
        # po_data_final = []
        invalid_po_id = []
        for po_id in po_data_search.ids:
            po_data = self.env['purchase.order'].browse(po_id)
            if self.spp_id.payment_type == 'BILL':
                if po_data.invoice_ids:  # jika sudah ada billing
                    inv_filter = po_data.invoice_ids.filtered(lambda inv: inv.state == 'open')  # cari yg masih open
                    if inv_filter:  # jika masih ada yg open
                        invalid_po_id.append(po_data.id)  # masukkan ke dalam list po yang tidak valid

        if invalid_po_id:
            po_data_final = po_data_search.filtered(lambda x: x.ids != invalid_po_id)
        else:
            po_data_final = po_data_search

        result['domain'] = {'purchaseorder_id': [('id', 'in', po_data_final.ids)]}

        # result['domain'] = {'purchaseorder_id': domain}
        return result

    @api.multi
    def get_domain_open_bill(self):
        # already assigned PO as item
        # po_ids = self.spp_id.spp_line_ids.mapped('purchaseorder_id')
        po_ids = self.spp_id.spp_line_bill_ids.mapped('purchaseorder_id')

        # PO yang sudah di confirm
        domain = [('state', 'in', ['purchase'])]

        domain += [('invoice_status', 'in', [('to invoice'), ('no')])]
        if self.spp_id.payment_type == 'BILL':
            # tagihan baru boleh dibuat jika

            # sudah ada shipment
            domain += [('picking_count', '>', 0)]
            # belum ada billing atau billing sebelumnya sudah paid atau cancel

        if self.spp_id.partner_id:
            domain += ['|', ('partner_id', 'child_of', self.spp_id.partner_id.id),
                       ('partner_id', '=', self.spp_id.partner_id.id)
                       ]

        # A Purchase Order can be added only if Purchase Order is not already in the SPP
        if po_ids:
            domain += [('id', 'not in', po_ids.ids)]

        return domain
