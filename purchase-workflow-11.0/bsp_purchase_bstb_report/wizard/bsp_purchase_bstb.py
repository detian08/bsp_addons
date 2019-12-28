import base64
import os
import platform
from datetime import datetime
from docxtpl import DocxTemplate
from odoo import api, fields, models, _


def fIsYaString(IsYa: bool()):
    if IsYa:
        return 'V'
    else:
        return '-'

class MaterialTransferBSTBReportOut(models.Model):
    _name = 'material.transfer.bstb.report.docx'
    _description = 'Material Transfer BSTB Report'

    material_transfer_bstb_data = fields.Char('Name', size=256)
    file_name = fields.Binary('Docx Report', readonly=True)


class WizardSMaterialTransferBSTB(models.Model):
    _name = 'wizard.material.transfer.bstb.print'
    _description = "Material Transfer BSTB Print Wizard"

    @api.multi
    def get_data(self):
        self.ensure_one()
        order = self.env['material.transfer'].browse(self._context.get('active_ids', list()))
        for rec in order:
            items = []
            no = 0
            for line in rec.line_ids:
                no += 1
                row = {'nomor': str(no),
                       'product_name': str(line.product_id.name),
                       'is_good': fIsYaString(not line.is_damage),
                       'is_bad': fIsYaString(line.is_damage),
                       'is_proper': fIsYaString(not line.is_not_match),
                       'is_not_proper': fIsYaString(line.is_not_match),
                       'qty_sent': str(int(line.product_qty))}
                items.append(row)

            data = {
                'mt_no': str(rec.name),
                'no_po': str(rec.order_id.name),
                'no_bppb': str(rec.request_id.name),
                'vendor_name': (rec.order_id.partner_id.name),
                'date_received': str(rec.transfer_date),
                'submit_name': '[Staff Purchasing]',
                'received_name': '[Penerima]',
                'received_dept': '[Departemen]',
                'waranty_val': 'n',
                'notes': '[catatan]',
                'items': items
            }
        return data

    @api.multi
    def print_report(self):
        datadir = os.path.dirname(__file__)
        #f = os.path.join(datadir, r'templates\permintaanbarangbon.docx')
        f = os.path.join(datadir, r'templates//template_bstb_isi.docx')
        template = DocxTemplate(f)
        context = self.get_data()

        #-- Pagination, jika item lebih dari 5
        # Get number of item and page
        num_items = context['items'].__len__()
        divmod_retval = divmod(num_items, 5)
        num_pages = divmod_retval[0]
        if divmod_retval[1] != 0 :
            num_pages += 1

        #- Start Printing
        # attach_vals = []
        page_count = 1
        idx = 0
        while page_count <= num_pages:
            output_data = None
            item_data = None

            output_data = {
                'mt_no': context['mt_no'],
                'no_po': context['no_po'],
                'no_bppb': context['no_bppb'],
                'vendor_name': context['vendor_name'],
                'date_received': context['date_received'],
                'submit_name': context['submit_name'],
                'received_name': context['received_name'],
                'received_dept': context['received_dept'],
                'waranty_val': context['waranty_val'],
                'notes': context['notes'],
                'items': []
            }

            curr_page = 5 * page_count
            max_idx = curr_page - 1
            while (idx <= max_idx) and (idx < num_items):
                item_data = {
                    'nomor': context['items'][idx]['nomor'],
                    'product_name': context['items'][idx]['product_name'],
                    'is_good': context['items'][idx]['is_good'],
                    'is_bad': context['items'][idx]['is_bad'],
                    'is_proper': context['items'][idx]['is_proper'],
                    'is_not_proper': context['items'][idx]['is_not_proper'],
                    'qty_sent': context['items'][idx]['qty_sent']
                }
                output_data['items'].append(item_data)
                idx += 1

            # # Masukin dummy row supaya ke bawah pas 5 baris
            x = 5 - len(output_data['items'])
            if x > 0 :
                for i in range(x):
                    row = {'nomor': '',
                           'product_name': '',
                           'is_good': '',
                           'is_bad': '',
                           'is_proper': '',
                           'is_not_proper': '',
                           'qty_sent': ''}
                    output_data['items'].append(row)

            #- Save to file
            mat_transfer_no = context.get('mt_no', '') + '-' + str(datetime.today().date())
            if num_pages > 1:
                mat_transfer_no += '-pg' + str(page_count)
            mat_transfer_no = str(mat_transfer_no.replace("/", ""))
            if platform.system() == 'Linux':
                filename = (r'/tmp/BSTB-' + mat_transfer_no + '.docx')
            else:
                filename = ('BSTB-' + mat_transfer_no + '.docx')

            template.render(output_data)
            template.save(filename)
            fp = open(filename, "rb")
            file_data = fp.read()
            out = base64.encodestring(file_data)

            # attach_vals.append(
            #     {'material_transfer_bstb_data': filename,
            #      'file_name': out,})

            attach_vals = {
                'material_transfer_bstb_data': filename,
                'file_name': out,
            }

            page_count += 1

            #- to do : menampilkan pop up windows dengan attachment beberapa file
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

