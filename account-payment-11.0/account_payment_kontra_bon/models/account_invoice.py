from odoo import fields, models, api
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, formatLang


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    kontrabon_line_ids = fields.Many2many(
        'kontra.bon.line',
        'kontra_bon_account_invoice_rel',
        'account_invoice_id',
        'kontra_bon_line_id',
        string='Kontra Bon Line', readonly=True, copy=False)
    kontrabon_reference = fields.Char(string='Kontra Bon Reference')

    @api.multi
    @api.depends('number','amount_total','currency_id')
    def name_get(self):
        result = []
        for inv in self:
            number = inv.number if inv.number  else ''
            if self.env.context.get('show_date_invoice'):  #and inv.date_invoice:
                number += ': ' + formatLang(self.env, inv.amount_total, currency_obj=inv.currency_id)
            result.append((inv.id, number))
        return result

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
                        if objAction['name'] not in ['Batch Payments','Kontra Bon Payments']:
                            action_list.remove(objAction)
                        else:
                            objAction['name'] = 'Kontra Bon Payments'
           else:
               for a in range(len(al)):
                   objAction = al[a]
                   if objAction['name'] in ['Batch Payments', 'Kontra Bon Payments']:
                       action_list.remove(objAction)


        return res