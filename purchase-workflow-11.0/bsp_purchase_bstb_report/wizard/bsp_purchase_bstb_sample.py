import base64
import os
from datetime import datetime
from docxtpl import DocxTemplate
from odoo import api, fields, models, _


class StockPickingBSTBReportOut(models.Model):
    _name = 'material.transfer.bstb.report.docx'
    _description = 'Material Transfer BSTB Report'

    stock_picking_bstb_data = fields.Char('Name', size=256)
    file_name = fields.Binary('Docx Report', readonly=True)


class WizardStockPickingBSTB(models.Model):
    _name = 'wizard.material.transfer.bstb.print'
    _description = "Material Transfer BSTB Print Wizard"

    @api.multi
    def get_data(self):
        self.ensure_one()
        order = self.env['material.transfer'].browse(self._context.get('active_ids', list()))
        for rec in order:
            items = []
            no = 0;
            for line in rec.move_lines:
                no += 1
                row = {'no': str(no),
                       'product_name': str(line.product_id.name),
                       'description': '', #str(line.name),
                       'last_propose': '',
                       'product_qty': str(line.product_uom_qty),
                       'product_uom': ''} #str(line.product_uom_id.name)}
                items.append(row)
            for restline in range(10-len(rec.move_lines)):
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
                'tanggal': str(rec.scheduled_date),
                'department': (rec.partner_id.name),
                'ext': '', #rec.requested_by.phone,
                'items': items
            }
        return data

    @api.multi
    def print_report(self):
        datadir = os.path.dirname(__file__)
        #f = os.path.join(datadir, 'templates\permintaanbarangbon.docx')
        f = os.path.join(datadir, 'templates\template_bstb.docx')
        template = DocxTemplate(f)
        context = self.get_data()
        template.render(context)
        filename = ('BSTB-' + str(datetime.today().date()) + '.docx')
        #filename = ('BSTB-' + context.get('nobpb','') + '-' + context.get('tanggal','') + '.docx')
        template.save(filename)
        fp = open(filename, "rb")
        file_data = fp.read()
        out = base64.encodestring(file_data)
        attach_vals = {
            'stock_picking_bstb_data': filename,
            'file_name': out,
        }
        act_id = self.env['material.transfer.bstb.report.docx'].create(attach_vals)
        fp.close()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'material.transfer.bstb.report.docx',
            'res_id': act_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            'context': self.env.context,
            'target': 'new',
        }