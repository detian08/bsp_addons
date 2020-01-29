# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Partner Taxes',
    'version' : '11.0.0.1.0',
    'summary': 'Set Partner Taxes',
    'sequence': 1,
    'license': 'AGPL-3',
    "author": "Alphasoft",
    'description': """ This module is aim to add Partner Taxes
    """,
    'category' : 'Accounting',
    'website': 'https://www.alphasoft.co.id/',
    'images':  ['images/main_screenshot.png'],
    'depends' : ['base', 'account'],
    'data': [
        "views/partner_view.xml",
    ],
    'demo': [
        
    ],
    'qweb': [
        
    ],
    'price': 0.00,
    'currency': 'EUR',
    'installable': True,
    'application': False,
    'auto_install': False,
    #'post_init_hook': '_auto_install_l10n',
}
