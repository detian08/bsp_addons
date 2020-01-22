# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'TED - OPU-K1 Recap',
    'version': '11.0',
    'author': 't.rachmayadi@gmail.com',
    'category': 'Purchase',
    'license': 'LGPL-3',
    'support': 't.rachmayadi@gmail.com',
    'website': 'https://www.bsp.com',
    'summary': 'OPU-K1 Report',
    'description': """ OPU-K1 report in xlsx""",
    'depends': [
        'purchase_request','base'
    ],
    'data': [

        'wizard/ted_opu_k1_recap_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
