import base64
import os
import platform
import datetime
from datetime import datetime
from docxtpl import DocxTemplate
from odoo import api, fields, models
from dateutil.relativedelta import relativedelta
# from .PrintJob import print_job


class PurchaseRequestK14(models.Model):
    _name = 'purchase.request.k4'
    _description = "purchase request print"

    purchase_request_data = fields.Char('Name', size=256)
    file_name = fields.Binary('Purchase Docx Report', readonly=True)


class WizardPurchaseRequestK14(models.Model):
    _name = 'wizard.purchase.request.k4'
    _description = "purchase request print wizard"

    @api.multi
    def get_data(self):
        self.ensure_one()
        order = self.env['purchase.request'].browse(self._context.get('active_ids', list()))
        dt = order.create_date
        # monthyear = fields.datetime.from_string  dt.strftime("%B %Y")
        monthyear = fields.Date.from_string(dt).strftime("%B %Y")

        for rec in order:
            items = []
            rowcnt = 1
            for line in rec.line_ids:
                row = {'no': str(rowcnt),
                       'product_name': str(line.product_id.name),
                       'description': str(line.name),
                       'product_qty':  line.product_qty,
                       'qty_buffer': line.qty_buffer,
                       'qty_usage_last_month1': line.qty_usage_last_month1,
                       'qty_usage_last_month2': line.qty_usage_last_month2,
                       'qty_usage_last_month3': line.qty_usage_last_month3,
                       'qty_available': line.qty_available,
                       'qty_avg_usage': line.qty_avg_usage,
                       'estimated_cost1': line.estimated_cost1,
                       'estimated_cost2': line.estimated_cost2,
                       'product_uom': str(line.product_uom_id.name),
                       'discount':  line.discount,
                       'price_unit':  line.price_unit,
                       'net_price_subtotal':  line.net_price_subtotal
                }
                items.append(row)
                rowcnt += 1

            data = {
                'document_number': str(rec.name),
                'doc_type': str(rec.doc_type),
                'date_start': str(rec.date_start),
                'company': (rec.company_id.name),
                'net_amount_total': str(rec.net_amount_total),
                'note': rec.description,
                'monthyear': str(monthyear),
                'month3': str((datetime.now() - relativedelta(months=3)).strftime("%B")),
                'month2': str((datetime.now() - relativedelta(months=2)).strftime("%B")),
                'month1': str((datetime.now() - relativedelta(months=1)).strftime("%B")),
                'items': items
            }
        return data

    @api.multi
    def print_report(self):
        self.ensure_one()
        datadir = os.path.dirname(__file__)
        order = self.env['purchase.request'].browse(self._context.get('active_ids', list()))
        doctype = order.doc_type
        if platform.system() == 'Linux':
            if doctype == 'K4':
                f = os.path.join(datadir, 'templates/purchase_request_k4.docx')
            elif doctype == 'K3':
                f = os.path.join(datadir, 'templates/purchase_request_k3.docx')
            elif doctype == 'K2':
                f = os.path.join(datadir, 'templates/purchase_request_k2.docx')
            elif doctype == 'K1':
                f = os.path.join(datadir, 'templates/purchase_request_k1.docx')
            else:
                f = os.path.join(datadir, 'templates/purchase_request_k0.docx')
        else:
            if doctype == 'K4':
                f = os.path.join(datadir, 'templates\purchase_request_k4.docx')
            elif doctype == 'K3':
                f = os.path.join(datadir, 'templates\purchase_request_k3.docx')
            elif doctype == 'K2':
                f = os.path.join(datadir, 'templates\purchase_request_k2.docx')
            elif doctype == 'K1':
                f = os.path.join(datadir, 'templates\purchase_request_k1.docx')
            else:
                f = os.path.join(datadir, 'templates\purchase_request_k0.docx')

        template = DocxTemplate(f)
        context = self.get_data()
        # context = get_sample()
        template.render(context)
        if platform.system() == 'Linux':
            filename = ('/tmp/PurchaseRequestRep-' + str(datetime.today().date()) + '.docx')
        else:
            filename = ('PurchaseRequestRep-' + str(datetime.today().date()) + '.docx')
        template.save(filename)
        fp = open(filename, "rb")
        file_data = fp.read()
        out = base64.encodestring(file_data)

        attach_vals = {
            'purchase_request_data': filename,
            'file_name': out,
        }

        act_id = self.env['purchase.request.k4'].create(attach_vals)
        fp.close()

        # print_job(filename) #--> print to default printer

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.request.k4',
            'res_id': act_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            'context': self.env.context,
            'target': 'new',
        }
