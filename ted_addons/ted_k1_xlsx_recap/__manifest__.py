# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'TED - K1 XLSX Recap',
    'version': '11.0',
    'author': 't.rachmayadi@gmail.com',
    'category': 'Purchase',
    'license': 'LGPL-3',
    'support': 't.rachmayadi@gmail.com',
    'website': 'https://www.bsp.com',
    'summary': 'K1 XLSX Recap',
    'description': """ K1 XLSX Recap""",
    'depends': [
        'purchase_request','base'
    ],
    'data': [

        'wizard/ted_k1_xlsx_recap_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
