import base64
import os
import datetime
from io import BytesIO
import xlwt,  base64
from datetime import datetime
from docxtpl import DocxTemplate
from odoo import api, fields, models
from .PrintJob import print_job
from xlsxwriter.workbook import Workbook
from io import StringIO
import platform

style0 = xlwt.easyxf('font: name Times New Roman bold on;align: horiz right;', num_format_str='#,##0.00')
style1 = xlwt.easyxf(
    'font: name Times New Roman bold on; pattern: pattern solid, fore_colour gray25;align: horiz center;',
    num_format_str='#,##0.00')
style2 = xlwt.easyxf('font:height 200,bold True; pattern: pattern solid;',
                     num_format_str='#,##0.00')
style3 = xlwt.easyxf('font:bold True;', num_format_str='#,##0.00')
style4 = xlwt.easyxf('font:bold True;  borders:top double;align: horiz right;', num_format_str='#,##0.00')
style5 = xlwt.easyxf('font: name Times New Roman bold on;align: horiz center;', num_format_str='#,##0')
style6 = xlwt.easyxf('font: name Times New Roman bold on;', num_format_str='#,##0.00')
style7 = xlwt.easyxf('font:bold True;  borders:top double;', num_format_str='#,##0.00')

class BppbReportOut(models.Model):
    _name = 'qcf.report.out'
    _description = 'purchase request report'

    purchase_request_data = fields.Char('File Name', size=256)
    file_name = fields.Binary('BPPB Excel Report', readonly=True)

