# -*- coding: utf-8 -*-
import xlwt
import datetime
import time
import base64
from io import StringIO
from datetime import datetime
from odoo import api, fields, models, _
import platform

styles = {'datetime': xlwt.easyxf(num_format_str='dd-mm-yyyy hh:mm:ss'),
          'date': xlwt.easyxf(num_format_str='dd-mm-yyyy'),
          'time': xlwt.easyxf(num_format_str='hh:mm:ss'),
          'number': xlwt.easyxf(num_format_str='#,##0.00'),
          'header': xlwt.easyxf('font: name Times New Roman, color-index black, bold on, height 200', num_format_str='#,##0.00'),
          'theader': xlwt.easyxf('font: name Times New Roman, color-index black, bold on;align: horiz center', num_format_str='#,##0.00'),
          'default': xlwt.Style.default_style}


class PurchaseRequestRecapReportOut(models.Model):
    _name = 'purchase.request.recap.reports'
    _description = 'purchase Request Recapitulation Report'

    purchase_request_recap_data = fields.Char('Name', size=256)
    file_name = fields.Binary('PR Recap Excel Report', readonly=True)


class WizardWizards(models.Model):
    _name = 'wizard.purchase.request.recap.reports'
    _description = 'purchase request recap wizard'
    
    date_start = fields.Date(string="Start Date", required=True, default=fields.Date.today)
    date_end = fields.Date(string="End Date", required=True, default=fields.Date.today)

    def get_width(num_characters):
        return int((1 + num_characters) * 256)

    @api.multi
    def action_purchase_request_recap_report(self):
        # XLS report
        rows = {}
        label_lists = ['TGL. MASUK', 'NAMA BARANG', 'KETERANGAN', 'JENIS BARANG',
                       'DEPARTEMENT', 'TGL_PR', 'TGL_PROC_PR', 'NO_PR','TGL_QCF','NO_QCF',
                       'TGL. PO','NO. PO','TGL.APROVE', 'PEMOHON', 'PENGGUNA', 'NO. POLISH',
                       'QTY','HARGA(Rp.)','HARGA(US$)', 'TOTAL(Rp.)', 'TOTAL(US$)', 'PPN_STT',
                       'SUPPLIER','KETERANGAN','TGL. PENBAR','TGL. BSTB']
        order = self.env['purchase.request'].search(['&',('date_start', '>=', self.date_start), ('date_start', '<=', self.date_end)])

        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('RECAP-BPPB', cell_overwrite_ok=True)
        sheet.write(0, 0, 'LAPORAN : ', styles['header'])
        sheet.write(0, 1, 'BPPB', styles['header'])
        sheet.write(1, 0, 'PERIODE :', styles['header'])
        periode = self.date_start + " s/d " + self.date_end
        sheet.write(1, 1, periode, styles['header'])
        
        for x in range(0, 26):
            sheet.write(3, x, label_lists[x], styles['theader'])

        no = 1
        ii = 4
        for rec in order:
            for line in rec.line_ids:
                sheet.write(ii, 0, datetime.strptime(rec.date_start, "%Y-%m-%d"), styles['date'])
                sheet.write(ii, 1, line.name, styles['default'])
                sheet.write(ii, 2, line.name, styles['default'])
                sheet.write(ii, 3, line.product_id.type, styles['default'])
                sheet.write(ii, 4, rec.department_id.name, styles['default'])
                sheet.write(ii, 5, datetime.strptime(rec.date_start, "%Y-%m-%d"), styles['date'])
                sheet.write(ii, 6, datetime.strptime(rec.received_doc_date, "%Y-%m-%d") if rec.received_doc_date else '', styles['date'])
                sheet.write(ii, 7, rec.name, styles['default'])
                sheet.write(ii, 13, rec.requested_by.name, styles['default'])
                sheet.write(ii, 14, rec.employee_id.name, styles['default'])
                sheet.write(ii, 15, "No-Insurance", styles['default'])
                sheet.write(ii, 16, line.product_qty, styles['number'])
                if line.purchase_lines:
                    for order_line in (line.purchase_lines):
                        if order_line.state =='purchase':
                            sheet.write(ii, 8, datetime.strptime(order_line.order_id.date_order, '%Y-%m-%d %H:%M:%S') if order_line.order_id.date_order else '', styles['date'])
                            sheet.write(ii, 9, order_line.order_id.name, styles['default'])
                            sheet.write(ii, 10, datetime.strptime(order_line.order_id.date_order, "%Y-%m-%d %H:%M:%S") if order_line.order_id.date_order else '' , styles['date'])
                            sheet.write(ii, 11, order_line.order_id.name, styles['default'])
                            sheet.write(ii, 12, datetime.strptime(order_line.order_id.date_approve, "%Y-%m-%d") if order_line.order_id.date_approve else '', styles['date'])
                            sheet.write(ii, 17, order_line.price_unit, styles['number'])
                            sheet.write(ii, 18, order_line.price_unit, styles['number'])
                            sheet.write(ii, 19, order_line.order_id.amount_total, styles['number'])
                            sheet.write(ii, 20, order_line.order_id.amount_total, styles['number'])
                            sheet.write(ii, 21, order_line.price_tax, styles['number'])
                            sheet.write(ii, 22, order_line.order_id.partner_id.name, styles['default'])
                            sheet.write(ii, 23, order_line.order_id.notes, styles['default'])
                            sheet.write(ii, 24, datetime.strptime(order_line.move_ids.date, "%Y-%m-%d %H:%M:%S") if order_line.move_ids.date else '' , styles['date'])
                            sheet.write(ii, 25, datetime.strptime(order_line.move_ids.date, "%Y-%m-%d %H:%M:%S") if order_line.move_ids.date else '', styles['date'])

                ii += 1
                no += 1

        if platform.system() == 'Linux':
            filename = ('/tmp/PurchaseRequestRecapReport-' + str(datetime.today().date()) + '.xls')
        else:
            filename = ('PurchaseRequestRecapReport-' + str(datetime.today().date()) + '.xls')
        # filename = filename.split('/')[0]
        workbook.save(filename)
        fp = open(filename, "rb")
        file_data = fp.read()
        out = base64.encodestring(file_data)

        # Files actions
        attach_vals = {
            'purchase_request_recap_data': filename,
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

