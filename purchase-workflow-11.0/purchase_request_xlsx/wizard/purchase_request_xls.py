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
    _name = 'purchase.request.report.out'
    _description = 'purchase request report'

    purchase_request_data = fields.Char('Name', size=256)
    file_name = fields.Binary('PR Excel Report', readonly=True)
    purchase_request_work = fields.Char('Name', size=256)
    file_names = fields.Binary('PR CSV Report', readonly=True)


class WizardWizards(models.Model):
    _name = 'wizard.purchase.request.reports'
    _description = 'purchase request wizard'

    @api.multi
    def action_purchase_request_report(self):
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

            sheet.write_merge(2, 3, 4, 6, 'Purchase Request :', style2)
            sheet.write_merge(2, 3, 7, 8, rows['name'], style2)
            sheet.write_merge(5, 5, 1, 2, 'Creation Date.', style3)
            sheet.write_merge(5, 5, 3, 4, rows['date_start'], style0)
            sheet.write_merge(5, 5, 8, 9, 'Requested by', style3)
            sheet.write_merge(5, 5, 10, 11, rows['requested_by'], style0)
            sheet.write_merge(6, 6, 8, 9, 'Approver', style3)
            sheet.write_merge(6, 6, 10, 11, rows['assigned_to'], style0)
            sheet.write_merge(7, 7, 8, 9, 'Company', style3)
            sheet.write_merge(7, 7, 10, 11, rows['company_id'], style0)

            sheet.write(10, 1, 'NO', style1)
            sheet.write_merge(10, 10, 2, 3, 'PRODUCT', style1)
            sheet.write(10, 4, 'UOM', style1)
            sheet.write(10, 5, 'QTY', style1)
            sheet.write_merge(10, 10, 6, 8, 'DESCR', style1)
            sheet.write_merge(10, 10, 9, 11, 'SPEC', style1)

            n = 11
            i = 1
            for product in rows['products']:
                sheet.write(n, 1, i, style5)
                sheet.write_merge(n, n, 2, 3, product['name'], style6)
                sheet.write(n, 4, product['product_uom_id'], style0)
                sheet.write(n, 5, product['product_qty'], style0)
                sheet.write_merge(n, n, 6, 8, product['description'], style0)
                sheet.write_merge(n, n, 9, 11, product['specifications'], style0)
                n += 1
                i += 1

        # CSV report
        datas = []
        for values in order:
            for value in values.line_ids:
                if value.product_id.seller_ids:
                    item = [
                        str(value.request_id.name or ''),
                        str(value.request_id.origin or ''),
                        str(value.request_id.date_start or ''),
                        str(value.request_id.requested_by.name or ''),
                        str(value.request_id.assigned_to.name or ''),
                        str(value.request_id.description or ''),
                        str(value.request_id.company_id.name or ''),
                        str(value.product_id.name or ''),
                        str(value.product_uom_id.name or ''),
                        str(value.product_qty or ''),
                        str(value.product_qty or ''),
                        str(value.description or ''),
                        str(value.specifications or ''),
                    ]
                    datas.append(item)

        output = StringIO()
        label = (';'.join(label_lists))
        output.write(label)
        output.write("\n")

        for data in datas:
            record = ';'.join(data)
            output.write(record)
            output.write("\n")
        data = base64.b64encode(bytes(output.getvalue(), "utf-8"))

        if platform.system() == 'Linux':
            filename = ('/tmp/PurchaseRequestReport-' + str(datetime.today().date()) + '.xls')
            filename2 = ('/tmp/PurchaseRequestReport-' + str(datetime.today().date()) + '.csv')
        else:
            filename = ('PurchaseRequestReport-' + str(datetime.today().date()) + '.xls')
            filename2 = ('PurchaseRequestReport-' + str(datetime.today().date()) + '.csv')

        filename = filename.split('/')[0]
        filename2 = filename2.split('/')[0]
        workbook.save(filename)
        fp = open(filename, "rb")
        file_data = fp.read()
        out = base64.encodestring(file_data)

        # Files actions
        attach_vals = {
            'purchase_request_data': filename,
            'file_name': out,
            'purchase_request_work': filename2,
            'file_names': data,
        }

        act_id = self.env['purchase.request.report.out'].create(attach_vals)
        fp.close()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.request.report.out',
            'res_id': act_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            'context': self.env.context,
            'target': 'new',
        }
