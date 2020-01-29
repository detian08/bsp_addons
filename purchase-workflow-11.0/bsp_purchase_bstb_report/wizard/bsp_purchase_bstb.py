import base64
import os
import platform
from datetime import datetime
from docxtpl import DocxTemplate
from odoo import api, fields, models, _
from odoo.exceptions import UserError

def fIsYaString(IsYa: bool()):
    if IsYa:
        return 'V'
    else:
        return '-'

class MaterialTransferBSTBReportOut(models.Model):
    _name = 'material.transfer.bstb.report.docx'
    _description = 'Material Transfer BSTB Report'

    material_transfer_bstb_data = fields.Binary('Docx Report', readonly=True)
    material_transfer_bstb_filename = fields.Char('Name', size=256)


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
            output_file = base64.encodestring(file_data)

            # attach_vals.append(
            #     {'material_transfer_bstb_data': filename,
            #      'file_name': out,})

            attach_vals = {
                'material_transfer_bstb_data': output_file,
                'material_transfer_bstb_filename': filename,
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


class InventoryTransferBSTBReportOut(models.Model):
    _name = 'inventory.transfer.bstb.report.docx'
    _description = 'Inventory Transfer BSTB Report'

    inventory_transfer_bstb_filename = fields.Char('Name', size=256)
    inventory_transfer_bstb_data = fields.Binary('Docx Report', readonly=True)


class WizardInventoryTransferBSTB(models.Model):
    _name = 'wizard.inventory.transfer.bstb.print'
    _description = "Inventory Transfer BSTB Print Wizard"


    @api.multi
    def get_data(self):
        self.ensure_one()
        picking = self.env['stock.picking'].browse(self._context.get('active_ids', list()))
        data = {}
        picking_singleton = picking.ensure_one()
        line_items = []
        nomor = 0
        for item in picking.move_line_ids:
            nomor += 1
            row = {'nomor': str(nomor),
                   'product_name': str(item.product_id.name),
                   'is_good': fIsYaString(not item.is_damage_line),
                   'is_bad': fIsYaString(item.is_damage_line),
                   'is_proper': fIsYaString(not item.is_not_match_line),
                   'is_not_proper': fIsYaString(item.is_not_match_line),
                   'qty_sent': str(int(item.qty_done))}
            line_items.append(row)
        po_pointer = self.sudo().env['purchase.order'].search([('name','=',picking.origin)])
        po_num = ''
        pr_num = ''
        vendor_name = ''
        if po_pointer:
            po_num = po_pointer[0].name
            pr_num = po_pointer[0].order_line[0].purchase_request_lines[0].request_id.name
            vendor_name = po_pointer[0].partner_id.name
        return_value = {
            'mt_no': str(picking.name),
            'no_po': str(po_num),
            'no_bppb': str(pr_num),
            'vendor_name': (vendor_name),
            'date_received': str(picking_singleton.date_done),
            'submit_name': '[Staff Purchasing]',
            'received_name': str(picking_singleton.receiving_employee.name),
            'received_dept': str(picking_singleton.receiving_dept.name),
            'waranty_val': 'n',
            'notes': '[catatan]',
            'items': line_items
        }
        return return_value

    @api.multi
    def print_report(self):
        datadir = os.path.dirname(__file__)
        #f = os.path.join(datadir, r'templates\permintaanbarangbon.docx')
        f = os.path.join(datadir, r'templates//template_bstb_isi.docx')
        template = DocxTemplate(f)
        context = self.get_data()
        if context:
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
                fileout = base64.encodestring(file_data)

                # attach_vals.append(
                #     {'material_transfer_bstb_data': filename,
                #      'file_name': out,})

                attach_vals = {
                    'inventory_transfer_bstb_filename': filename,
                    'inventory_transfer_bstb_data': fileout,
                }

                page_count += 1

                #- to do : menampilkan pop up windows dengan attachment beberapa file
                act_id = self.env['inventory.transfer.bstb.report.docx'].create(attach_vals)
                fp.close()
                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'inventory.transfer.bstb.report.docx',
                    'res_id': act_id.id,
                    'view_type': 'form',
                    'view_mode': 'form',
                    'context': self.env.context,
                    'target': 'new',
                }
        else:
            raise UserError('Data Kosong')
        

