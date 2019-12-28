from odoo import api, fields, models


class PurchaseKontrabon(models.Model):
    _name = 'purchase.kontrabon'
    _description = 'Purchase Kontrabon'

    # @api.model
    # def _vendor_get(self):
    #     vendor_id = self.env['res.partner']._partner_default_get(self._name)
    #     return self.env['res.partner'].browse(vendor_id.id)

    name = fields.Char(String='No Kontrabon', default='New')
    kb_date = fields.Date(String='Tanggal Kontrabon',
                                required=True,
                                default=fields.Date.context_today)
    return_date = fields.Date(String='Tanggal Kembali', default=fields.Date.context_today)
    vendor_id = fields.Many2one('res.partner', 'Vendor',
                                 required=True)
    line_ids = fields.One2many('purchase.kontrabon.line', 'kontrabon_id',
                               'Kontrabon lines',
                               readonly=False,
                               copy=True, )
    kwitansi = fields.Selection([('asli', 'Asli'), ('copy', 'Copy'), ('none', 'Tidak Ada')], default='none')
    faktur = fields.Selection([('asli', 'Asli'), ('copy', 'Copy'), ('none', 'Tidak Ada')], default='none')
    bpb = fields.Selection([('asli', 'Asli'), ('copy', 'Copy'), ('none', 'Tidak Ada')], default='none')
    po = fields.Selection([('asli', 'Asli'), ('copy', 'Copy'), ('none', 'Tidak Ada')], default='none')
    faktur_pajak = fields.Selection([('asli', 'Asli'), ('copy', 'Copy'), ('none', 'Tidak Ada')], default='none')

    @api.multi
    def button_load_payment_kontrabon(self):

        rel_view_id = self.env.ref('purchase_kontrabon.purchase_payment_view')
        if self.vendor_id.id:
           listFaktur = self.env['account.invoice'].search([('date_due', '>=', self.kb_date),
                                                            ('partner_id', '=', self.vendor_id.id)],
                                                                    order = 'date_invoice DESC').mapped('id')
        else:
            warning = {'title': 'Warning!', 'message': 'Vendor must be defined!'}
            return {'warning': warning}

        if not listFaktur:
            #raise Warning("No payment history found.!")
            warning = {'title': 'Warning!', 'message': 'No payment history found.!'}
            return {'warning': warning}
        else:
            return {
                'domain': [('id', 'in', listFaktur)],
                'views': [(rel_view_id.id, 'tree')],
                'name': 'Payment History',
                'res_model': 'account.invoice',
                'view_id': rel_view_id.id,
                'type': 'ir.actions.act_window',
                'target': 'new'
            }


class PurchaseKontrabonLine(models.Model):
    _name = 'purchase.kontrabon.line'
    _description = 'Purchase Kontrabon Line'

    kontrabon_id = fields.Many2one('purchase.kontrabon',
                                  String='Purchase Kontrabon',
                                  ondelete='cascade',
                                  readonly=True)
    line_item = fields.Integer('No')
    invoice_date = fields.Date('Tanggal Faktur')
    invoice_no = fields.Char('Nomor Faktur')
    invoice_amount = fields.Float('Jumlah')
    remark = fields.Char('Keterangan')
    invoice_id = fields.Many2one('account.invoice',
                                 String='Invoice')