class BppbReportWizard(models.Model):
    _name = 'bppb.report.wizard'

    #name = fields.Date(string="No BPPB")

    @api.multi
    def get_data(self):
        self.ensure_one()
        req = self.env['purchase.request'].browse(self._context.get('active_ids', list()))
        for rec in req:
            items = []
            vno = 1
            for line in rec.line_ids:
                row = {
                    "no":str(vno),
                    "product_name": str(line.product_id.name),
                    "product_qty": str(line.product_qty),
                    "product_uom":  str(line.product_uom_id.name)
                }
                items.append(row)
                vno += 1

            # down_payments = []
            # vno = 1
            # for dp in rec.advance_payment_ids:
            #     row = {
            #         "no":str(vno),
            #         "dp_date": str(dp.payment_date),
            #         "dp_amount": str(dp.amount),
            #         "remark":  "Uang Muka ke: " + str(vno)
            #     }
            #     down_payments.append(row)
            #     vno += 1

            tgl = str(rec.date_start).rsplit("-", 2);
            tgl2= tgl[2]+"-"+tgl[1]+"-"+tgl[0]

            data = {
                # "po_no": str(rec.name),
                # "supplier": str(rec.partner_id.name),
                # "supplier_add": str(rec.partner_id.street),
                # "po_date": str(rec.date_order),
                "no_bppb": rec.name,
                "tgl": tgl2,
                "pemesan": rec.requested_by.name,
                "fin_dir": "Drs Setiawan Tjahyadi",
                "purc_man": "Erni Sumarni, SE",
                "ref": "PR/BSP/IT/10/2019",
                "items": items
            }
        return data

    @api.multi
    def get_report_doc(self):
        self.ensure_one()
        req = self.env['purchase.request'].browse(self._context.get('active_ids', list()))

        datadir = os.path.dirname(__file__)
        f = os.path.join(datadir, 'templates//bppb.docx')
        template = DocxTemplate(f)
        context = self.get_data()
        template.render(context)
        if platform.system() == 'Linux':
            filename = ('/tmp/BPPB-' + str(datetime.today().date()) + '.docx')
        else:
            filename = ('BPPB-' + str(datetime.today().date()) + '.docx')
        template.save(filename)
        fp = open(filename, "rb")
        file_data = fp.read()
        out = base64.encodestring(file_data)

        # Files actions
        attach_vals = {
            'purchase_request_data': filename,
            'file_name': out,
        }

        act_id = self.env['qcf.report.out'].create(attach_vals)
        fp.close()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'qcf.report.out',
            'res_id': act_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            'context': self.env.context,
            'target': 'new',
        }

    @api.multi
    def get_report_print(self):
        self.ensure_one()
        req = self.env['purchase.request'].browse(self._context.get('active_ids', list()))
        datadir = os.path.dirname(__file__)
        f = os.path.join(datadir, 'templates//bppb_print.docx')
        template = DocxTemplate(f)
        context = self.get_data()
        template.render(context)
        if platform.system() == 'Linux':
            filename = ('/tmp/BPPB-' + str(datetime.today().date()) + '.docx')
        else:
            filename = ('BPPB-' + str(datetime.today().date()) + '.docx')
        template.save(filename)
        fp = open(filename, "rb")
        file_data = fp.read()
        out = base64.encodestring(file_data)

        attach_vals = {
            'purchase_data': filename,
            'file_name': out,
        }

        fp.close()

        print_job(filename)  # --> print to default printer

    @api.multi
    def get_report_excel(self):
        # XLS report
        rows = {}
        label_lists = ['PR NUMBER', 'ORIGIN', 'DATE', 'REQUESTED BY', 'APPROVAL', 'DESCRIPTION', 'COMPANY', 'PRODUCT',
                       'UOM',
                       'QTY', 'DESCR', 'SPEC']
        order = self.env['purchase.request'].browse(self._context.get('active_ids', list()))
        workbook = xlwt.Workbook()
        for rec in order:
            row = []
            for line in rec.line_ids:
                product = {'name': line.product_id.name, 'product_uom_id': line.product_uom_id.name,
                           'product_qty': line.product_qty, 'description': line.name,
                           'specifications': line.specifications}
                row.append(product)

            rows['products'] = row
            rows['name'] = rec.name
            rows['origin'] = rec.origin
            rows['date_start'] = rec.date_start
            rows['requested_by'] = rec.requested_by.name
            rows['assigned_to'] = rec.assigned_to.name
            rows['description'] = rec.description
            rows['company_id'] = rec.company_id.name

            sheet = workbook.add_sheet(rec.name, cell_overwrite_ok=True)

            sheet.write_merge(2, 2, 1, 6, 'PT. BINA SAN PRIMA', style2)
            sheet.write_merge(4, 4, 1, 7, 'BUKTI PERMINTAAN PEMBELIAN BARANG', style1)
            sheet.write_merge(5, 5, 1, 7, '( B P P B )', style1)
            sheet.write_merge(6, 6, 1, 2, 'BPPB No.     :', style3)
            sheet.write_merge(6, 6, 3, 4, rows['name'], style0)
            sheet.write_merge(7, 7, 1, 2, 'Tanggal BPPB :', style3)
            sheet.write_merge(7, 7, 3, 4, rows['date_start'], style0)
            sheet.write_merge(8, 8, 1, 2, 'Bagian yang memesan :', style3)
            sheet.write_merge(8, 8, 3, 4, rows['requested_by'], style0)

            sheet.write(10, 1, 'Qty', style1)
            sheet.write_merge(10, 10, 2, 3, 'Nama Barang', style1)
            sheet.write(10, 4, 'Stock akhir', style1)
            sheet.write(10, 5, 'Contoh Terlampir', style1)
            sheet.write_merge(10, 10, 6, 7, 'Catatan/Menyetujui Fixed Asset Dept.', style1)

            n = 11
            i = 1
            for product in rows['products']:
                sheet.write(n, 1, product['product_qty'], style5)
                sheet.write_merge(n, n, 2, 3, product['name'], style6)
                #sheet.write(n, 4, product['product_uom_id'], style0)
                #sheet.write(n, 5, product['product_qty'], style0)
                #sheet.write_merge(n, n, 6, 7, product['specifications'], style0)
                #sheet.write_merge(n, n, 9, 11, product['description'], style0)
                n += 1
                i += 1

        sheet.write_merge(n, n, 1, 2, "Pemesan :", style6)
        sheet.write_merge(n, n, 3, 4, "Mengetahui :", style6)
        sheet.write_merge(n, n, 5, 6, "Menyetujui :", style6)
        n += 3

        sheet.write_merge(n, n, 1, 2, "(             )", style6)
        sheet.write_merge(n, n, 3, 4, "(             )", style6)
        sheet.write_merge(n, n, 5, 6, "(             )", style6)
        n += 1

        sheet.write_merge(n, n, 1, 7, 'Diisi oleh Bagian Pembelian', style1)
        n += 1
        sheet.write_merge(n, n, 1, 2, "CHECKLIST BPPB", style6)
        sheet.write_merge(n, n, 4, 5, "CHECKLIST BIDDING", style6)
        sheet.write_merge(n, n, 6, 7, "KETERANGAN", style6)
        n += 1

        sheet.write_merge(n, n, 1, 2, "NOMOR BPPB", style6)
        sheet.write_merge(n, n, 4, 5, "SUPPLIER", style6)
        sheet.write_merge(n, n, 6, 7, "", style6)
        n += 1
        sheet.write_merge(n, n, 1, 2, "TANGGAL BPPB", style6)
        sheet.write_merge(n, n, 4, 5, "BPPB", style6)
        sheet.write_merge(n, n, 6, 7, "", style6)
        n += 1
        sheet.write_merge(n, n, 1, 2, "BAGIAN YANG MEMESAN", style6)
        sheet.write_merge(n, n, 4, 5, "HARGA TERAKHIR/AVRG", style6)
        sheet.write_merge(n, n, 6, 7, "", style6)
        n += 1
        sheet.write_merge(n, n, 1, 2, "SPESIFIKASI BARANG", style6)
        sheet.write_merge(n, n, 4, 5, "HARGA 6 BLN TERAKHIR", style6)
        sheet.write_merge(n, n, 6, 7, "", style6)
        n += 1
        sheet.write_merge(n, n, 1, 2, "ALASAN PENGAJUAN", style6)
        sheet.write_merge(n, n, 4, 5, "TGL BELI TERAKHIR", style6)
        sheet.write_merge(n, n, 6, 7, "", style6)
        n += 1
        sheet.write_merge(n, n, 1, 2, "STOCK TERAKHIR", style6)
        sheet.write_merge(n, n, 4, 5, "PENAWARAN RESMI", style6)
        sheet.write_merge(n, n, 6, 7, "", style6)
        n += 1
        sheet.write_merge(n, n, 1, 2, "ALOKASI UNTUK SIAPA", style6)
        sheet.write_merge(n, n, 4, 5, "NEGOSIASI HARGA", style6)
        sheet.write_merge(n, n, 6, 7, "", style6)
        n += 1
        sheet.write_merge(n, n, 1, 2, "TTD PEMESAN", style6)
        sheet.write_merge(n, n, 4, 5, "", style6)
        sheet.write_merge(n, n, 6, 7, "", style6)
        n += 1
        sheet.write_merge(n, n, 1, 2, "TTD MENGETAHUI", style6)
        sheet.write_merge(n, n, 4, 5, "", style6)
        sheet.write_merge(n, n, 6, 7, "", style6)
        n += 1
        sheet.write_merge(n, n, 1, 2, "TTD MENYETUJUI", style6)
        sheet.write_merge(n, n, 4, 5, "", style6)
        sheet.write_merge(n, n, 6, 7, "", style6)
        n += 4

        sheet.write_merge(n, n, 1, 2, "Purchasing Staff", style6)
        sheet.write_merge(n, n, 4, 5, "Purchasing Spv", style6)
        sheet.write_merge(n, n, 6, 7, "Purchasing Manager", style6)
        #n += 1

        output = StringIO()
        label = (';'.join(label_lists))
        output.write(label)
        output.write("\n")

        if platform.system() == 'Linux':
            filename = ('/tmp/BPPB-' + str(datetime.today().date()) + '.xls')
        else:
            filename = ('BPPB-' + str(datetime.today().date()) + '.xls')

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

        act_id = self.env['qcf.report.out'].create(attach_vals)
        fp.close()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'qcf.report.out',
            'res_id': act_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            'context': self.env.context,
            'target': 'new',
        }
