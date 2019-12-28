import base64
import os
import platform
import datetime
from datetime import datetime
from docxtpl import DocxTemplate
from odoo import api, fields, models
from .PrintJob import print_job

class WizardPurchaseRequisitionDoc(models.Model):
    _name = 'purchase.requisition.docx'
    _description = "purchase requisition doc print wizard"

    purchase_requisition_data = fields.Char('Name', size=256)
    file_name = fields.Binary('Docx Report', readonly=True)

class WizardPurchaseRequisition(models.Model):
    _name = 'wizard.purchase.requisition.print2'
    _description = "purchase request print doc wizard"

    @api.multi
    def get_data(self):
        self.ensure_one()
        order = self.env['purchase.requisition'].browse(self._context.get('active_ids', list()))
        for rec in order:
                no = 0
                rows = []
                # amount_total = 0
                product_name = ''
                product_name2 = ''
                product_name3 = ''
                product_code = ''
                product_code2 = ''
                product_code3 = ''
                quantity = 0
                quantity2 = 0
                quantity3 = 0
                vendor_terakhir = ''
                memo = rec.description
                for line in rec.line_ids:
                    # product_name += str(line.product_id.name) + ", "
                    product_code += str(line.product_id.default_code) + ", "
                    quantity += line.product_qty
                    vendor_terakhir = str(line.product_id.last_supplier_id.name)
                    harga_terakhir = str(line.product_id.last_purchase_price)
                    tanggal_terakhir = str(line.product_id.last_purchase_date)

                amount_total_awal = 1000000000
                vendor1=''
                vendor2=''
                vendor3=''
                for line in rec.purchase_ids:
                    vendor_rekomemndasi =''
                    no += 1
                    if no == 1:
                        vendor1 = str(line.partner_id.name)
                    elif no == 2:
                        vendor3 = str(line.partner_id.name)
                    else:
                        vendor3 = str(line.partner_id.name)
                    s = {
                        'no': str(no),
                        'vendor_name': str(line.partner_id.name),
                        'amount_total': str(int(line.amount_total)),
                        'payment_term': str(line.payment_term_id.name)
                    }
                    if line.amount_total< amount_total_awal:
                        vendor_rekomendasi = line.partner_id.name
                        amount_total_awal = line.amount_total

                    rows.append(s)
                    for line1 in line.order_line:
                        if no == 1:
                            product_name = line1.name
                            product_name2=''
                            product_name3=''
                        elif no == 2:
                            product_name=''
                            product_name2=''
                            product_name3=''
                        else:
                            product_name=''
                            product_name2=''
                            product_name3=''

                        for line11 in line1.purchase_request_lines:

                            for line111 in line11.request_id:
                                bppbku = line111.name
                                date_doc = str(line111.date_start)
                                dept = line111.department_id.name
                                # bppbku = line1.purchase_request_lines.request_id.name
                            # bppbku = line.order_line[0].id
                    # bppbku = 1
                data = {
                        'qcf_no': str(rec.name),
                        'no_bppb' : bppbku,
                        'qcf_date' : str(rec.ordering_date),
                        'date_doc' : date_doc,
                        'product_name':product_name,
                        'company':rec.company_id.name,
                        'department': dept,
                        'internal_code': product_code,
                        'quantity' :quantity,
                        'value': str(int(line.amount_total)),
                        'vendor_terakhir': vendor_terakhir,
                        'harga_terakhir': harga_terakhir,
                        'po_terakhir': '',
                        'tanggal_terakhir': tanggal_terakhir,
                        'vendor_rekomendasi': vendor_rekomendasi ,
                        'memo' : memo,
                        'rows':rows
                }
        return data

    @api.multi
    def print_report_doc(self):
        self.ensure_one()
        datadir = os.path.dirname(__file__)
        # f = os.path.join(datadir, 'template/QCF-template.docx')
        if platform.system() == 'Linux':
           f = os.path.join(datadir, 'template/QCFbaru.docx')
        else:
           f = os.path.join(datadir, 'template\QCFbaru.docx')
        template = DocxTemplate(f)
        context = self.get_data()
        template.render(context)
        if platform.system() == 'Linux':
            # filename = ('/tmp/QCF_' + str(datetime.today().date()) + '.docx')
            filename = ('/tmp/QCF_' + 'test' + '.docx')
        else:
            filename = ('QCF_' + 'test' + '.docx')
        template.save(filename)
        fp = open(filename, "rb")
        file_data = fp.read()
        out = base64.encodestring(file_data)

        attach_vals = {
            'purchase_requisition_data': filename,
            'file_name': out,
        }

        act_id = self.env['purchase.requisition.docx'].create(attach_vals)
        fp.close()

        # print_job(filename)

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.requisition.docx',
            'res_id': act_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            'context': self.env.context,
            'target': 'new',
        }
