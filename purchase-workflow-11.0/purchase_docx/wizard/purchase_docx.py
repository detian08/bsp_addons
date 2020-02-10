import base64
import platform
import os
import datetime
from datetime import  datetime
from docxtpl import DocxTemplate
from odoo import api, fields, models
from .PrintJob import print_job

def get_sample():
    return {
        "po_no": "PO/BSP-HC/10/09/2019/0003",
        "supplier": "TOKO ABC",
        "supplier_add": "Jl ABC no 123 Bandung 40112",
        "po_date": "10-10-2019",
        "bppb_no": "BPPB/BSP-HC/10/09/2019/0004",
        "arrival_date": "10-11-2019",
        "send_date": "12-10-2019",
        "fin_dir": "Drs Setiawan Tjahyadi",
        "purc_man": "Erni Sumarni, SE",
        "ref": "PR/BSP/IT/10/2019",
        "termofpayment": "Tempo 45 hari",
        "lamp": "2 lembar",
        "total_amount": 4400000,
        "down_payments": [
            {
                "dp_date": "13-10-2019",
                "dp_amount": 100000,
                "remark": "DP Pertama"
            },
            {
                "dp_date": "14-10-2019",
                "dp_amount": 200000,
                "remark": "DP Kedua"
            }
        ],
        "items": [
            {
                "no": "1",
                "product_name": "Monitor LCD 14",
                "product_qty": 5,
                "product_uom": "Unit",
                "price_unit": 500000,
                "price_total": 2500000
            },
            {
                "no": "2",
                "product_name": "Mouse wireless Logitech",
                "product_qty": 20,
                "product_uom": "Unit",
                "price_unit": 50000,
                "price_total": 1000000
            },
            {
                "no": "3",
                "product_name": "Keyboard 102 pad ext",
                "product_qty": 10,
                "product_uom": "Unit",
                "price_unit": 90000,
                "price_total": 900000
            }
        ]
    }

class PurchaseReportOut(models.Model):
    _name = 'purchase.report.docx'
    _description = 'purchase report'

    purchase_data = fields.Char('Name', size=256)
    file_name = fields.Binary('Purchase Docx Report', readonly=True)

    @api.multi
    def printWordDocument(self):
        pathfile = os.getcwd() + "\\" + self.purchase_data
        if platform.system() == 'Linux':
            pathfile = os.getcwd() + "//" + self.purchase_data
        print_job(pathfile)
        # if sys.platform == "win32":
        #     pythoncom.CoInitialize()
        #     path = os.getcwd() + "\\" + self.purchase_data
        #     word = client.Dispatch("Word.Application")
        #     word.Documents.Open(path)
        #     word.ActiveDocument.PrintOut()
        #     time.sleep(2)
        #     word.ActiveDocument.Close()
        #     word.Quit()
        # else:
        #     return 1




