import base64
import os
import datetime
from datetime import datetime
from docxtpl import DocxTemplate
from odoo import api, fields, models
import platform
from zipfile import ZipFile

if platform.system() == 'Windows':  # sys.platform == 'win32':
    import win32api
    import win32print
elif platform.system() == 'Linux':
    import subprocess
else:
    raise Exception("Sorry: no implementation for your platform ('%s') available" % platform.system())


class TedK1DocxSingle(models.Model):
    _name = 'purchase.request.docx.k1single'
    _description = 'Purchase Request K-1 Docx File Class'

    filename = fields.Char('Name', size=256)
    filedata = fields.Binary('Docx Report', readonly=True)


class Tedk1DocxWizard(models.Model):
    _name = 'purchase.request.docx.k1wizard'
    _description = "purchase request K-1 print wizard"

    @api.multi
    def get_data(self):
        self.ensure_one()
        selected_orders = self.env['purchase.request'].browse(self._context.get('active_ids', list()))
        return_value = []
        for order in selected_orders:
            #         hitung jumlah item
            num_items = order.line_ids.__len__()
            #
            # # num_pages = num_items div
            divmod_retval = divmod(num_items, 10)  # max 5 item in 1 pages
            num_pages = 0
            if divmod_retval[1] == 0:
                num_pages = divmod_retval[0]
                if num_pages == 0:
                    num_pages = 1
            else:
                num_pages = divmod_retval[0] + 1
            page_count = 1
            idx = 0
            items = []
            item_counter = 0
            while page_count <= num_pages:
                print_data = {}
                print_data_item = []
                # {{k1_no}}
                k1_no = order.name
                # {{k1_plate}}
                k1_plate = order.vehicle_id.license_plate
                # {{r2}}
                r2 = '-'
                # {{r4}}
                r4 = 'V'
                # {{k1_last_odo}}
                k1_last_odo = order.vehicle_last_odometer
                # {{k1_vehicle_name}}
                k1_vehicle_name = order.vehicle_id.name
                # {{k1_vehicle_type}}
                k1_vehicle_type = order.vehicle_id.model_id.name
                # {{k1_vehicle_year}}
                k1_vehicle_year = order.vehicle_id.model_year
                # {{e}}
                e = '-'
                # {{v}}
                v = '-'
                # {{c}}
                c = '-'
                if order.vehicle_repair_status == 'notyet':
                    ny = 'V'
                    ip = ''
                    fin = ''
                elif order.vehicle_repair_status == 'inservice':
                    ip = 'V'
                    ny=''
                    fin = ''
                elif order.vehicle_repair_status == 'already':
                    fin = 'V'
                    ny= ''
                    ip = ''
                print_data = {
                    'k1_no': k1_no,
                    'k1_plate': k1_plate,
                    'r2': r2,
                    'r4': r4,
                    'k1_last_odo': k1_last_odo,
                    'k1_vehicle_name': k1_vehicle_name,
                    'e': e,
                    'v': v,
                    'c': c,
                    'ny':ny,
                    'ip':ip,
                    'fin':fin,
                    'supplier1_total': 0,
                    'supplier2_total': 0,
                    'items': items,
                }
                max_idx = (10 * page_count) - 1
                supplier1_total = 0
                supplier2_total = 0
                while idx <= max_idx and idx < num_items:
                    item_counter += 1
                    product_name = order.line_ids[idx].name
                    prod_qty = order.line_ids[idx].product_qty
                    prod_uom = order.line_ids[idx].product_uom_id.name
                    if order.line_ids[idx].last_service:
                        last_consume = order.line_ids[idx].last_service
                    else:
                        last_consume = '-'
                    supplier1_price = order.line_ids[idx].estimated_cost2
                    supplier1_total = supplier1_total + supplier1_price
                    supplier2_price = order.line_ids[idx].estimated_cost3
                    supplier2_total = supplier2_total + supplier2_price

                    item_data = {
                        'nomor': item_counter,
                        'product_name': product_name,
                        'prod_qty': prod_qty,
                        'prod_uom': prod_uom,
                        'last_consume': last_consume,
                        'supplier1_price': supplier1_price,
                        'supplier2_price': supplier2_price
                    }
                    print_data['items'].append(item_data)
                    idx += 1
                if not supplier1_total:
                    supplier1_total = 0

                if not supplier2_total:
                    supplier2_total = 0

                print_data['supplier1_total'] = supplier1_total
                print_data['supplier2_total'] = supplier2_total
                return_value.append(print_data)
                page_count += 1
                return return_value
            else:
                return {}

    @api.multi
    def get_result(self):
        # get data
        self.ensure_one()
        print_data = self.get_data()
        if print_data:
            counter_page = 1
            list_file_result = []
            for single_print_data in print_data:
                # inisialisasi
                file_name = ""
                file_content = single_print_data
                template = None

                file_template = os.path.join(os.path.dirname(__file__), r'templates/k1_template.docx')
                template_object = DocxTemplate(file_template)

                file_name = ('/tmp/test' + str(datetime.today().date()) + 'page' + str(counter_page) + '.docx')
                template_object.render(file_content)
                template_object.save(file_name)
                list_file_result.append(file_name)

            zipfilename = str('/tmp/k1_docx_zipped' + str(datetime.today().timestamp()) + '.zip')

            with ZipFile(zipfilename, 'w') as zipfile:
                for file in list_file_result:
                    print(file)
                    zipfile.write(file)
            fp = open(zipfile.filename, "rb")
            file_data = fp.read()
            out = base64.encodestring(file_data)
            print_data_file = {
                'filename': zipfile.filename,
                'filedata': out
            }
            header_object = self.env['purchase.request.docx.k1single'].create(print_data_file)
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.request.docx.k1single',
                'res_id': header_object.id,
                'view_type': 'form',
                'view_mode': 'form',
                'context': self.env.context,
                'target': 'new',
            }
        else:
            return {
            }
