# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'TED - Test Output Multiple Files Docx',
    'version': '11.0',
    'author': 't.rachmayadi@gmail.com',
    'category': 'Purchase',
    'license': 'LGPL-3',
    'support': 't.rachmayadi@gmail.com',
    'website': 'https://www.bsp.com',
    'summary': 'Test Output Multiple Files Docx',
    'description': """ Test Output Multiple Files Docx""",
    'depends': [
        'purchase_request','base'
    ],
    'data': [
        'security/security.csv',
        'wizard/ted_test_docx_single_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
