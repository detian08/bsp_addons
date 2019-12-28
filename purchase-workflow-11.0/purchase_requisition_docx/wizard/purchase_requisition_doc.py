import base64
import os
import platform
import datetime
# from datetime import datetime
from docxtpl import DocxTemplate,R
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
        vendor1 = ''
        vendor2 = ''
        vendor3 = ''
        tv1 = ''
        tv2 = ''
        tv3 = ''
        penjumlah1 = 0
        penjumlah2 = 0
        penjumlah3 = 0
        no_bppb = ''
        date_doc = ''
        dept = ''
        items = []
        vno = 1
        memo = ''
        for rec in order:
            if rec.description:
                memo = rec.description
            for line in rec.line_ids:
                row = {}
                no = 0
                if line.purchase_request_lines.request_id.name !='':
                    no_bppb = str(line.purchase_request_lines.request_id.name)
                if line.purchase_request_lines.request_id.date_start!='':
                    # date_doc = str(line.purchase_request_lines.request_id.date_start)
                    date_doc = str(datetime.datetime.strptime(format(line.purchase_request_lines.request_id.date_start), "%Y-%m-%d").strftime(
                        "%d-%b-%y"))
                if line.purchase_request_lines.request_id.department_id.name!='':
                    dept = str(line.purchase_request_lines.request_id.department_id.name)
                # tanggal = datetime.datetime.strptime(line.product_id.last_purchase_date, "%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d')
                row.update({
                    "no": str(vno),
                    "nama_produk": str(line.product_id.name),
                    "qty": str("{0:8,.0f}".format(line.product_qty)),
                    "last_price": str("{0:8,.0f}".format(line.product_id.last_purchase_price)),
                    "last_supp": str(line.product_id.last_supplier_id.name),
                    "last_order": str(datetime.datetime.strptime(format(line.product_id.last_purchase_date), "%Y-%m-%d").strftime("%d-%b-%y")),
                })
                for record in self.env['purchase.order'].sudo().search(
                    [('requisition_id', '=', rec.id)]):
                    no += 1
                    if no == 1:
                        vendor1 = str(record.partner_id.name)
                        tv1 = str(record.payment_term_id.name)
                        for isi_po in self.env['purchase.order.line'].search(
                                [('order_id', '=', record.id), ('product_id', '=', line.product_id.id)]):
                            if isi_po:
                                row.update({
                                    # "price_total1": str("{0:12,.2f}".format(isi_po.price_unit * isi_po.product_qty)),
                                    "price_total1": str("{0:12,.0f}".format(isi_po.price_total)),
                                })
                            else:
                                row.update({
                                    "price_total1": '',
                                    "price_total2": '',
                                })
                            # penjumlah1 += (isi_po.price_unit * isi_po.product_qty)
                            penjumlah1 += (isi_po.price_total)
                    if no == 2:
                        vendor2 = str(record.partner_id.name)
                        tv2 = str(record.payment_term_id.name)
                        for isi_po in self.env['purchase.order.line'].search(
                                [('order_id', '=', record.id), ('product_id', '=', line.product_id.id)]):
                            if isi_po:
                                row.update({
                                    "price_total2": str("{0:12,.0f}".format(isi_po.price_total)),
                                })
                            else:
                                row.update({
                                    "price_total2": '',
                                    "price_total3": '',
                                })
                            penjumlah2 += (isi_po.price_total)
                    if no == 3:
                        vendor3 = str(record.partner_id.name)
                        tv3 = str(record.payment_term_id.name)
                        for isi_po in self.env['purchase.order.line'].search(
                                [('order_id', '=', record.id), ('product_id', '=', line.product_id.id)]):
                            if isi_po:
                                row.update({
                                    "price_total3": str("{0:12,.0f}".format(isi_po.price_total)),
                                })
                            else:
                                row.update({
                                    "price_total3": '',
                                })
                            penjumlah3 += (isi_po.price_total)
                    if no == 1:
                        row.update({
                            "price_total2": '',
                            "price_total3": '',
                            })
                vno += 1
                items.append(row)
        murah = penjumlah1
        vendor_rekomemndasi = vendor1
        if murah > penjumlah2:
            if penjumlah2>0:
                murah = penjumlah2
                vendor_rekomemndasi = vendor2
        if murah > penjumlah3:
            if penjumlah3>0:
                murah = penjumlah3
                vendor_rekomemndasi = vendor3
        data = {
            'vendor1': vendor1,
            'vendor2': vendor2,
            'vendor3': vendor3,
            'jumlah1': str("{0:12,.0f}".format(penjumlah1)),
            'jumlah2': str("{0:12,.0f}".format(penjumlah2)),
            'jumlah3': str("{0:12,.0f}".format(penjumlah3)),
            'qcf_no': str(rec.name),
            # 'qcf_date': str(rec.ordering_date),
            "qcf_date": str(datetime.datetime.strptime(format(rec.ordering_date), "%Y-%m-%d").strftime("%d-%b-%y")),
            'company': rec.company_id.name,
            'value':str("{0:12,.2f}".format(murah)),
            'batas':murah,
            'no_bppb': no_bppb,
            'date_doc': date_doc,
            'vendor_rekomendasi': vendor_rekomemndasi,
            'memo': R(memo),
            'dept': dept,
            'pay1': tv1,
            'pay2': tv2,
            'pay3': tv3,
            'item':items,
        }
        return data

    @api.multi
    def print_report_doc(self):
        self.ensure_one()
        datadir = os.path.dirname(__file__)
        # f = os.path.join(datadir, 'template/QCF-template.docx')
        context = self.get_data()
        murah = context['batas']
        if murah > 1000000:
            if platform.system() == 'Linux':
               f = os.path.join(datadir, 'template/QCFbaru5.docx')
            else:
               f = os.path.join(datadir, 'template\QCFbaru5.docx')
        else:
            if platform.system() == 'Linux':
               f = os.path.join(datadir, 'template/QCFbaru1.docx')
            else:
               f = os.path.join(datadir, 'template\QCFbaru1.docx')
        template = DocxTemplate(f)
        template.render(context,autoescape=True)
        if murah > 1000000:
            if platform.system() == 'Linux':
                # filename = ('/tmp/QCF_' + str(datetime.today().date()) + '.docx')
                filename = ('/tmp/QCF_' + 'Besar' + '.docx')
            else:
                filename = ('QCF_' + 'Besar' + '.docx')
        else:
            if platform.system() == 'Linux':
                # filename = ('/tmp/QCF_' + str(datetime.today().date()) + '.docx')
                filename = ('/tmp/QCF_' + 'Kecil' + '.docx')
            else:
                filename = ('QCF_' + 'Kecil' + '.docx')
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
