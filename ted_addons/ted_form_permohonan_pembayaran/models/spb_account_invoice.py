from odoo import fields, models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    spb_id = fields.Many2one(comodel_name='ted.surat.permohonan.bayar', string='No. Register SPB')

    @api.onchange('spb_id')
    def onchange_spb_id(self):
        if  self.spb_id:
            amount_to_bill = 0
            purchase_orders=[]
            for spb_line_item in self.spb_id.line_ids:
                amount_to_bill = spb_line_item.purchase_order_amount
                purchase_orders.append(spb_line_item.purchase_order_id)
            self.update(
                {
                    'origin':self.spb_id,
                    'partner_id':self.spb_id.supplier_id,
                    'purchase_id':spb_line_item.purchase_order_id,
                    'amount_total':amount_to_bill
                }
            )
