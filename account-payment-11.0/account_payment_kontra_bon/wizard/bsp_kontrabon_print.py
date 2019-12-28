import base64
import datetime
import os
import platform
from num2words import num2words
from datetime import datetime
from docxtpl import DocxTemplate
from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT


class BspKontrabonPrintOut(models.Model):
    _name = 'kontra.bon.print.docx'
    _description = 'Kontrabon Print'

    bsp_kontrabon_data = fields.Char('Name', size=256)
    file_name = fields.Binary('Docx Report', readonly=True)


class WizzardBspKontrabon(models.Model):
    _name = 'wizard.kontra.bon.print'
    _description = 'kontra Bon print wizzard'

    kontrabon = fields.Char(store=False)
    @api.multi
    def _get_selection_value(self, model, field, value):
        selection = self.pool.get(model)._columns.get(field).selection
        val = ''
        for v in selection:
            if v[0] == value:
                val = v[1]
            break
        return val

    @api.multi
    def get_data(self):
        self.ensure_one()
        kb = self.env['kontra.bon'].browse(self._context.get('active_ids', list()))
        # AmountText = self.env['terbilang']
        for rec in kb:
            self.kontrabon = rec.name
            items = []
            totaldetail = 0
            line_no  = 1
            for line in rec.invoice_line_ids:
                row = {
                    'line_item': str(line_no),
                    'kontrabon_id': str(line.kontrabon_id.id),
                    'invoice_id': str(line.invoice_id.number) if line.invoice_id else '',
                    'date_invoice': datetime.strptime(line.date_invoice, DATE_FORMAT).strftime('%d %b %Y'),
                    'amount_untaxed': str("{0:12,.2f}".format(line.amount_untaxed)),
                    'amount_tax': str("{0:12,.2f}".format(line.amount_tax)),
                    'amount_total': str("{0:12,.2f}".format(line.amount_total)),
                    'residual': str("{0:12,.2f}".format(line.residual)),
                    'amount_payment': str("{0:12,.2f}".format(line.amount_payment)),
                    'comments': str(line.comments)if line.comments else ''
                }
                totaldetail += line.amount_total
                line_no += 1
                items.append(row)
            data = {
                'name': str(rec.name),
                'partner_id': str(rec.partner_id.name),
                'date_doc': datetime.strptime(rec.date_doc, DATE_FORMAT).strftime('%d %b %Y'),
                'date_receipt': datetime.strptime(rec.date_receipt, DATE_FORMAT).strftime('%d %b %Y'),
                #                'chk_kwitansi': str(dict(self._fields['chk_kwitansi'].selection)(rec.chk_kwitansi)),
                'chk_kwitansi': dict(rec._fields['chk_kwitansi']._description_selection(rec.env)).get(rec.chk_kwitansi),
                'chk_faktur': dict(rec._fields['chk_faktur']._description_selection(rec.env)).get(rec.chk_faktur),
                'chk_bppb': dict(rec._fields['chk_bppb']._description_selection(rec.env)).get(rec.chk_bppb),
                'chk_qcf': dict(rec._fields['chk_qcf']._description_selection(rec.env)).get(rec.chk_qcf),
                'chk_po': dict(rec._fields['chk_po']._description_selection(rec.env)).get(rec.chk_po),
                'chk_bpb': dict(rec._fields['chk_bpb']._description_selection(rec.env)).get(rec.chk_bpb),
                'chk_bstb': dict(rec._fields['chk_bstb']._description_selection(rec.env)).get(rec.chk_bstb),
                'chk_sj': dict(rec._fields['chk_sj']._description_selection(rec.env)).get(rec.chk_sj),
                'chk_fpajak': dict(rec._fields['chk_fpajak']._description_selection(rec.env)).get(rec.chk_fpajak),
                'amount_payment_total': str("{0:12,.2f}".format(rec.amount_payment_total)),
                'terbilang': num2words(rec.amount_payment_total, lang='id').upper(),
                'items': items
            }
        return data

    @api.multi
    def print_report(self):
        self.ensure_one()
        datadir = os.path.dirname(__file__)
        if platform.system() == 'Linux':
            f = os.path.join(datadir, 'templates/kontrabon_template.docx')
        else:
            f = os.path.join(datadir, 'templates\kontrabon_template.docx')
        template = DocxTemplate(f)
        context = self.get_data()
        template.render(context)
        if platform.system() == 'Linux':
            filename = ('/tmp/BSPKontrabon-'+ self.kontrabon + '-' + str(datetime.today().date()) + '.docx')
        else:
            filename = ('BSPKontrabon-' + self.kontrabon + '-' + str(datetime.today().date()) + '.docx')
        template.save(filename)
        fp = open(filename, 'rb')
        file_data = fp.read()
        out = base64.encodestring(file_data)

        attach_vals = {
            'bsp_kontrabon_data': filename,
            'file_name': out,
        }

        act_id = self.env['kontra.bon.print.docx'].create(attach_vals)
        fp.close()

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'kontra.bon.print.docx',
            'res_id': act_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            'context': self.env.context,
            'target': 'new',
        }
