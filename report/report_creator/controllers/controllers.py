# -*- coding: utf-8 -*-
from odoo import http
from openerp.http import request
from openerp.addons.web.controllers.main import serialize_exception,content_disposition
import base64

class ReportCreator(http.Controller):
    
    @http.route('/web/test', type='http', auth="public")
    @serialize_exception
    def download_document(self,model,id, **kw):  
        
#         get the string html from database and return it
        test_report =""
        if request.env[model].browse(int(id)).test_html:
            test_report = request.env[model].browse(int(id)).test_html
            
        
        return test_report