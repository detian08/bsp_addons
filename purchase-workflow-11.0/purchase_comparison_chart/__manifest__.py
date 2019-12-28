# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Purchase Comparison Chart',
    'version': '11.0.0',
    'category': 'Purchase',
    'author':'erickalvino@gmail.com',
    'description': """
    Quotation Comparison Form
    """,
    'license': 'LGPL-3',
    'summary': 'Quotation Comparison Form',
    'depends': ['purchase','website', 'purchase_requisition'],
    'website': 'https://www.binasanprima.com',
    'data': [
        'views/inherit_purchase_requisition_view.xml',
        'views/bid_templates.xml',
    ],
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 105,
}