class PurchaseOrderServiceBSTBOutput(models.Model):
    _name = 'purchase.order.service.bstb.output'
    _description = 'Purchase Order Service - BSTB Report'

    po_service_bstb_filename = fields.Char('Name', size=256)
    po_service_bstb_data = fields.Binary('Docx Report', readonly=True)

class PurchaseOrderServiceBSTBWizard(models.Model):

    _name = 'purchase.order.service.bstb.wizard'
    _description = "Purchase Order Service BSTB Print Wizard"

    date_done = fields.Datetime(string='Date of Receive', readonly=False, )
    receiving_dept = fields.Many2one('hr.department', string='Departement Penerima')
    receiving_employee = fields.Many2one('hr.employee', string='Karyawan Penerima')

    @api.onchange('receiving_dept')
    def _filter_empl_by_dept(self):
        domain_val = {}
        if self.receiving_dept:
            # get list of employee
            list_of_employee = []
            list_of_employee = self.sudo().env['hr.employee'].search([('department_id','=',self.receiving_dept.id)]).ids
            if list_of_employee:
                domain_val = {'domain': {'receiving_employee': [('id', 'in', list_of_employee)]}}
                return domain_val

    @api.multi
    def get_data(self):
        self.ensure_one()
        po_data = self.env['purchase.order'].browse(self._context.get('active_ids', list())).ensure_one()
        data = {}
        line_items = []
        nomor = 0
        for item in po_data.order_line:
            nomor += 1
            row = {'nomor': str(nomor),
                   'product_name': str(item.product_id.name),
                   # 'is_good': fIsYaString(not item.is_damage_line),
                   'is_good': '',
                   'is_bad': '',
                   'is_proper': '',
                   'is_not_proper': '',
                   'qty_sent': str(int(item.product_qty))}
            line_items.append(row)
        # po_pointer = self.sudo().env['purchase.order'].search([('name','=',picking.origin)])
        po_num = ''
        if po_data:
            po_num = po_data[0].name

        pr_num = '-'
        try:
            pr_num = po_data[0].order_line[0].purchase_request_lines[0].request_id.name
        except:
            pr_num = '-'

        return_value = {
            'mt_no': '',
            'no_po': str(po_num),
            'no_bppb': str(pr_num),
            'vendor_name': '',
            'date_received': '',
            'submit_name': '[Staff Purchasing]',
            'received_name': str(self.receiving_employee.name),
            'received_dept': str(self.receiving_dept.name),
            'waranty_val': 'n',
            'notes': '[catatan]',
            'items': line_items
        }

        return return_value

    @api.multi
    def print_report(self):
        datadir = os.path.dirname(__file__)
        #f = os.path.join(datadir, r'templates\permintaanbarangbon.docx')
        f = os.path.join(datadir, r'templates//template_bstb_isi.docx')
        template = DocxTemplate(f)
        context = self.get_data()
        if context:
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
                fileout = base64.encodestring(file_data)

                # attach_vals.append(
                #     {'material_transfer_bstb_data': filename,
                #      'file_name': out,})

                attach_vals = {
                    'po_service_bstb_filename': filename,
                    'po_service_bstb_data': fileout,
                }

                page_count += 1

                #- to do : menampilkan pop up windows dengan attachment beberapa file
                act_id = self.env['purchase.order.service.bstb.output'].create(attach_vals)
                fp.close()
                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'purchase.order.service.bstb.output',
                    'res_id': act_id.id,
                    'view_type': 'form',
                    'view_mode': 'form',
                    'context': self.env.context,
                    'target': 'new',
                }
        else:
            raise UserError('Data Kosong')