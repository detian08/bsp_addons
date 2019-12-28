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
    'font: name Times New Roman bold on; align: horiz center;', num_format_str='#,##0.00')
style2 = xlwt.easyxf('font:height 200,bold True; pattern: pattern solid;',
                     num_format_str='#,##0.00')
style3 = xlwt.easyxf('font:bold True;', num_format_str='#,##0.00')
style4 = xlwt.easyxf('font:bold True;  borders:top double;align: horiz right;', num_format_str='#,##0.00')
style5 = xlwt.easyxf('font: name Times New Roman bold on;align: horiz center;', num_format_str='#,##0')
style6 = xlwt.easyxf('font: name Times New Roman bold on;', num_format_str='#,##0.00')
style7 = xlwt.easyxf('font:bold True;  borders:top double;', num_format_str='#,##0.00')

class QcfReportOut(models.Model):
    _name = 'qcf.report.out'
    _description = 'purchase request report'

    purchase_request_data = fields.Char('File Name', size=256)
    file_name = fields.Binary('BPPB Excel Report', readonly=True)

class QcfReportWizard(models.Model):
    _name = 'qcf.report.wizard'

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
                    "product_uom":  str(line.product_uom_id.name),
                    "partner_id1": str(line.partner_id1.name),
                    "partner_id2": str(line.partner_id2.name),
                    "partner_id3": str(line.partner_id3.name),
                    "estimated_cost1": str(line.estimated_cost1),
                    "estimated_cost2": str(line.estimated_cost2),
                    "estimated_cost3": str(line.estimated_cost3),
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
        f = os.path.join(datadir, 'templates//qcf.docx')
        template = DocxTemplate(f)
        context = self.get_data()
        template.render(context)
        filename = ('QCF-' + str(req.name.replace("/","")) + '.docx')
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
        f = os.path.join(datadir, 'templates//qcf_print.docx')
        template = DocxTemplate(f)
        context = self.get_data()
        template.render(context)
        filename = ('QCF-' + str(req.name.replace("/","")) + '.docx')
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
                product = {'name': line.product_id.name,
                           'product_uom_id': line.product_uom_id.name,
                           'product_qty': line.product_qty, 'description': line.name,
                           'specifications': line.specifications,
                           'vendor1': line.partner_id1.name,
                           'vendor2': line.partner_id2.name,
                           'vendor3': line.partner_id3.name,
                           'estimasi1': line.estimated_cost1,
                           'estimasi2': line.estimated_cost2,
                           'estimasi3': line.estimated_cost3}
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

            # sheet.write_merge(2, 2, 1, 6, 'PT. BINA SAN PRIMA', style2)
            sheet.write_merge(4, 4, 1, 11, 'Quotation Comparison form', style3)
            sheet.write_merge(5, 5, 1, 8, 'No. ', style6)
            sheet.write_merge(5, 5, 9, 11, 'Date ', style6)
            sheet.write_merge(6, 6, 1, 3, 'BPPB No. & Date :', style3)
            sheet.write_merge(6, 6, 4, 7, str(rows['name'] + ' & ' + rows['date_start']), style6)
            sheet.write_merge(7, 7, 1, 3, 'Head Office / Branch Office :', style3)
            sheet.write_merge(7, 7, 4, 7, rows['requested_by'], style6)

            sheet.write_merge(8, 10, 1, 1, 'No', style1)
            sheet.write_merge(8, 10, 2, 4, 'Material / Item', style1)
            sheet.write_merge(8, 10, 5, 5, 'Qty', style1)
            sheet.write_merge(8, 8, 6, 11, 'Supplier Name', style1)

            sheet.write_merge(9, 9, 6, 7, product['vendor1'], style1)
            sheet.write_merge(9, 9, 8, 9, product['vendor2'], style1)
            sheet.write_merge(9, 9, 10, 11, product['vendor3'], style1)

            sheet.write(10, 6, 'Satuan', style1)
            sheet.write(10, 7, 'Total', style1)
            sheet.write(10, 8, 'Satuan', style1)
            sheet.write(10, 9, 'Total', style1)
            sheet.write(10, 10, 'Satuan', style1)
            sheet.write(10, 11, 'Total', style1)

            n = 11
            i = 1
            for product in rows['products']:
                sheet.write(n, 1, str(i), style5)
                sheet.write_merge(n, n, 2, 4, product['name'], style6)
                sheet.write(n, 5, product['product_qty'], style0)
                sheet.write(n, 6, product['product_uom_id'], style0)
                sheet.write(n, 7, product['estimasi1'], style0)
                sheet.write(n, 8, product['product_uom_id'], style0)
                sheet.write(n, 9, product['estimasi2'], style0)
                sheet.write(n, 10, product['product_uom_id'], style0)
                sheet.write(n, 11, product['estimasi3'], style0)

                n += 1
                i += 1

        sheet.write_merge(n, n, 1, 5, "GRAND TOTAL", style6)
        sheet.write_merge(n, n, 6, 7, product['estimasi1'], style6)
        sheet.write_merge(n, n, 8, 9, product['estimasi2'], style6)
        sheet.write_merge(n, n, 10, 11, product['estimasi3'], style6)

        n += 3

        sheet.write_merge(n, n, 1, 4, "Negotiated by :", style1)
        sheet.write_merge(n, n, 8, 11, "Acknowledged by :", style1)

        output = StringIO()
        label = (';'.join(label_lists))
        output.write(label)
        output.write("\n")

        if platform.system() == 'Linux':
            filename = ('/tmp/QCF-' + rec.name.replace("/","") + '.xls')
        else:
            filename = ('QCF-' + rec.name.replace("/","") + '.xls')

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