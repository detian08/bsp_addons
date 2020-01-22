import base64
import os
import datetime
from datetime import datetime
from docxtpl import DocxTemplate
from odoo import api, fields, models
import platform
import random
from zipfile import ZipFile

if platform.system() == 'Windows':  # sys.platform == 'win32':
    import win32api
    import win32print
elif platform.system() == 'Linux':
    import subprocess
else:
    raise Exception("Sorry: no implementation for your platform ('%s') available" % platform.system())


class TedK1DocxMulti(models.Model):
    _name = 'test.output.docx.k1multi'
    _description = 'Purchase Request K-1 Docx File Class'

    filename = fields.Char('Name', size=256)
    filedata = fields.Binary('Docx Report in zip file', readonly=True)


class Tedk1DocxWizard(models.Model):
    _name = 'test.output.docx.k1wizard'
    _description = "purchase request K-1 print wizard"

    @api.multi
    def get_result(self):
        self.ensure_one()
        max_count = random.randint(50, 101)
        counter = 0
        return_value = []
        num_items = max_count
        divmod_retval = divmod(num_items, 10)  # max 10 item in 1 pages
        num_pages = 0
        if divmod_retval[1] == 0:
            num_pages = divmod_retval[0]
        else:
            num_pages = divmod_retval[0] + 1
        page_count = 1
        item_index = 0

        # create zip file
        zipfilename = str('k1_docx_zipped' + str(datetime.today().date()) + '.zip')
        list_file_result = []

        while page_count <= num_pages:
            file_name = ''
            file_content = None
            item_values = None
            file_content = {
                'header': str('header value for page = ' + str(page_count)),
                'items': []
            }
            current_page_max_idx = 10 * page_count
            max_item_index = current_page_max_idx - 1
            while item_index <= max_item_index and item_index < num_items:
                item_data = {
                    'nomor': item_index,
                    'deskripsi': str('item value for index = ' + str(item_index))
                }
                file_content['items'].append(item_data)
                item_index = item_index + 1

            template = None
            file_template = os.path.join(os.path.dirname(__file__), r'templates\test_files.docx')
            template_object = DocxTemplate(file_template)
            file_name = ('test' + str(datetime.today().date()) + 'page'+str(page_count) + '.docx')
            template_object.render(file_content)
            template_object.save(file_name)
            list_file_result.append(file_name)
            # docx_object = template_object.get_docx()
            # zipfile.write(file_name)
            page_count = page_count + 1

        with ZipFile(zipfilename, 'w') as zipfile:
            for file in list_file_result:
                print(file)
                zipfile.write(file)

        fp = open(zipfile.filename, "rb")
        file_data = fp.read()
        out = base64.encodestring(file_data)
        TedK1DocxMultiValue = {
            'filename': zipfile.filename,
            'filedata': out
        }
        wizardResult = self.env['test.output.docx.k1multi'].create(TedK1DocxMultiValue)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'test.output.docx.k1multi',
            'res_id': wizardResult.id,
            'view_type': 'form',
            'view_mode': 'form',
            'context': self.env.context,
            'target': 'new',
        }
