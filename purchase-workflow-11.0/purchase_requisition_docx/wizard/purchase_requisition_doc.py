import base64
import os
import platform
import datetime
# from datetime import datetime
from docxtpl import DocxTemplate,R
from odoo import api, fields, models
from .PrintJob import print_job
import subprocess

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
        name = (order.name if order.name else '')
        vendor1 = ''
        vendor2 = ''
        vendor3 = ''
        tv1 = ''
        tv2 = ''
        tv3 = ''
        penjumlah1 = 0
        penjumlah2 = 0
        penjumlah3 = 0
        mahal = 0
        selisih = ''
        persen = ''
        no_bppb = ''
        date_doc = ''
        dept = ''
        items = []
        vno = 1
        memo = ''
        pajak1 = '-'
        pajak2 = '-'
        pajak3 = '-'
        pic1 = ''
        pic2 = ''
        pic3 = ''
        for rec in order:
            if rec.description:
                memo = rec.description
            for line in rec.line_ids:
                row = {}
                no = 0
                # terakhir = ''
                if line.purchase_request_lines.request_id.name:
                    no_bppb = str(line.purchase_request_lines.request_id.name)
                if line.purchase_request_lines.request_id.date_start:
                    # date_doc = str(line.purchase_request_lines.request_id.date_start)
                    date_doc = " / "+str(datetime.datetime.strptime(format(line.purchase_request_lines.request_id.date_start), "%Y-%m-%d").strftime(
                        "%d-%b-%y"))
                if line.purchase_request_lines.request_id.department_id.name:
                    dept = str(line.purchase_request_lines.request_id.department_id.name)
                # if line.product_id.last_purchase_date!='':
                #     terakhir=str(datetime.datetime.strptime(format(line.product_id.last_purchase_date), "%Y-%m-%d").strftime("%d-%b-%y"))
                # tanggal = datetime.datetime.strptime(line.product_id.last_purchase_date, "%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d')
                order_terakhir = self.env['purchase.order.line'].search([('product_id','=',line.product_id.id),('product_qty','>',0),('state','=','purchase')],limit=1,order='create_date desc');
                if order_terakhir:
                    date_time_str = str(order_terakhir.order_id.create_date)
                    date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
                    row.update({
                        "no": str(vno),
                        "nama_produk": str(line.product_id.name),
                        "qty": str("{0:8,.0f}".format(line.product_qty) if line.product_qty else 0),
                        "last_price": str("{0:8,.0f}".format(order_terakhir.price_unit) if order_terakhir.price_unit else ''),
                        "last_supp": str(order_terakhir.order_id.partner_id.name if order_terakhir.order_id.partner_id.name else ''),
                        "last_order": str(date_time_obj.date()),
                        # "last_order": str(datetime.datetime.strptime(format(order_terakhir.order_id.create_date), "%Y-%m-%d").strftime("%d-%b-%y") if order_terakhir.order_id.create_date else ''),
                        # "last_order": terakhir,
                    })
                else:
                    row.update({
                        "no": str(vno),
                        "nama_produk": str(line.product_id.name),
                        "qty": str("{0:8,.0f}".format(line.product_qty) if line.product_qty else 0),
                        "last_price": '',
                        "last_supp": '',
                        "last_order": '',
                    })

                # row.update({
                #     "no": str(vno),
                #     "nama_produk": str(line.product_id.name),
                #     "qty": str("{0:8,.0f}".format(line.product_qty) if line.product_qty else 0),
                #     "last_price": str("{0:8,.0f}".format(line.product_id.last_purchase_price) if line.product_id.last_purchase_price and line.product_id.seller_ids[0].min_qty>0 else ''),
                #     "last_supp": str(line.product_id.last_supplier_id.name if line.product_id.last_supplier_id.name and line.product_id.seller_ids[0].min_qty>0 else ''),
                #     "last_order": str(datetime.datetime.strptime(format(line.product_id.last_purchase_date), "%Y-%m-%d").strftime("%d-%b-%y") if line.product_id.last_purchase_date and line.product_id.seller_ids[0].min_qty>0 else ''),
                #     # "last_order": terakhir,
                # })
                for record in self.env['purchase.order'].sudo().search(
                    [('requisition_id', '=', rec.id)]):
                    no += 1
                    if no == 1:
                        # row.update({
                        #     "price_total1": '',
                        #     "price_total2": '',
                        # })
                        vendor1 = str(record.partner_id.name)
                        # pic1 = (" PIC: "+str(record.partner_id.child_ids[0].name) if record.partner_id.child_ids[0].name else '')+(" - "+str(record.partner_id.child_ids[0].phone) if record.partner_id.child_ids[0].phone else '' )
                        pic1 = (", pic: " + str(record.partner_id.child_ids[0].name)+(" - "+str(record.partner_id.child_ids[0].phone) if record.partner_id.child_ids[0].phone else '' ) if record.partner_id.child_ids else '' )
                        tv1 = str(record.payment_term_id.name if record.payment_term_id.name else '')
                        for isi_po in self.env['purchase.order.line'].search(
                                [('order_id', '=', record.id), ('product_id', '=', line.product_id.id)]):
                            if isi_po:
                                row.update({
                                    # "price_total1": str("{0:12,.2f}".format(isi_po.price_unit * isi_po.product_qty)),
                                    # "price_total1": str("{0:12,.0f}".format(isi_po.price_total)),
                                    "price_total1": str("{0:12,.0f}".format(isi_po.price_unit) if isi_po.product_qty>0 else ''),
                                })
                                if isi_po.taxes_id.ids:
                                    pajak1 = "Y"
                            else:
                                row.update({
                                    "price_total1": '',
                                    "price_total2": '',

                                })
                            # penjumlah1 += (isi_po.price_unit * isi_po.product_qty)
                            penjumlah1 += (isi_po.price_total if isi_po.product_qty>0 else 0)
                    if no == 2:
                        vendor2 = str(record.partner_id.name)
                        pic2 = (", pic: " + str(record.partner_id.child_ids[0].name)+(" - "+str(record.partner_id.child_ids[0].phone) if record.partner_id.child_ids[0].phone else '' ) if record.partner_id.child_ids else '' )
                        tv2 = str(record.payment_term_id.name if record.payment_term_id.name else '')
                        for isi_po in self.env['purchase.order.line'].search(
                                [('order_id', '=', record.id), ('product_id', '=', line.product_id.id)]):
                            if isi_po:
                                row.update({
                                    "price_total2": str("{0:12,.0f}".format(isi_po.price_unit) if isi_po.product_qty>0 else ''),
                                })
                                if isi_po.taxes_id.ids:
                                    pajak2 = "Y"
                            else:
                                row.update({
                                    "price_total2": '',
                                    "price_total3": '',
                                })
                            penjumlah2 += (isi_po.price_total if isi_po.product_qty>0 else 0)
                    if no == 3:
                        vendor3 = str(record.partner_id.name)
                        pic3 = (", pic: " + str(record.partner_id.child_ids[0].name)+(" - "+str(record.partner_id.child_ids[0].phone) if record.partner_id.child_ids[0].phone else '' ) if record.partner_id.child_ids else '' )
                        tv3 = str(record.payment_term_id.name if record.payment_term_id.name else '')
                        for isi_po in self.env['purchase.order.line'].search(
                                [('order_id', '=', record.id), ('product_id', '=', line.product_id.id)]):
                            if isi_po:
                                row.update({
                                    "price_total3": str("{0:12,.0f}".format(isi_po.price_unit) if isi_po.product_qty>0 else ''),
                                })
                                if isi_po.taxes_id.ids:
                                    pajak3 = "Y"
                            else:
                                row.update({
                                    "price_total3": '',
                                })
                            penjumlah3 += (isi_po.price_total if isi_po.product_qty>0 else 0)
                    if no == 1:
                        row.update({
                            "price_total2": '',
                            "price_total3": '',
                            })
                vno += 1
                items.append(row)
        murah = penjumlah1
        mahal = penjumlah1
        vendor_rekomemndasi = vendor1
        if murah > penjumlah2:
            if penjumlah2>0:
                murah = penjumlah2
                vendor_rekomemndasi = vendor2
        if murah > penjumlah3:
            if penjumlah3>0:
                murah = penjumlah3
                vendor_rekomemndasi = vendor3
        if mahal < penjumlah2:
            if penjumlah2>0:
                mahal:penjumlah2
        if mahal > penjumlah3:
            if penjumlah3>0:
                mahal:penjumlah3
        selisih = str("{0:12,.0f}".format(mahal - murah).replace(" ", "") if mahal - murah > 0 else '')
        if selisih != '':
            selisih = "-" + selisih
        else:
            selisih = "0"
        persen = str("{0:12,.0f}".format(((mahal - murah) / murah) * 100).replace(" ", "") if mahal - murah > 0 else '')
        if persen != '':
            persen = "-" + persen + "%"
        else:
            persen = "0%"
        data = {
            'vendor1': vendor1,
            'vendor2': vendor2,
            'vendor3': vendor3,
            'pic1': pic1,
            'pic2': pic2,
            'pic3': pic3,
            'jumlah1': str("{0:12,.0f}".format(penjumlah1) if penjumlah1>0 else ''),
            'jumlah2': str("{0:12,.0f}".format(penjumlah2) if penjumlah2>0 else ''),
            'jumlah3': str("{0:12,.0f}".format(penjumlah3) if penjumlah3>0 else ''),
            'ppn1': (pajak1 if vendor1 else ''),
            'ppn2': (pajak2 if vendor2 else ''),
            'ppn3': (pajak3 if vendor3 else ''),
            'qcf_no': str(rec.name),
            # 'qcf_date': str(rec.ordering_date),
            "qcf_date": str(datetime.datetime.strptime(format(rec.ordering_date), "%Y-%m-%d").strftime("%d-%b-%y") if rec.ordering_date else '' ),
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
            'name':name,
            'selisih':selisih,
            'persen':persen,
            'item':items,
        }
        return data

    @api.multi
    def print_report(self):
        self.ensure_one()
        datadir = os.path.dirname(__file__)
        # f = os.path.join(datadir, 'template/QCF-template.docx')
        context = self.get_data()
        murah = context['batas']
        nama = context['name']
        nama =nama.replace('/','')
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
                filename = ('/prn/' + nama + '.docx')
            else:
                filename = (nama + '.docx')
        else:
            if platform.system() == 'Linux':
                # filename = ('/tmp/QCF_' + str(datetime.today().date()) + '.docx')
                filename = ('/prn/' + nama + '.docx')
            else:
                filename = (nama + '.docx')
        template.save(filename)

        #custom miftah
        if self._context.get('pdf'):
            self.doc2pdf_linux(filename)
            filename = filename.replace('docx','pdf')
        #end of custom

        fp = open(filename, "rb")
        file_data = fp.read()
        out = base64.encodestring(file_data)

        attach_vals = {
            'purchase_requisition_data': filename.replace('/prn/',''),
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

    def doc2pdf_linux(self, doc):
        """
        convert a doc/docx document to pdf format (linux only, requires libreoffice)
        :param doc: path to document
        """
        cmd = 'libreoffice --convert-to pdf --outdir /prn'.split() + [doc]
        p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        p.wait(timeout=10)
        p.communicate()
