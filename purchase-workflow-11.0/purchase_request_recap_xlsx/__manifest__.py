# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Purchase Request Recap Excel',
    'version': '11.0',
    'author': 'erickalvino@gmail.com',
    'category': 'Purchase',
    'license': 'LGPL-3',
    'support': 'erickalvino@gmail.com',
    'website': 'https://www.bsp.com',
    'summary': 'Recap Excel sheet for Purchase Request',
    'description': """ Purchase Request recap excel report""",
    'depends': [
        'purchase_request','base'
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/purchase_request_xls_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
