from odoo import api, fields, models, _
from num2words import num2words
import pandas as pd
import numpy as np

_STATES = [
    ('draft', 'Draft'),
    ('to_approve', 'To be approved'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('open', 'Open'),
    ('cancel', 'Cancelled')
]


# class SelectPurchaseOrder(models.Model):
#     _name = 'select.purchase.order'
#     purchase_order_ids = fields.Many2many('purchase.order',
#                                          'spb_po_rel',
#                                          'spb_id','purchase_order_id',
#                                           string='Purchase Orders'
#                                         )
#     @api.multi
#     def  create_spb_line(self):
#         spb_id = self.env['ted.surat.permohonan.bayar'].browse(self._context.get('active_id', False))
#         for po_data in self.purchase_order_ids:
#             self.env['ted.surat.permohonan.bayar.line'].create({
#                     'purchase_order_id': po_data.id,
#                     'spb_id': spb_id,
#                     'purchase_order_name': po_data.name,
#                     'purchase_order_amount':po_data.amount_total
#                 })
#         spb_id._update_link_account_invoice(spb_id.id)

class TedSuratPermohonanPembayaran(models.Model):
    _name = 'ted.surat.permohonan.bayar'
    _description = 'Header Surat Permohonan Pembayaran'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.multi
    @api.onchange('supplier_id')
    def onchange_supplier_id(self):
        self.supplier_id = self.supplier_id
        self.supplier_name = self.supplier_id.name
        self.payment_dest_supplier_name = self.supplier_id.name
        try:
            bank_info = self.supplier_id.bank_ids[0]
            self.payment_dest_bank_acc_name = self.supplier_id.bank_ids[0].bank_account_name
            self.payment_dest_bank_acc_no = self.supplier_id.bank_ids[0].acc_number
            self.payment_dest_bank_name = self.supplier_id.bank_ids[0].bank_name
            self.payment_dest_bank_branch_name = self.supplier_id.bank_ids[0].bank_branch_name
            self.payment_dest_bank_branch_address = self.supplier_id.bank_ids[0].bank_branch_addr1
        except:
            self.payment_dest_bank_acc_name = ''
            self.payment_dest_bank_acc_no = ''
            self.payment_dest_bank_name = ''
            self.payment_dest_bank_branch_name = ''
        if self.line_ids:
            self.amount_value = 0
            for po_data in self.line_ids:
                self.amount_value = self.amount_value + po_data.spb_line_amount
            if self.company_id.currency_id.name == 'IDR':
                self.amount_words = num2words(int(self.amount_value), lang='id', to='currency')
            else:
                self.amount_words = num2words(self.amount_value, lang='en', to='currency')
            self.amount_words_disp = self.amount_words

    @api.multi
    @api.onchange('line_ids')
    def onchange_line_id(self):
        self.amount_value = 0
        for po_data in self.line_ids:
            self.amount_value = self.amount_value + po_data.spb_line_amount
        if self.company_id.currency_id.name == 'IDR':
            self.amount_words = num2words(int(self.amount_value), lang='id', to='currency')
        else:
            self.amount_words = num2words(self.amount_value, lang='en', to='currency')
        self.amount_words_disp = self.amount_words

    @api.multi
    @api.onchange('amount_value')
    def onchange_amount_value(self):
        if self.company_id.currency_id.name == 'IDR':
            self.amount_words = num2words(int(self.amount_value), lang='id', to='currency')
        else:
            self.amount_words = num2words(self.amount_value, lang='en', to='currency')
        self.amount_words_disp = self.amount_words

    @api.model
    def _company_get(self):
        company_id = self.env['res.company']._company_default_get(self._name)
        return self.env['res.company'].browse(company_id.id)

    @api.depends('amount_value')
    @api.multi
    def _get_amount_in_words(self):
        if self.amount_value:
            if self.company_id.currency_id.name == 'IDR':
                self.amount_words = num2words(int(self.amount_value), lang='id', to='currency')
            else:
                self.amount_words = num2words(self.amount_value, lang='en', to='currency')
            self.amount_words_disp = self.amount_words

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('spb.sequence') or '/'
        request = super(TedSuratPermohonanPembayaran, self).create(vals)
        self._update_link_purchase_order(request.ids[0])
        return request

    @api.multi
    def write(self, vals):
        result = super(TedSuratPermohonanPembayaran, self).write(vals)
        self._update_link_purchase_order(self.id)
        return result

    @api.depends('line_ids.purchase_order_amount')
    @api.multi
    def _update_link_purchase_order(self, id):
        obj_spb = self.env['ted.surat.permohonan.bayar'].browse(id)
        for line in obj_spb.line_ids:
            po_id = line.purchase_order_id.id
            # Get semua id dari kontra.bon.line yang menggunakan invoice_id = _id
            line_ids = self.env['ted.surat.permohonan.bayar.line'].search([('purchase_order_id', '=', po_id)]).ids
            objPurchaseOrder = self.env['purchase.order'].search([('id', '=', po_id)])
            # update many2many
            rec = objPurchaseOrder.write({
                'spb_reff': self._prepare_spb_reference(line_ids),
                'spb_line_ids': [(6, 0, line_ids)]
            })
        return True

    @api.multi
    def _prepare_spb_reference(self, line_ids):
        objSPBLines = self.env['ted.surat.permohonan.bayar.line'].search([('id', 'in', line_ids)])
        spb_ids = objSPBLines.mapped('spb_id')
        vals = ', '.join(spb_ids.mapped('name'))
        return vals

    @api.onchange('spb_line_ids')
    def _onchange_spb_reference(self):
        spb_ids = self.line_ids.mapped('spb_line_id')
        if spb_ids:
            self.spb_reff = ', '.join(spb_ids.mapped('name'))

    name = fields.Char(string='No. Register',
                       required=True,
                       default='New')
    assigned_to = fields.Char(string='UP',
                              required=True)
    doc_date = fields.Date(string='Tanggal',
                           required=True,
                           default=fields.Date.context_today)
    payment_purpose = fields.Text(string='Untuk Pembayaran')
    company_id = fields.Many2one('res.company', 'Company',
                                 required=True,
                                 default=_company_get,
                                 track_visibility='onchange')
    currency_id = fields.Many2one('res.currency',
                                  related='company_id.currency_id',
                                  string='Currency')
    supplier_id = fields.Many2one(comodel_name='res.partner',
                                  string='Kepada',
                                  required=True,
                                  store=True,
                                  track_visibility='onchange',
                                  domain=[('supplier', '=', True)])
    supplier_name = fields.Char(string='Nama Supplier',
                                store=True,
                                track_visibility='onchange')
    amount_value = fields.Monetary(string='Sebesar',
                                   track_visibility='onchange',
                                   store=True
                                   )
    amount_words = fields.Text(compute='_get_amount_in_words',
                               store=True,)
    amount_words_disp = fields.Char(string = 'Terbilang')
    payment_dest_supplier_name = fields.Char(string='Pembayaran ke',
                                             track_visibility='onchange',
                                             store=True)
    payment_dest_bank_acc_name = fields.Char(string='Nama Rekening',
                                             store=True,
                                             track_visibility='onchange')
    payment_dest_bank_acc_no = fields.Char(string='No. Rekening',
                                           store=True,
                                           track_visibility='onchange')
    payment_dest_bank_name = fields.Char(string='Nama Bank',
                                         store=True,
                                         track_visibility='onchange')
    payment_dest_bank_branch_name = fields.Char(string='Nama Cabang',
                                                store=True,
                                                track_visibility='onchange')
    payment_dest_bank_branch_address = fields.Char(string='Alamat Cabang',
                                                   store=True,
                                                   track_visibility='onchange')
    acknowledged_by1 = fields.Many2one(comodel_name='hr.employee',
                                       string='Hormat Kami')
    acknowledged_by2 = fields.Many2one(comodel_name='hr.employee',
                                       string='Mengetahui')
    # invoice_line_ids = fields.One2many("kontra.bon.line", "kontrabon_id", "Bill of Kontra Bon")
    invoice_ids = fields.One2many(comodel_name='account.invoice',
                                  inverse_name='spb_id',
                                  string='Vendor Bills')
    invoice_count = fields.Integer(compute='_compute_payment', string='Transfer',
                                   default=0, store=True,
                                   compute_sudo=True)
    line_ids = fields.One2many(comodel_name='ted.surat.permohonan.bayar.line',
                               inverse_name='spb_id',
                               string='List of Purchase Order', )
    autofill_advance = fields.Boolean(string="Auto Fill Payment Amount", store=False)
    state = fields.Selection(selection=_STATES,
                             string='Status',
                             index=True,
                             track_visibility='onchange',
                             required=True,
                             copy=False,
                             default='draft')

    @api.multi
    @api.onchange('autofill_advance')
    def _onchange_autofill_advance(self):
        test = 0
        # for po_data in self.line_ids:
        #     adv_pays = po_data.advance_payment_ids
        #     if adv_pays:  # ada advance payment
        #         filtered_adv_pays = list(filter(lambda x: (x.state == 'posted')))
        #         if filtered_adv_pays:
        #             adv_df = pd.DataFrame(filtered_adv_pays)
        #             adv_max = adv_df[adv_df.payment_date == adv_df.payment_date.max()]
        #             po_data.last_advance_payment_date = adv_max.payment_date
        #             po_data.last_advance_payment_amount = adv_max.amount
        #     else:  # belum ada advance payment
        #         po_data.spb_line_amount = po_data.purchase_order_amount

    @api.depends('line_ids.purchase_order_id.state')
    def _compute_payment(self):
        for spb in self:
            invoices = self.env['account.invoice']
            for line in spb.line_ids:
                # We keep a limited scope on purpose. Ideally, we should also use move_orig_ids and
                # do some recursive search, but that could be prohibitive if not done correctly.
                purchase_order_id = line.purchase_order_id
                invoices |= purchase_order_id.mapped('invoice_ids')
            spb.invoice_ids = invoices
            spb.payment_count = len(invoices)


#                 create advance payment

class TedSuratPermohonanPembayaranLine(models.Model):
    _name = 'ted.surat.permohonan.bayar.line'
    _description = 'Line Item Surat Permohonan Pembayaran'

    spb_id = fields.Many2one("ted.surat.permohonan.bayar",
                             string="SPB Header",
                             ondelete='cascade')

    purchase_order_id = fields.Many2one("purchase.order",
                                        string="Purchase Order")

    purchase_order_name = fields.Char(related="purchase_order_id.name",
                                      string="Nomor PO",
                                      readonly=True,
                                      store=True)
    currency_id = fields.Many2one('res.currency',
                                  string='PO Currency',
                                  related='purchase_order_id.currency_id')
    purchase_order_amount = fields.Monetary(related="purchase_order_id.amount_total",
                                            string='Nilai Purchase Order',
                                            readonly=True,
                                            store=True)
    last_advance_payment_date = fields.Date(string='Last Advance Payment Date',
                                            readonly=True,
                                            store=True)
    state = fields.Selection(related="purchase_order_id.state",
                             string="Status PO",
                             readonly=True,
                             store=True)
    last_advance_payment_amount = fields.Monetary(string='Last Advance Payment Amount',
                                                  readonly=True,
                                                  store=True)
    spb_line_amount = fields.Monetary(string='Nilai Pembayaran')

    # purchase_order_last_adv_pay_id = fields
    @api.onchange('purchase_order_id')
    def _onchange_allowed_po_ids(self):
        result = {}
        domain = self.get_domain_open_po()
        result['domain'] = {'purchase_order_id': domain}
        return result

    @api.multi
    def get_domain_open_po(self):
        # A Bill can be added only if Bill is not already in the kontra bon
        po_ids = self.spb_id.line_ids.mapped('purchase_order_id')

        # domain = [('state', 'in', ['locked'])]
        domain = [('state', 'in', ['purchase'])]
        domain += [('invoice_status', 'in', ['no', 'to_invoice'])]
        if self.spb_id.supplier_id:
            domain += [('partner_id', 'child_of',
                        self.spb_id.supplier_id.id)]  # domain PO yang dipilih adalah milik anak perusahaan partner ID
        if po_ids:
            domain += [('id', 'not in', po_ids.ids)]
        return domain
