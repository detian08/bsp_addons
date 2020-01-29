import json
from _datetime import datetime, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import Warning as UserError
import odoo.addons.decimal_precision as dp

_STATES = [
    ('draft', 'Draft'),
    ('to_approve', 'To be approved'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('open', 'Open'),
    ('paid', 'Paid'),
    ('cancel', 'Cancelled')
]


class KontraBon(models.Model):
    _name = "kontra.bon"
    _description = 'Kontra Bon'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def _company_get(self):
        company_id = self.env['res.company']._company_default_get(self._name)
        return self.env['res.company'].browse(company_id.id)

    @api.model
    def _get_default_requested_by(self):
        return self.env['res.users'].browse(self.env.uid)

    @api.depends('invoice_line_ids.amount_payment')
    @api.multi
    def _amount_all(self):
        for kontrabon in self:
            amount_payment_total = residual_total = amount_tax_total = 0.0
            for line in kontrabon.invoice_line_ids:
                residual_total += line.residual
                amount_tax_total += line.amount_tax
                amount_payment_total += line.amount_payment
            kontrabon.update({
                'residual_total': residual_total,
                'amount_tax_total': amount_tax_total,
                'amount_payment_total': amount_payment_total
            })

    # update state
    @api.depends('invoice_line_ids.state')
    @api.multi
    def _compute_state(self):
        for kontrabon in self:
            if kontrabon.state == 'approved' or kontrabon.state == 'open' or kontrabon.state == 'paid':
                if not any(line.invoice_id.state == 'open' for line in kontrabon.invoice_line_ids):
                    kontrabon.write({'state': 'paid'})
                else:
                    kontrabon.write({'state': 'open'})

    name = fields.Char(string="Number KB", default='New', readonly=True, size=25)
    date_doc = fields.Date(string="Date KB", default=datetime.now().date())
    partner_id = fields.Many2one("res.partner", string="Supplier/Vendor",
                                 required=True, domain=[('supplier', '=', True)])
    date_receipt = fields.Date(String="Date of Receipt")
    invoice_line_ids = fields.One2many("kontra.bon.line", "kontrabon_id", "Bill of Kontra Bon")

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
    amount_tax_total = fields.Monetary(string="Total Tax", compute='_amount_all',
                                       currency_field='currency_id', store=True)
    residual_total = fields.Monetary(string="Total Amount Due", compute='_amount_all',
                                     currency_field='currency_id', store=True)
    amount_payment_total = fields.Monetary(string="Total Payment Amount", compute='_amount_all',
                                           currency_field='currency_id', store=True)
    comp_state = fields.Boolean(string='compute state', compute='_compute_state', store=True)

    assigned_to = fields.Many2one(
        'res.users', 'Approver', track_visibility='onchange',
        domain=lambda self: ['|',
                             (
                                 'groups_id', 'in',
                                 self.env.ref('account_payment_kontra_bon.group_kontra_bon_manager').id),
                             (
                                 'groups_id', 'in',
                                 self.env.ref('account_payment_kontra_bon.group_kontra_bon_manager').id)]
    )

    chk_kwitansi = fields.Selection([('asli', 'Asli'), ('copy', 'Copy'), ('none', 'Tdk Ada')], default='none')
    chk_faktur = fields.Selection([('asli', 'Asli'), ('copy', 'Copy'), ('none', 'Tdk Ada')], default='none')
    chk_bppb = fields.Selection([('asli', 'Asli'), ('copy', 'Copy'), ('none', 'Tdk Ada')], default='none')
    chk_qcf = fields.Selection([('asli', 'Asli'), ('copy', 'Copy'), ('none', 'Tdk Ada')], default='none')
    chk_po = fields.Selection([('asli', 'Asli'), ('copy', 'Copy'), ('none', 'Tdk Ada')], default='none')
    chk_bpb = fields.Selection([('asli', 'Asli'), ('copy', 'Copy'), ('none', 'Tdk Ada')], default='none')
    chk_bstb = fields.Selection([('asli', 'Asli'), ('copy', 'Copy'), ('none', 'Tdk Ada')], default='none')
    chk_sj = fields.Selection([('asli', 'Asli'), ('copy', 'Copy'), ('none', 'Tdk Ada')], default='none')
    chk_fpajak = fields.Selection([('asli', 'Asli'), ('copy', 'Copy'), ('none', 'Tdk Ada')], default='none')

    payment_ids = fields.One2many("account.payment", "kontrabon_id",  compute='_compute_payment', string="Payment Invoice")
    payment_count = fields.Integer(compute='_compute_payment', string='Transfer',
                                   default=0, store=True,
                                   compute_sudo=True)
    # payment_ids = fields.Many2many('account.payment', compute='_compute_payment', string='Payments',
    #                                copy=False,
    #                                store=True, compute_sudo=True)

    @api.depends('invoice_line_ids.amount_payment')
    @api.multi
    def _update_link_account_invoice(self, id):
        objKB = self.env['kontra.bon'].browse(id)
        for line in objKB.invoice_line_ids:
            _id = line.invoice_id.id
            # Get semua id dari kontra.bon.line yang menggunakan invoice_id = _id
            line_ids = self.env['kontra.bon.line'].search([('invoice_id', '=', _id)]).ids
            objAccInv = self.env['account.invoice'].search([('id', '=', _id)])
            # update many2many
            rec = objAccInv.write({
                'kontrabon_reference': self._prepare_kontrabon_reference(line_ids),
                'kontrabon_line_ids': [(6, 0, line_ids)]
            })
        return True

    @api.multi
    def _prepare_kontrabon_reference(self, line_ids):
        objLines = self.env['kontra.bon.line'].search([('id', 'in', line_ids)])
        kontrabon_ids = objLines.mapped('kontrabon_id')
        vals = ', '.join(kontrabon_ids.mapped('name'))
        return vals

    @api.onchange('kontrabon_line_ids')
    def _onchange_kontrabon_reference(self):
        kontrabon_ids = self.kontrabon_line_ids.mapped('kontra_bon_line_id')
        if kontrabon_ids:
            self.kontrabon_reference = ', '.join(kontrabon_ids.mapped('name'))

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id.property_supplier_payment_term_id:
            delta =self.partner_id.property_supplier_payment_term_id.line_ids[0].days
            self.date_receipt = datetime.strptime(self.date_doc, "%Y-%m-%d") + timedelta(delta)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('kontra.bon') or '/'
        result = super(KontraBon, self).create(vals)
        self._update_link_account_invoice(result.ids[0])
        return result

    @api.multi
    def write(self, vals):
        result = super(KontraBon, self).write(vals)
        self._update_link_account_invoice(self.id)
        return result

    @api.multi
    def button_draft(self):
        return self.write({'state': 'draft'})

    @api.multi
    def button_to_approve(self):
        self.to_approve_allowed_check()
        self._check_duplicate_supplier_reference()
        return self.write({'state': 'to_approve'})

    @api.multi
    def button_approved(self):
        return self.write({'state': 'approved'})

    @api.multi
    def button_rejected(self):
        if self.filtered(lambda kontrabon: kontrabon.state not in ['paid']):
            raise UserError(_("Kontra Bon has paid state in order cannot be rejected."))
        return self.write({'state': 'rejected'})



    @api.multi
    def button_paid(self):
        if not any(line.invoice_id.state == 'open' for line in self.invoice_line_ids):
            raise UserError(
                _("You can only register payments for open invoices"))

        invoice_ids = self.invoice_line_ids.mapped('invoice_id').ids

        # for invoice in invoice_ids:
        #     invoice.paymenet_residual = invoice.amount_payment
        # prepare_amount_invoices = self._prepare_invoice
        ctx =  dict (
            kontrabon_number = self.name
        )
        ctx.update(create=False,
                   delete=False,
                   menu=False)
        view_id = self.env['ir.model.data'].get_object_reference(
            'account',
            'invoice_supplier_tree')[1]
        return {
            'name': _('Batch Payments Kontra Bon'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'account.invoice',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': "[('partner_id', '=', %d), ('state', 'in', ['open']), ('id', 'in', %s)]" % (
                self.partner_id.id, invoice_ids),
            'context': ctx
        }

    @api.multi
    def button_cancel(self):
        if self.filtered(lambda kontrabon: kontrabon.state not in ['draft', 'approved']):
            raise UserError(_("Kontra Bon must be in draft or approved state in order to be cancelled."))
        return self.action_cancel()

    @api.multi
    def action_cancel(self):
        # TODO: lengkapi dengan proses pembatalan pembayaran, jika kontra bon sdh dalam status dibayar ( tanya
        #  usernya ?)
        self.write({'state': 'cancel'})
        return True

    @api.multi
    def _check_duplicate_supplier_reference(self):
        for invoice in self.invoice_line_ids:
            if self.invoice_line_ids.search([('kontrabon_id', '=', invoice.kontrabon_id.id),
                                             ('invoice_id', '=', invoice.invoice_id.id),
                                             ('id', '!=', invoice.id)]):
                raise UserError(_("Duplicated invoice detected. You probably encoded twice the same vendor bill."))

    @api.multi
    def to_approve_allowed_check(self):
        for rec in self:
            if not rec.to_approve_allowed:
                raise UserError(
                    _("You can't request an approval for a kontra bon "
                      "which is empty or zero amount payment. (%s)") % rec.name)

    @api.multi
    @api.depends('state', 'invoice_line_ids.amount_payment', )
    def _compute_to_approve_allowed(self):
        for rec in self:
            rec.to_approve_allowed = (
                    rec.state == 'draft' and
                    any([not line.amount_payment == 0 for line in rec.invoice_line_ids])
            )

    @api.multi
    def _get_printed_report_name(self):
        self.ensure_one()
        return self.state == 'draft' and _('Draft KontraBon') or \
               self.state in ('approved') and _('Approved KontraBon - %s') % (self.name) or \
               self.state in ('paid') and _('Paid KontraBon - %s') % self.name

    # TODO: amount_word = \
    #       self.currency_id.amount_to_text(amount_total)
    # return self.write({'state': 'paid'})
    # action = self.env.ref('account_payment_kontra_bon.action_invoice_batch_process1').read()[0]
    # return action


    # Fill invoice kontrabon amount automaticly
    my_detail = fields.Boolean(string="Auto Fill Payment Amount", store=False)

    @api.multi
    @api.onchange('my_detail')
    def _onchange_my_detail(self):
        for payline in self.invoice_line_ids:
            # payline.amount_payment = payline.residual
            payline.residual = payline.amount_payment

    @api.depends('invoice_line_ids.invoice_id.state')
    def _compute_payment(self):
        for kb in self:
            payments = self.env['account.payment']
            for line in kb.invoice_line_ids:
                # We keep a limited scope on purpose. Ideally, we should also use move_orig_ids and
                # do some recursive search, but that could be prohibitive if not done correctly.
                bills = line.invoice_id
                payments |= bills.mapped('payment_ids')
            kb.payment_ids = payments
            kb.payment_count = len(payments)


    @api.multi
    def action_view_payment(self):
        '''
        This function returns an action that display existing vendor payments of given kontrabon ids.
        When only one found, show the payment immediately.
        '''
        action = self.env.ref('account.action_account_payments_payable')
        result = action.read()[0]
        ctx = action._context.copy()
        ctx.update(create=False,
                   delete=False)
        result['context'] = ctx
        # result['context'] = {'create': False}
        # jika banyak yang akan di passing bisa alternative yang di bawah
        # ctx = dict(result['context'] or {})
        # ctx.update(create=False)
        pay_ids = self.mapped('payment_ids')
        result['domain'] = "[('id','in',%s)]" % (pay_ids.ids)
        return result


class KontraBonLine(models.Model):
    _name = "kontra.bon.line"
    _description = "Kontra Bon Lines"

    kontrabon_id = fields.Many2one("kontra.bon", string="Kontra Bon", required=True, ondelete='cascade')
    invoice_id = fields.Many2one("account.invoice", string="Bill Number")
    date_invoice = fields.Date(related="invoice_id.date_invoice", string="Bill Date", readonly=True, store=True)
    date_due = fields.Date(related="invoice_id.date_due", string="Due Date", readonly=True, store=True)
    currency_id = fields.Many2one("res.currency", related="invoice_id.currency_id", string="Currency", readonly=True,
                                  store=True)
    amount_untaxed = fields.Monetary(related="invoice_id.amount_untaxed", string="Untaxed Amount", readonly=True,
                                     store=True)
    amount_tax = fields.Monetary(related="invoice_id.amount_tax", string="Tax", readonly=True, store=True)
    amount_total = fields.Monetary(related="invoice_id.amount_total", string="Total", readonly=True, store=True)
    residual = fields.Monetary(related="invoice_id.residual", string="Amount Due", readonly=True, store=True)
    amount_payment = fields.Monetary(string="Payment Amount")
    comments = fields.Text(string="Comments" , default='')
    state = fields.Selection(related="invoice_id.state", string="Status", readonly=True, store=True)


    @api.onchange('invoice_id')
    def _onchange_allowed_invoice_ids(self):
        result = {}

        # TODO: untuk pengajuan kontra bon hanya boleh satu kali untuk nomor invoice/bill yg sama
        #       sampai status kontra bon paid atau rejected atau cancel

        domain = self.get_domain_open_bill()
        result['domain'] = {'invoice_id': domain}
        return result

    @api.multi
    def get_domain_open_bill(self):

        # A Bill can be added only if Bill is not already in the kontra bon
        bill_ids = self.kontrabon_id.invoice_line_ids.mapped('invoice_id')

        domain = [('state', 'in', ['open'])]
        if self.kontrabon_id.partner_id:
            domain += [('partner_id', 'child_of', self.kontrabon_id.partner_id.id)]
        if bill_ids:
            domain += [('id', 'not in', bill_ids.ids)]
        return domain



