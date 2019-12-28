# -*- coding: utf-8 -*-
import xlwt
import datetime
import base64
from io import StringIO
from datetime import datetime
from odoo import api, fields, models, _
import platform

style0 = xlwt.easyxf('font: name Times New Roman bold on;align: horiz right;', num_format_str='#,##0.00')
style1 = xlwt.easyxf(
    'font: name Times New Roman bold on; pattern: pattern solid, fore_colour gray25;align: horiz center;',
    num_format_str='#,##0.00')
style2 = xlwt.easyxf('font:height 400,bold True; pattern: pattern solid, fore_colour gray25;',
                     num_format_str='#,##0.00')
style3 = xlwt.easyxf('font:bold True;', num_format_str='#,##0.00')
style4 = xlwt.easyxf('font:bold True;  borders:top double;align: horiz right;', num_format_str='#,##0.00')
style5 = xlwt.easyxf('font: name Times New Roman bold on;align: horiz center;', num_format_str='#,##0')
style6 = xlwt.easyxf('font: name Times New Roman bold on;', num_format_str='#,##0.00')
style7 = xlwt.easyxf('font:bold True;  borders:top double;', num_format_str='#,##0.00')


class PurchaseRequestReportOut(models.Model):
    _name = 'purchase.request.recap.reports'
    _description = 'purchase request recap report'

    purchase_request_data = fields.Char('Name', size=256)
    file_name = fields.Binary('PR Excel Report', readonly=True)

class WizardWizards(models.Model):
    _name = 'wizard.purchase.request.recap.reports'
    _description = 'purchase request recap wizard'

    date_start = fields.Date(string="Start Date", required=True, default=fields.Date.today)
    date_end = fields.Date(string="End Date", required=True, default=fields.Date.today)

    @api.multi
    def action_purchase_request_report(self):
        # XLS report
        rows = {}
        order = self.env['purchase.request'].search(['&',('date_start', '>=', self.date_start), ('date_start', '<=', self.date_end)])

        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('data_recap', cell_overwrite_ok=True)
        sheet.write(0, 0, 'LAPORAN : ', style0)
        sheet.write(0, 1, 'BPPB', style0)
        sheet.write(1, 0, 'PERIODE :', style0)
        periode = self.date_start + " s/d " + self.date_end
        sheet.write(1, 1, periode, style0)

        sheet.write(3, 0, 'NO', style1)
        sheet.write(3, 1, 'TGL TERIMA', style1)
        sheet.write(3, 2, 'CABANG', style1)
        sheet.write(3, 3, 'SPESIFIKASI', style1)
        sheet.write(3, 4, 'QTY', style1)
        sheet.write(3, 5, 'UNIT', style1)
        sheet.write(3, 6, 'PR NUMBER', style1)
        sheet.write(3, 7, 'PO NUMBER', style1)
        no = 1
        ii = 4
        for rec in order:
            for line in rec.line_ids:
                c = len(rec.line_ids.purchase_lines.ids)
                if c > 0:
                    for i in range(0, c):
                        ponumber = rec.line_ids.purchase_lines[i].order_id.name
                        sheet.write(ii, 0, no, style5)
                        sheet.write(ii, 1, rec.received_doc_date, style5)
                        sheet.write(ii, 2, rec.company_id.name, style5)

                        sheet.write(ii, 3, line.name, style6)
                        sheet.write(ii, 4, line.product_qty, style0)
                        sheet.write(ii, 5, line.product_uom_id.name, style6)
                        sheet.write(ii, 6, rec.name, style6)
                        sheet.write(ii, 7, ponumber, style6)
                        ii += 1
                        no += 1
                else:
                    sheet.write(ii, 0, no, style5)
                    sheet.write(ii, 1, rec.received_doc_date, style5)
                    sheet.write(ii, 2, rec.company_id.name, style5)

                    sheet.write(ii, 3, line.name, style6)
                    sheet.write(ii, 4, line.product_qty, style0)
                    sheet.write(ii, 5, line.product_uom_id.name, style6)
                    sheet.write(ii, 6, rec.name, style6)
                    sheet.write(ii, 7, '', style6)
                    ii += 1
                    no += 1

        if platform.system() == 'Linux':
            filename = ('/tmp/PurchaseRequestReport-' + str(datetime.today().date()) + '.xls')
        else:
            filename = ('PurchaseRequestReport-' + str(datetime.today().date()) + '.xls')
        filename = filename.split('/')[0]
        workbook.save(filename)
        fp = open(filename, "rb")
        file_data = fp.read()
        out = base64.encodestring(file_data)

        # Files actions
        attach_vals = {
            'purchase_request_data': filename,
            'file_name': out,
        }

        act_id = self.env['purchase.request.recap.reports'].create(attach_vals)
        fp.close()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.request.recap.reports',
            'res_id': act_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            'context': self.env.context,
            'target': 'new',
        }