class WizardPurchase(models.Model):
    _name = 'wizard.purchase.print2'
    _description = "purchase print wizard"


    @api.multi
    def get_data(self):
        self.ensure_one()
        order = self.env['purchase.order'].browse(self._context.get('active_ids', list()))
        pph = 0
        for rec in order:
            items = []
            vno = 1
            penjumlah = 0
            for line in rec.order_line:
                # str_att = ''
                atts = []
                for att in line.product_id.attribute_line_ids:
                    att_values = ''
                    for val in att.value_ids:
                        att_values = ( att_values + ', ' + val.name ) if att_values != '' else  val.name
                    # str_att = (str_att + '\n\r' + att.attribute_id.name + ":" + att_values) if str_att != '' else ( att.attribute_id.name + ":" + att_values)
                    row = {
                        "att_name": att.attribute_id.name,
                        "att_val": att_values
                    }
                    atts.append(row)
                row = {
                    "no":str(vno),
                    "product_name": str(line.product_id.name) ,
                    # "attribute":str_att,
                    "attributes": atts,
                    "product_qty": str("{0:8,.2f}".format(line.product_qty)),
                    "product_uom":  str(line.product_uom.name),
                    "price_unit": str("{0:10,.2f}".format(line.price_unit)),
                    "price_total": str("{0:12,.2f}".format(line.price_unit * line.product_qty)),
                }
                penjumlah += (line.price_unit * line.product_qty)
                items.append(row)


                prs = []
                for prline in line.purchase_request_lines:
                    row = {
                        "bppb_no": str(prline.request_id.name)
                    }
                    if (row["bppb_no"] not in prs):
                        prs.append(row)
                vno += 1
            strPR = ''
            for v in prs:
                if strPR == '':
                    strPR = v['bppb_no']
                else:
                    strPR = strPR.trim() + ',' + v['bppb_no']
            down_payments = []
            vno = 1
            for dp in rec.advance_payment_ids:
                row = {
                    "no":str(vno),
                    "dp_date": (datetime.strptime(dp.payment_date,'%Y-%m-%d')).strftime('%d-%m-%Y') if dp.payment_date else '',
                    "dp_amount": str("{0:12,.2f}".format(dp.amount)),
                    "remark":  "Uang Muka ke: " + str(vno)
                }
                down_payments.append(row)
                vno += 1
            cpnya =''
            kon_total =''
            kon_cara =''
            kon_waktu =''
            kon_lok =''
            kon_fak =''
            if rec.partner_id.child_ids:
                cpnya = str(rec.partner_id.child_ids[0].name)
            if rec.total_pembelian:
                kon_total = str(rec.total_pembelian)
            if rec.cara_pembayaran:
                kon_cara = str(rec.cara_pembayaran)
            if rec.waktu_pelaksanaan:
                kon_waktu = str(rec.waktu_pelaksanaan)
            if rec.lokasi_pelaksanaan:
                kon_lok = str(rec.lokasi_pelaksanaan)
            if rec.faktur_an:
                kon_fak = str(rec.faktur_an)
            fin_dir = self.env['hr.employee'].search([('job_id.name', 'like', 'Finance Director')], limit=1)
            purchase_mgr = self.env['hr.employee'].search([('job_id.name', 'like', 'Purchase Manager')], limit=1)
            # pr_no = str(rec.order_line[0].purchase_request_lines[0].request_id.name if rec.order_line[0].purchase_request_lines[0].request_id.name else '')
            pr_no=''
            data = {
                "pr_no": str(pr_no),
                "po_no": str(rec.name),
                "supplier": str(rec.partner_id.name),
                "cp": cpnya,
                "supplier_add": str(rec.partner_id.street),
                "supplier_city": str(rec.partner_id.city)  if rec.partner_id.city else '',
                "supplier_zip": str(rec.partner_id.zip) if rec.partner_id.zip else '',
                "supplier_country": str(rec.partner_id.country_id.name)  if rec.partner_id.country_id else '',
                "supplier_pic_name":str(rec.partner_id.child_ids[0].name)  if rec.partner_id.child_ids else '',
                "po_date": (datetime.strptime(rec.date_order,'%Y-%m-%d %H:%M:%S')).strftime('%d-%m-%Y') if rec.date_order else '',
                "bppb_no": strPR,
                "arrival_date":  (datetime.strptime(rec.date_planned,'%Y-%m-%d %H:%M:%S')).strftime('%d-%m-%Y') if rec.date_planned else '',
                "send_date": (datetime.strptime(rec.date_approve,'%Y-%m-%d')).strftime('%d-%m-%Y') if rec.date_approve else '',
                "fin_dir": fin_dir.name if fin_dir else "",
                "purc_man": purchase_mgr.name if purchase_mgr else "",
                "ref": strPR,
                "termofpayment": str(rec.partner_id.property_supplier_payment_term_id.name if rec.partner_id.property_supplier_payment_term_id.name else ''),
                "lamp": "2 lembar",
                "total_untaxed": str("{0:12,.2f}".format(rec.amount_untaxed)),
                "total_tax": str("{0:12,.2f}".format(rec.amount_tax)),
                "total_amount": str("{0:12,.2f}".format(rec.amount_total)),
                "total_amount2": str("{0:12,.2f}".format(penjumlah)),
                "diskon": str("{0:12,.2f}".format(rec.general_discount*penjumlah/100)),
                "pph":pph,
                "total_pph": str("{0:12,.2f}".format(pph*penjumlah/100)),
                # "grand_amount": str("{0:12,.2f}".format(((1-rec.general_discount/100) * penjumlah) + rec.amount_tax +(pph*penjumlah/100))),
                "grand_amount": str("{0:12,.2f}".format(rec.amount_total) if rec.amount_total else '0'),
                "down_payments": down_payments,
                "kon_total": kon_total,
                "kon_cara": kon_cara,
                "kon_waktu": kon_waktu,
                "kon_lok": kon_lok,
                "kon_fak": kon_fak,
                'items': items
            }
        return data


    @api.multi
    def print_report(self):
        self.ensure_one()
        datadir = os.path.dirname(__file__)
        order = self.env['purchase.order'].browse(self._context.get('active_ids', list()))
        doctype = order.bsp_po_type
        # doctype = order.order_type
        doctype = str(doctype).upper()
        # doctype =''
        if platform.system() == 'LINUX':
            # if doctype == 'general':
            if doctype == 'GENERAL':
                doc_file = 'templates/suratpesanan_pp1.docx'
            else:
                doc_file = 'templates/suratpesanan_specific.docx'
        else:
            if doctype == 'GENERAL':
                doc_file = 'templates/suratpesanan_pp1.docx'
            else:
                doc_file = 'templates/suratpesanan_specific.docx'

        f = os.path.join(datadir, doc_file)
        template = DocxTemplate(f)
        context = self.get_data()
        # context = self.get_sample()
        template.render(context)
        filename = ('PurchaseRep-' + order.name + '__' +  str(datetime.today().date()) + '.docx')
        if platform.system() == 'Linux':
           filename = ('/tmp/PurchaseRep-' + order.name + '__' + str(datetime.today().date()) + '.docx')
        template.save(filename)
        fp = open(filename, "rb")
        file_data = fp.read()
        out = base64.encodestring(file_data)
        fp.close()
        attach_vals = {
            'purchase_data': filename,
            'file_name': out,
        }

        act_id = self.env['purchase.report.docx'].create(attach_vals)
        # print_job(filename) --> print to default printer

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.report.docx',
            'res_id': act_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            'context': self.env.context,
            'target': 'new',
        }