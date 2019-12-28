import base64
import os
from datetime import datetime
from docxtpl import DocxTemplate
from odoo import api, fields, models, _


class PurchaseRequestBPBReportOut(models.Model):
    _name = 'purchase.request.bpb.report.docx'
    _description = 'purchase request bpb report'

    purchase_request_data = fields.Char('Name', size=256)
    file_name = fields.Binary('BPB docx Report', readonly=True)


class WizardPurchaseRequestBPB(models.Model):
    _name = 'wizard.purchase.request.bpb.print'
    _description = "purchase request bpb print wizard"

    @api.multi
    def get_data(self):
        self.ensure_one()
        order = self.env['purchase.request'].browse(self._context.get('active_ids', list()))
        for rec in order:
            items = []
            no = 0;
            for line in rec.line_ids:
                no += 1
                row = {'no': str(no),
                       'product_name': str(line.product_id.name),
                       'description': str(line.product_id.attribute_line_ids.attribute_id.name) + ' ' + str(line.product_id.attribute_value_ids.name),
                       'last_propose': '',
                       'product_qty': str(line.product_qty),
                       'product_uom': str(line.product_uom_id.name)}
                items.append(row)
            for restline in range(10-len(rec.line_ids)):
                no += 1
                row = {'no': str(no),
                       'product_name': '',
                       'description': '',
                       'last_propose': '',
                       'product_qty': '',
                       'product_uom': ''}
                items.append(row)
            row = {'no': '',
                   'product_name': '',
                   'description': '',
                    'last_propose': '',
                   'product_qty': '',
                   'product_uom': ''}
            items.append(row)
            data = {
                'nobpb': str(rec.name),
                'tanggal': str(rec.date_start),
                'department': (rec.department_id.name),
                'ext': rec.requested_by.phone,
                'items': items
            }
        return data

    @api.multi
    def print_report(self):
        datadir = os.path.dirname(__file__)
        # f = os.path.join(datadir, 'templates\purchase_request.docx')
        f = os.path.join(datadir, 'templates/permintaanbarangbon.docx')
        template = DocxTemplate(f)
        context = self.get_data()
        template.render(context)
        # filename = ('PurchaseRequestRep-' + str(datetime.today().date()) + '.docx')
        # filename = (context.get('nobpb','') + '_' + context.get('tanggal','') + '.docx')
        #filename = 'nobpb' + '_' + context.get('tanggal', '') + '.docx'
        filename = ('/tmp/nobpb' + '_' + context.get('tanggal', '') + '.docx')
	#filename = ('/tmp/PurchaseRequestReport-' + str(datetime.today().date()) + '.xls')
        template.save(filename)
        fp = open(filename, "rb")
        file_data = fp.read()
        out = base64.encodestring(file_data)
        attach_vals = {
            'purchase_request_data': filename,
            'file_name': out,
        }
        act_id = self.env['purchase.request.bpb.report.docx'].create(attach_vals)
        fp.close()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.request.bpb.report.docx',
            'res_id': act_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            'context': self.env.context,
            'target': 'new',
        }
