from odoo import fields, models, api


class SPBPurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    spb_line_ids = fields.Many2many(
        'ted.surat.permohonan.bayar.line',
        'spb_purchase_order_rel',
        'purchase_order_id',
        'spb_line_id',
        string='SPB Line', readonly=True, copy=False)
    spb_reff = fields.Char(string='SPB Reference')

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super().fields_view_get(view_id=view_id,
                                      view_type=view_type,
                                      toolbar=toolbar,
                                      submenu=submenu)
        # jika semua toolbar mau dihilangkan set --> toolbar = false
        # dan jika auto_search mau dihilangkan set --> auto_search = false
        # dan tidak perlu lagi code dibawah ini
        if toolbar != None and view_type == 'tree' and res['name'] == 'account.invoice.supplier.tree':
            action_list = res['toolbar']['action']
            al = action_list.copy()
            if self._context.get('kontrabon_number'):
                if len(self._context['kontrabon_number']) > 0:
                    for a in range(len(al)):
                        objAction = al[a]
                        if objAction['name'] not in ['Batch Payments', 'Kontra Bon Payments']:
                            action_list.remove(objAction)
                        else:
                            objAction['name'] = 'Kontra Bon Payments'
            else:
                for a in range(len(al)):
                    objAction = al[a]
                    if objAction['name'] in ['Batch Payments', 'Kontra Bon Payments']:
                        action_list.remove(objAction)

        return res

