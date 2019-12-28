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
    'font: name Times New Roman bold on; borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_colour gray25;align: vert center, horiz center;',
    num_format_str='#,##0.00')
style2 = xlwt.easyxf('font:height 400,bold True; pattern: pattern solid, fore_colour gray25;',
                     num_format_str='#,##0.00')
style3 = xlwt.easyxf('font:bold True;', num_format_str='#,##0.00')
style4 = xlwt.easyxf('font:bold True;  borders:top double;align: horiz right;', num_format_str='#,##0.00')
style5 = xlwt.easyxf('font: name Times New Roman bold on;align: horiz center;', num_format_str='#,##0')
style6 = xlwt.easyxf('font: name Times New Roman bold on;', num_format_str='#,##0.00')
style7 = xlwt.easyxf('font:bold True;  borders:top double;', num_format_str='#,##0.00')
style8 = xlwt.easyxf(
    'font: name Times New Roman bold on; align: vert center, horiz center;',
    num_format_str='#,##0.00')

class PurchaseRequestReportOut(models.Model):
    _name = 'purchase.request.recap.qcf.reports'
    _description = 'purchase request recap qcf report'

    purchase_request_data = fields.Char('Name', size=256)
    file_name = fields.Binary('PR Excel Report', readonly=True)

class WizardWizards(models.Model):
    _name = 'wizard.purchase.request.recap.qcf.reports'
    _description = 'purchase request recap qcf wizard'

    date_start = fields.Date(string="Start Date", required=True, default=fields.Date.today)
    date_end = fields.Date(string="End Date", required=True, default=fields.Date.today)

    @api.multi
    def action_purchase_request_qcf_report(self):
        # XLS report
        rows = {}
        order = self.env['purchase.request'].search(['&',('date_start', '>=', self.date_start), ('date_start', '<=', self.date_end)])

        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('data_recap', cell_overwrite_ok=True)
        sheet.write_merge(0,0,0,18, 'REKAP  QUOTATION COMPARISON FORM ', style8)
        #sheet.write(1,0, 'PERIODE :', style0)
        periode = self.date_start + " s/d " + self.date_end
        sheet.write_merge(1,1,0,18, 'PERIODE : '+periode, style8)
        sheet.write_merge(3,4,0,0, 'NO', style1)
        sheet.write_merge(3,4,1,1, 'TANGGAL', style1)
        sheet.write_merge(3,4,2,2, 'NO QCF', style1)
        sheet.write_merge(3,4,3,3, 'NO BPB', style1)
        sheet.write_merge(3,4,4,4, 'CABANG/DEPT', style1)
        sheet.write_merge(3,4,5,5, 'KETERANGAN', style1)
        sheet.write_merge(3,4,6,6, 'QTY', style1)
        sheet.write_merge(3,3,7,8, 'C-Martien', style1)
        sheet.write(4,7, 'Masuk', style1)
        sheet.write(4,8, 'Kembali', style1)
        sheet.write_merge(3,3,9,10, 'Ibu Nani', style1)
        sheet.write(4,9, 'Masuk', style1)
        sheet.write(4,10, 'Kembali', style1)
        sheet.write_merge(3,3,11,12, 'P-Bambang', style1)
        sheet.write(4,11, 'Masuk', style1)
        sheet.write(4,12, 'Kembali', style1)
        sheet.write_merge(3,3,13,14, 'P-Setiawan', style1)
        sheet.write(4,13, 'Masuk', style1)
        sheet.write(4,14, 'Kembali', style1)
        sheet.write_merge(3,3,15,16, 'P-Jahja S', style1)
        sheet.write(4,15, 'Masuk', style1)
        sheet.write(4,16, 'Kembali', style1)
        sheet.write_merge(3,4,17,17, 'KETERANGAN', style1)
        sheet.write_merge(3,4,18,18, 'PRINCIPAL', style1)

        no = 1
        ii = 5
        for rec in order:
            noqcf =''
            # sheet.write(ii, 0, no, style5)
            # sheet.write(ii, 1, rec.received_doc_date, style5)
            # sheet.write(ii, 3, rec.name, style6)
            # sheet.write(ii, 4, rec.company_id.name, style5)
            keterangan = ""
            total = 0
            totalqty = 0
            for line in rec.line_ids:
                c = len(line.purchase_lines.ids)
                for i in range(0, c):
                    # keterangan = ""
                    noqcf = line.purchase_lines[i].order_id.origin
                    if noqcf == '' or noqcf == False :
                        noqcf == ''
                    else:
                        # sheet.write(ii, 0, no, style5)
                        # sheet.write(ii, 1, rec.received_doc_date, style5)
                        # sheet.write(ii, 3, rec.name, style6)
                        # sheet.write(ii, 4, rec.company_id.name, style5)
                        # keterangan = ""
                        if line.purchase_lines[i].order_id.state == "purchase":
                            keterangan += line.name + " ("+(str(line.product_qty))+") Rp " + str(line.price_unit)
                            # total += line.purchase_lines[i].order_id.amount_total
                            total += line.product_qty * line.price_unit
                            totalqty += line.product_qty
                            sheet.write(ii, 0, no, style5)
                            sheet.write(ii, 1, rec.received_doc_date, style5)
                            sheet.write(ii, 3, rec.name, style6)
                            sheet.write(ii, 4, rec.company_id.name, style5)
            if noqcf == ''  or noqcf == False:
                noqcf == ''
            else:
                keterangan += " Total "+str(total)
                sheet.write(ii, 5, keterangan, style0)
                sheet.write(ii, 6, totalqty, style0)
                sheet.write(ii, 2, noqcf, style6)
                no += 1

            ii += 1

        if platform.system() == 'Linux':
            filename = ('/tmp/PurchaseRequestQcf-' + str(datetime.today().date()) + '.xls')
        else:
            filename = ('PurchaseRequest -' + str(datetime.today().date()) + '.xls')
        #filename = filename.split('/')[0]
        workbook.save(filename)
        fp = open(filename, "rb")
        file_data = fp.read()
        out = base64.encodestring(file_data)

        # Files actions
        attach_vals = {
            'purchase_request_data': filename,
            'file_name': out,
        }

        act_id = self.env['purchase.request.recap.qcf.reports'].create(attach_vals)
        fp.close()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.request.recap.qcf.reports',
            'res_id': act_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            'context': self.env.context,
            'target': 'new',
        }
