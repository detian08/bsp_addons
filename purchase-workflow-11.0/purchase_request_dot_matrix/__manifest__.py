# -*- coding: utf-8 -*-
{
    'name' : 'Purchase Request Dot Matrix Report',
    'version': '11.0',
    'author': 'erickalvino@gmail.com',
    'category': 'Purchase',
    'license': 'LGPL-3',
    'support': 'erickalvino@gmail.com',
    'website': 'https://www.mobee.com',
    'summary': 'Direct Print Dot Matrix for Purchase Request',
    'description': """ Purchase Request Dot Matrix report
When user need to print the Dot Matrix report in purchase request select the purchase request list and
user need to click the "Print dot matrix" button """,
    'depends': [
        'purchase_request','base'
    ],
    'data': [
        'wizard/purchase_request_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
