import base64
import os
import platform
import datetime
from datetime import datetime
from docxtpl import DocxTemplate
from odoo import api, fields, models
from .PrintJob import print_job


def get_sample():
    return {
        'nomor_doc': 12345,
        'supplier': 'Toko ABC',
        'tgl_diterima': '10-10-2019',
        'pemberi': 'TUTI',
        'penerima': 'RUDI',
        'items': [
            {
                'no': 1,
                'product_name': 'Barang-01',
                'product_qty': 30,
                'product_uom': 'Unit',
            },
            {
                'no': 2,
                'product_name': 'Barang-02',
                'product_qty': 50,
                'product_uom': 'Unit',
            },
            {
                'no': 3,
                'product_name': 'Barang-03',
                'product_qty': 60,
                'product_uom': 'Unit',
            }
        ]
    }


class MaterialTransferReportOut(models.Model):
    _name = 'material.transfer.report.docx'
    _description = 'material transfer report'

    material_transfer_data = fields.Char('Name', size=256)
    file_name = fields.Binary('Docx Report', readonly=True)


class WizardPurchaseRequest(models.Model):
    _name = 'wizard.material.transfer.print2'
    _description = "material transfer print wizard"

    @api.multi
    def get_data(self):
        self.ensure_one()
        spids = self.env['stock.picking'].browse(self._context.get('active_ids', list()))
        vno = 0
        for splist in spids:
            items = []
            no = 0
            for mvline in splist.move_lines:
                no += 1
                item_data = {
                        'no': str(no),
                        'product_name': mvline.product_id.name,
                        'product_qty': str(mvline.product_qty),
                        'product_uom': mvline.product_uom.name
                }
                items.append(item_data)
            for restline in range(10 - len(splist.move_lines)):
                no += 1
                item_data = {
                    'no': str(no),
                    'product_name': '',
                    'product_qty': '',
                    'product_uom': ''
                }
                items.append(item_data)

            output_data = {
                            'nomor_doc': str(splist.move_lines[0].purchase_line_id[0].purchase_request_lines[0].request_id.name) +'|' + str(splist.origin),
                            'supplier': str(splist.partner_id.name),
                            'tgl_diterima': str(splist.date_done),
                            'pemberi':  '              ',
                            'penerima': '              ',
                            'items': items
            }
        return output_data

    @api.multi
    def print_report(self):
        self.ensure_one()
        datadir = os.path.dirname(__file__)
        f = os.path.join(datadir, 'templates/BTB.docx')
        #if platform.system() == 'Linux':
        #    f = os.path.join(datadir, 'templates/BTB.docx')
        template = DocxTemplate(f)
        context = self.get_data()
        template.render(context)
        filename = ('/tmp/BTB-' + str(datetime.today().date()) + '.docx')
        #if platform.system() == 'Linux':
        #   filename = ('/tmp/BTB-' + str(datetime.today().date()) + '.docx')
        template.save(filename)
        fp = open(filename, "rb")
        file_data = fp.read()
        out = base64.encodestring(file_data)

        attach_vals = {
            'material_transfer_data': filename,
            'file_name': out,
        }

        act_id = self.env['material.transfer.report.docx'].create(attach_vals)
        fp.close()

        # print_job(filename) --> print to default printer

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'material.transfer.report.docx',
            'res_id': act_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            'context': self.env.context,
            'target': 'new',
        }
