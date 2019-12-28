import base64
import os
import datetime
import platform
from datetime import datetime
from docxtpl import DocxTemplate
from odoo import api, fields, models
from num2words import num2words
import re


class SPPOutputDocx(models.Model):
    _name = 'spp.output.docx'
    spb_file_name = fields.Char('SPB Filename', size=256)
    spb_file_data = fields.Binary('SPB Data', readonly=True)


class SPPOutputWizard(models.Model):
    _name = 'spp.output.wizard'
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
        spb = self.env['spp'].browse(self._context.get('active_ids', list()))
        # AmountText = self.env['terbilang']
        list_of_spb = []
        for rec in spb:
            self.spb_name = rec.name
            items = []
            totaldetail = 0
            line_no = 1
            for line in rec.spp_line_ids:
                amount_item_text = 0
                if rec.currency_id.name == 'IDR':
                    amount_item_text = int(line.amount_payment)
                    amount_item_text = rec.currency_id.name + '.' + str(amount_item_text)
                else:
                    amount_item_text = rec.currency_id.name + '.' + str(line.amount_payment)
                row = {
                    'name': str(line.purchaseorder_id.name),
                    'amount': amount_item_text
                }
                items.append(row)
            amount_value_text = ''
            amount_value_num = 0
            if rec.currency_id.name == 'IDR':
                amount_value_num = int(rec.amount_payment_total)
                amount_value_text = rec.currency_id.name + '.' + str(amount_value_num)
            else:
                amount_value_text = rec.currency_id.name + '.' + str(rec.amount_payment_total)
            amount_value_words = ''
            if rec.company_id.currency_id.name == 'IDR':
                amount_value_words = num2words(amount_value_num, lang='id', to='currency')
            else:
                amount_value_words = num2words(amount_value_num, lang='en', to='currency')
            memo_value = str.splitlines(rec.memo)
            # memo_value = re.sub(r'\n','\\n',memo_value)
            data = {
                'name': str(rec.name),
                'assigned_to': str(rec.up_value),
                'doc_date': str(rec.request_date),
                # 'payment_purpose': str(rec.memo),
                'payment_purpose': memo_value,
                'company_id': str(rec.company_id),
                'currency_id': str(rec.currency_id),
                'supplier_id': str(rec.partner_id),
                'supplier_name': str(rec.partner_id.name),
                # 'amount_value':str(rec.amount_value),
                'amount_value': amount_value_text,
                'amount_words': str(amount_value_words),
                'payment_dest_supplier_name': str(rec.partner_id.name),
                'payment_dest_bank_acc_name': str(rec.payment_dest_bank_acc_name),
                'payment_dest_bank_acc_no': str(rec.payment_dest_bank_acc_no),
                'payment_dest_bank_name': str(rec.payment_dest_bank_name),
                'payment_dest_bank_branch_name': str(rec.payment_dest_bank_branch_name),
                'payment_dest_bank_branch_address': str(rec.payment_dest_bank_branch_address),
                'acknowledged_by1': str(rec.acknowledged_1.name),
                'acknowledged_by2': str(rec.assigned_to.name),
                'items': items,
                'page_break': '\f',
                'newline':'\n'
            }
            list_of_spb.append(data)

        retval = {
            'list_of_spb': list_of_spb
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
            filename = ('/tmp/SPP-' + self.spb_name + '-' + str(datetime.today().date()) + '.docx')
        else:
            filename = ('SPP-' + self.spb_name + '-' + str(datetime.today().date()) + '.docx')
        template.save(filename)
        fp = open(filename, 'rb')
        file_data = fp.read()
        out = base64.encodestring(file_data)

        attach_vals = {
            'spb_file_name': filename,
            'spb_file_data': out,
        }

        act_id = self.env['spp.output.docx'].create(attach_vals)
        fp.close()

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'spp.output.docx',
            'res_id': act_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            'context': self.env.context,
            'target': 'new',
        }
