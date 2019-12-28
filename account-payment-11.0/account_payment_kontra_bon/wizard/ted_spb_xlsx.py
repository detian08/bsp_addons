import base64
import os
import datetime
from datetime import datetime, date
from docxtpl import DocxTemplate
from odoo import api, fields, models
import platform
from zipfile import ZipFile
import xlwt
from num2words import num2words


style_bold = xlwt.easyxf('font: name Trebuchet MS bold on;', num_format_str='#.##0,00')
style_normal = xlwt.easyxf('font:name Trebuchet MS ;', num_format_str='#.##0,00')

class TedSPBWizardDriver(models.Model):
    _name = 'ted.spb.wizard.output'
    _description = 'xlsx output file SPB'

    output_filename = fields.Char('Name', size=256)
    output_filedata = fields.Binary('SPB Data', readonly=True)

class TedSPBWizardDriver(models.Model):
    _name = 'ted.spb.wizard.driver'
    _description = 'wizard output SPB'

    date_start = fields.Date(string="Start Date", required=True, default=fields.Date.today)
    date_end = fields.Date(string="End Date", required=True, default=fields.Date.today)

    @api.multi
    def action_spb_output_handler(self):
        retval = {}
        list_of_spb = self.env['kontra.bon'].browse(self._context.get('active_ids', list()))
        row_odd_start = 2
        row_odd_end   = 3
        col_odd_start = 2
        col_odd_end   = 5

        col_even_start = 7
        col_even_end   = 10

        row_pivot = 0
        col_pivot = 0


        if list_of_spb:
            counter = 0
            workbook = xlwt.Workbook()
            sheet = workbook.add_sheet('spb', cell_overwrite_ok=True)
            for spb in list_of_spb:
                counter += 1
                divmod_res = divmod(counter, 2)
                source_doc_id = spb.id
                name = spb.name
                assigned_to = spb.partner_id.name
                doc_date = spb.date_doc
                payment_purpose = spb.memo
                supplier_id = spb.partner_id
                supplier_name = spb.partner_id.name
                amount_value = spb.amount_payment_total
                # amount_words = spb.amount_words
                if spb.currency_id.name == 'IDR':
                    amount_words = num2words(int(amount_value), lang='id',to='currency')
                else:
                    amount_words = num2words(amount_value, lang='en',to='currency')
                payment_dest_supplier_name = payment_dest_bank_acc_name = ''
                payment_dest_bank_acc_no = payment_dest_bank_name = ''
                payment_dest_bank_branch_name = ''
                payment_dest_bank_branch_address = ''
                if spb.partner_id.bank_ids and spb.partner_id.bank_ids[0]:
                    payment_dest_bank_acc_name = spb.partner_id.bank_ids[0].bank_account_name
                    payment_dest_bank_acc_no = spb.partner_id.bank_ids[0].acc_number
                    payment_dest_bank_name = spb.partner_id.bank_ids[0].bank_name
                    payment_dest_bank_branch_name = spb.partner_id.bank_ids[0].bank_branch_name
                    payment_dest_bank_branch_address = spb.partner_id.bank_ids[0].bank_branch_addr1
                acknowledged_by1 = spb.assigned_to.name
                acknowledged_by2 = 'Marthien P., S.Si., Apt.'


                excel_data = {'source_doc_id':source_doc_id,
                              'name': name,
                              'assigned_to':assigned_to,
                              'doc_date': doc_date,
                              'payment_purpose': payment_purpose,
                              'supplier_id': supplier_id,
                              'supplier_name': supplier_name,
                              'amount_value': amount_value,
                              'amount_words': amount_words,
                              'payment_dest_supplier_name': payment_dest_supplier_name,
                              'payment_dest_bank_acc_name': payment_dest_bank_acc_name,
                              'payment_dest_bank_acc_no': payment_dest_bank_acc_no,
                              'payment_dest_bank_name': payment_dest_bank_name,
                              'payment_dest_bank_branch_name': payment_dest_bank_branch_name,
                              'payment_dest_bank_branch_address': payment_dest_bank_branch_address,
                              'acknowleded_by1': acknowledged_by1,
                              'acknowleded_by2': acknowledged_by2,
                              }

                row_odd_start = (25 * (counter - 1)) + 2
                row_odd_end = (25 * (counter - 1)) + 3

                col_odd_start = 2
                col_odd_end = 5
                col_even_start = 7
                col_even_end = 10
                if divmod_res[1] == 1:
                #     handle ganjil
                    sheet.write_merge(row_odd_start, row_odd_end, col_odd_start, col_odd_end, 'Permohonan Pembayaran')
                # No.Register
                    row_odd_start += 1
                    col_odd_start = 2
                    col_odd_end = 4
                    sheet.write(row_odd_start, col_odd_start, 'No. Register')
                    sheet.write(row_odd_start, col_odd_end, name)
                # UP
                    row_odd_start += 1
                    sheet.write(row_odd_start, col_odd_start, 'UP')
                    sheet.write(row_odd_start, col_odd_end, assigned_to)
                # Tanggal
                    row_odd_start += 1
                    sheet.write(row_odd_start, col_odd_start, 'Tanggal')
                    sheet.write(row_odd_start, col_odd_end, doc_date)
                # Untuk Pembayaran
                    row_odd_start += 1
                    sheet.write(row_odd_start, col_odd_start, 'Untuk Pembayaran')
                    source_text = payment_purpose
                    if source_text:
                        clustered_text = []
                        cluster_num = 4
                        if divmod(len(source_text),cluster_num) == 0:
                            max_words = divmod(len(source_text),cluster_num)[0]
                        else:
                            max_words = divmod(len(source_text),cluster_num)[0] + 1
                        cluster_count = 1
                        idx_iterator = 0
                        while cluster_count <= cluster_num:
                            idx_start = cluster_count * max_words - max_words
                            if cluster_count < cluster_num:
                                idx_end = cluster_count * max_words - 1
                            else:
                                idx_end = len(source_text) - 1
                            idx_iterator = idx_start
                            current_text = ''
                            while idx_iterator <= idx_end:
                                current_text += ' ' + source_text[idx_iterator]
                                idx_iterator += 1
                            clustered_text.append(current_text)
                            cluster_count += 1
                        if clustered_text[0]:
                            sheet.write(row_odd_start, col_odd_end, clustered_text[0])
                    #
                        row_odd_start += 1  #blank space
                        if clustered_text[0]:
                            sheet.write(row_odd_start, col_odd_end, clustered_text[1])

                        row_odd_start += 1  #blank space
                        if clustered_text[0]:
                            sheet.write(row_odd_start, col_odd_end, clustered_text[2])
                        row_odd_start += 1  #blank space
                        if clustered_text[0]:
                            sheet.write(row_odd_start, col_odd_end, clustered_text[3])
                # Kepada
                    row_odd_start += 1
                    sheet.write(row_odd_start, col_odd_start, 'Kepada')
                    sheet.write(row_odd_start, col_odd_end, payment_dest_supplier_name)
                # Sebesar
                    row_odd_start += 1
                    sheet.write(row_odd_start, col_odd_start, 'Sebesar')
                    sheet.write(row_odd_start, col_odd_end, amount_value)
                # Terbilang
                    row_odd_start += 1
                    sheet.write(row_odd_start, col_odd_start, 'Terbilang')
                    sheet.write(row_odd_start, col_odd_end, amount_words)
                # Pembayaran ke
                    row_odd_start += 1
                    sheet.write(row_odd_start, col_odd_start, 'Pembayaran ke')
                    sheet.write(row_odd_start, col_odd_end, payment_dest_supplier_name)
                #
                    row_odd_start += 1  #blank space
                    sheet.write(row_odd_start, col_odd_end, payment_dest_bank_acc_name)

                    row_odd_start += 1  #blank space
                    sheet.write(row_odd_start, col_odd_end, payment_dest_bank_acc_no)
                    row_odd_start += 1  #blank space
                    bank_val = str(payment_dest_bank_name) + ' cabang ' + str(payment_dest_bank_branch_name)
                    sheet.write(row_odd_start, col_odd_end, bank_val)

                # Hormat kami,
                    row_odd_start += 1
                    sheet.write(row_odd_start, col_odd_start, 'Hormat kami,')
                    sheet.write(row_odd_start, col_odd_end, 'Mengetahui,')
                #
                    row_odd_start += 1  #blank space
                    row_odd_start += 1  #blank space
                    row_odd_start += 1  #blank space

                # Dian Sri M.
                    row_odd_start += 1
                    sheet.write(row_odd_start, col_odd_start, acknowledged_by1)
                    sheet.write(row_odd_start, col_odd_end, acknowledged_by2)
                else:
                #     handle even
                    sheet.write_merge(row_odd_start, row_odd_end, col_even_start, col_even_end, 'Permohonan Pembayaran')
                    row_pivot = row_odd_start
                # No.Register
                    row_odd_start += 1
                    col_even_start = 7
                    col_even_end = 9
                    sheet.write(row_odd_start, col_even_start, 'No. Register')
                    sheet.write(row_odd_start, col_even_start + 1, ':')
                    sheet.write(row_odd_start, col_even_end, name)
                # UP
                    row_odd_start += 1
                    sheet.write(row_odd_start, col_even_start, 'UP')
                    sheet.write(row_odd_start, col_even_end, assigned_to)
                # Tanggal
                    row_odd_start += 1
                    sheet.write(row_odd_start, col_even_start, 'Tanggal')
                    sheet.write(row_odd_start, col_even_end, doc_date)
                # Untuk Pembayaran
                    row_odd_start += 1
                    sheet.write(row_odd_start, col_even_start, 'Untuk Pembayaran')
                    source_text = payment_purpose
                    if source_text:
                        clustered_text = []
                        cluster_num = 4
                        if divmod(len(source_text),cluster_num) == 0:
                            max_words = divmod(len(source_text),cluster_num)[0]
                        else:
                            max_words = divmod(len(source_text),cluster_num)[0] + 1
                        cluster_count = 1
                        idx_iterator = 0
                        while cluster_count <= cluster_num:
                            idx_start = cluster_count * max_words - max_words
                            if cluster_count < cluster_num:
                                idx_end = cluster_count * max_words - 1
                            else:
                                idx_end = len(source_text) - 1
                            idx_iterator = idx_start
                            current_text = ''
                            while idx_iterator <= idx_end:
                                current_text += ' ' + source_text[idx_iterator]
                                idx_iterator += 1
                            clustered_text.append(current_text)
                            cluster_count += 1
                        if clustered_text[0]:
                            sheet.write(row_odd_start, col_even_end, clustered_text[0])
                    #
                        row_odd_start += 1  #blank space
                        if clustered_text[0]:
                            sheet.write(row_odd_start, col_even_end, clustered_text[1])

                        row_odd_start += 1  #blank space
                        if clustered_text[0]:
                            sheet.write(row_odd_start, col_even_end, clustered_text[2])
                        row_odd_start += 1  #blank space
                        if clustered_text[0]:
                            sheet.write(row_odd_start, col_even_end, clustered_text[3])
                # Kepada
                    row_odd_start += 1
                    sheet.write(row_odd_start, col_even_start, 'Kepada')
                    sheet.write(row_odd_start, col_even_end, payment_dest_supplier_name)
                # Sebesar
                    row_odd_start += 1
                    sheet.write(row_odd_start, col_even_start, 'Sebesar')
                    sheet.write(row_odd_start, col_even_end, amount_value)
                # Terbilang
                    row_odd_start += 1
                    sheet.write(row_odd_start, col_even_start, 'Terbilang')
                    sheet.write(row_odd_start, col_even_end, amount_words)
                # Pembayaran ke
                    row_odd_start += 1
                    sheet.write(row_odd_start, col_even_start, 'Pembayaran ke')
                    sheet.write(row_odd_start, col_even_end, payment_dest_supplier_name)
                #
                    row_odd_start += 1  #blank space
                    sheet.write(row_odd_start, col_even_end, payment_dest_bank_acc_name)

                    row_odd_start += 1  #blank space
                    sheet.write(row_odd_start, col_even_end, payment_dest_bank_acc_no)
                    row_odd_start += 1  #blank space
                    bank_val = payment_dest_bank_name + ' cabang ' + payment_dest_bank_branch_name
                    sheet.write(row_odd_start, col_even_end, bank_val)

                # Hormat kami,
                    row_odd_start += 1
                    sheet.write(row_odd_start, col_even_start, 'Hormat kami,')
                    sheet.write(row_odd_start, col_even_end, 'Mengetahui,')
                #
                    row_odd_start += 1  #blank space
                    row_odd_start += 1  #blank space
                    row_odd_start += 1  #blank space

                # Dian Sri M.
                    row_odd_start += 1
                    sheet.write(row_odd_start, col_even_start, acknowledged_by1)
                    sheet.write(row_odd_start, col_even_end, acknowledged_by2)
            
            
            if platform.system() == 'Linux':
                output_filename = ('/tmp/SPB-'+ str(self[0].id)+ '-' + str(datetime.today().date()) + '.xlsx')
            else:
                output_filename = ('SPB-'+ str(self[0].id) + '-' + str(datetime.today().date()) + '.xlsx')
            
            workbook.save(output_filename)
            file_handler = open(output_filename,"rb")
            file_data = file_handler.read()
            output_filedata = base64.encodestring(file_data)
            attach_value = {
                'output_filename':  output_filename,
                'output_filedata':  output_filedata
            }
            output = self.env['ted.spb.wizard.output'].create(attach_value)
            retval = {
            'type': 'ir.actions.act_window',
            'res_model': 'ted.spb.wizard.output',
            'res_id': output.id,
            'view_type': 'form',
            'view_mode': 'form',
            'context': self.env.context,
            'target': 'new',
            }
            return retval
        else:
            return retval