# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'TED - K1 DOCX Recap',
    'version': '11.0',
    'author': 't.rachmayadi@gmail.com',
    'category': 'Purchase',
    'license': 'LGPL-3',
    'support': 't.rachmayadi@gmail.com',
    'website': 'https://www.bsp.com',
    'summary': 'Excel sheet for Purchase Request',
    'description': """ Docx Recap for K1 Form""",
    'depends': [
        'purchase_request','base'
    ],
    'data': [

        'wizard/ted_k1_pdf_recap_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
