import base64
import os
import datetime
import platform
from datetime import datetime
from docxtpl import DocxTemplate
from odoo import api, fields, models
from .PrintJob import print_job


def get_sample():
    return {
        'name': 12345,
        'date_start': '10-10-2019',
        'company': 'BLG',
        'net_amount_total': 96000000,
        'note': 'penggantian dan service rutin',
        'items': [
            {
                'product_name': 'ABCD-01',
                'description': 'Service Ganti Oli',
                'product_qty': 30,
                'product_uom': 'Unit',
                'discount': 10,
                'price_unit': 50000,
                'net_price_subtotal': 1589000
            },
            {
                'product_name': 'ABCD-02',
                'description': 'Spare part',
                'product_qty': 50,
                'product_uom': 'Unit',
                'discount': 10,
                'price_unit': 80000,
                'net_price_subtotal': 1544000
            },
            {
                'product_name': 'ABCD-03',
                'description': 'Service saja',
                'product_qty': 60,
                'product_uom': 'Unit',
                'discount': 15,
                'price_unit': 588000,
                'net_price_subtotal': 17889000
            }
        ]
    }


class PurchaseRequestReportOut(models.Model):
    _name = 'purchase.request.report.docx'
    _description = 'purchase request report'

    purchase_request_data = fields.Char('Name', size=256)
    file_name = fields.Binary('Docx Report', readonly=True)


class WizardPurchaseRequest(models.Model):
    _name = 'wizard.purchase.request.print2'
    _description = "purchase request print wizard"

    @api.multi
    def get_data(self):
        self.ensure_one()
        order = self.env['purchase.request'].browse(self._context.get('active_ids', list()))
        for rec in order:
            items = []
            for line in rec.line_ids:
                row = {'product_name': str(line.product_id.name),
                       'description': str(line.name),
                       'product_qty': str(line.product_qty),
                       'product_uom': str(line.product_uom_id.name),
                       'discount': str(line.discount),
                       'price_unit': str(line.price_unit),
                       'net_price_subtotal': str(line.net_price_subtotal)}
                items.append(row)
            data = {
                'name': str(rec.name),
                'date_start': str(rec.date_start),
                'company': (rec.company_id.name),
                'net_amount_total': str(rec.net_amount_total),
                'note': rec.description,
                'items': items
            }
        return data

    @api.multi
    def print_report(self):
        self.ensure_one()
        datadir = os.path.dirname(__file__)
        if platform.system() == 'Linux':
            f = os.path.join(datadir, 'templates/purchase_request.docx')
        else:
            f = os.path.join(datadir, 'templates\purchase_request.docx')
        template = DocxTemplate(f)
        # context = self.get_data()
        context = get_sample()
        template.render(context)
        if platform.system() == 'Linux':
            filename = ('/tmp/PurchaseRequestRep_' + str(datetime.today().date()) + '.docx')
        else:
            filename = ('PurchaseRequestRep_' + str(datetime.today().date()) + '.docx')
        template.save(filename)
        fp = open(filename, "rb")
        file_data = fp.read()
        out = base64.encodestring(file_data)

        attach_vals = {
            'purchase_request_data': filename,
            'file_name': out,
        }

        act_id = self.env['purchase.request.report.docx'].create(attach_vals)
        fp.close()

        print_job(filename)

        # return {
        #     'type': 'ir.actions.act_window',
        #     'res_model': 'purchase.request.report.docx',
        #     'res_id': act_id.id,
        #     'view_type': 'form',
        #     'view_mode': 'form',
        #     'context': self.env.context,
        #     'target': 'new',
        # }

# import cups
# conn = cups.Connection()
# printers = conn.getPrinters()
# fileName = "/tmp/test1.txt"
# conn.printFile("Epson-L120", fileName, "", {})