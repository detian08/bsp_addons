import base64
import datetime
import os
import platform
from num2words import num2words
from datetime import datetime
from docxtpl import DocxTemplate
from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT

class TedSPBOutputDocx(models.Model):
    _name = 'ted.spb.output.docx'
    _description = 'Output SPB - Docx'

    spb_file_name = fields.Char('SPB Filename', size=256)
    spb_file_data = fields.Binary('SPB Data', readonly=True)


class TedSPBOutputWizard(models.Model):
    _name = 'ted.spb.output.wizard'
    _description = 'Output SPB - Wizard'

    spb_name = fields.Char(string='Nomor Register')

    @api.multi
    def _get_selection_value(self, model, field, value):
        selection = self.pool.get(model)._columns.get(field).selection
        val = ''
        for v in selection:
            if v[0] == value:
                val = v[1]
            break
        return val

    @api.multi
    def get_data(self):
        self.ensure_one()
        spb = self.env['ted.surat.permohonan.bayar'].browse(self._context.get('active_ids', list()))
        # AmountText = self.env['terbilang']
        list_of_spb = []
        for rec in spb:
            self.spb_name = rec.name
            items = []
            totaldetail = 0
            line_no = 1
            for line in rec.line_ids:
                amount_item_text = 0
                if rec.currency_id.name == 'IDR':
                    amount_item_text = int(line.spb_line_amount)
                    amount_item_text = rec.currency_id.name + '.' + str(amount_item_text)
                else:
                    amount_item_text = rec.currency_id.name + '.' + str(line.spb_line_amount)
                row = {
                    'name':str(line.purchase_order_name),
                    'amount':amount_item_text
                }
                items.append(row)
            amount_value_text = ''
            amount_value_num = 0
            if rec.currency_id.name == 'IDR':
                amount_value_num = int(rec.amount_value)
                amount_value_text = rec.currency_id.name +'.'+ str(amount_value_num)
            else:
                amount_value_text = rec.currency_id.name + '.' + str(rec.amount_value)
            data = {
                'name': str(rec.name),
                'assigned_to':str(rec.assigned_to),
                'doc_date':str(rec.doc_date),
                'payment_purpose':str(rec.payment_purpose),
                'company_id':str(rec.company_id),
                'currency_id':str(rec.currency_id),
                'supplier_id':str(rec.supplier_id),
                'supplier_name':str(rec.supplier_name),
                # 'amount_value':str(rec.amount_value),
                'amount_value':amount_value_text,
                'amount_words':str(rec.amount_words_disp),
                'payment_dest_supplier_name':str(rec.payment_dest_supplier_name),
                'payment_dest_bank_acc_name':str(rec.payment_dest_bank_acc_name),
                'payment_dest_bank_acc_no':str(rec.payment_dest_bank_acc_no),
                'payment_dest_bank_name':str(rec.payment_dest_bank_name),
                'payment_dest_bank_branch_name':str(rec.payment_dest_bank_branch_name),
                'payment_dest_bank_branch_address':str(rec.payment_dest_bank_branch_address),
                'acknowledged_by1':str(rec.acknowledged_by1.name),
                'acknowledged_by2':str(rec.acknowledged_by2.name),
                'items': items,
                'page_break': r'\f',
            }
            list_of_spb.append(data)

        retval = {
            'list_of_spb':list_of_spb
        }
        return retval

    @api.multi
    def print_report(self):
        self.ensure_one()
        datadir = os.path.dirname(__file__)
        if platform.system() == 'Linux':
            f = os.path.join(datadir, r'templates/template_spb.docx')
        else:
            f = os.path.join(datadir, r'templates\template_spb.docx')
        template = DocxTemplate(f)
        context = self.get_data()
        template.render(context)
        if platform.system() == 'Linux':
            filename = ('/tmp/BSPSPB-'+ self.spb_name + '-' + str(datetime.today().date()) + '.docx')
        else:
            filename = ('BSPSPB-' + self.spb_name + '-' + str(datetime.today().date()) + '.docx')
        template.save(filename)
        fp = open(filename, 'rb')
        file_data = fp.read()
        out = base64.encodestring(file_data)

        attach_vals = {
            'spb_file_name': filename,
            'spb_file_data': out,
        }

        act_id = self.env['ted.spb.output.docx'].create(attach_vals)
        fp.close()

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ted.spb.output.docx',
            'res_id': act_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            'context': self.env.context,
            'target': 'new',
        }

