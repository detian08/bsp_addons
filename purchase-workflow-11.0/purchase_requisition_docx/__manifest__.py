# -*- coding: utf-8 -*-
{
    'name' : 'Purchase Requisition Dot Matrix Report',
    'version': '11.0',
    'author': 'putragolat@gmail.com',
    'category': 'Purchase',
    'license': 'LGPL-3',
    'support': 'putragolat@gmail.com',
    'website': 'https://www.mobee.com',
    'summary': 'Direct Print Dot Matrix for Purchase Request',
    'description': 'Purchase Requisition Dot Matrix report',
    'depends': [
        'purchase_request','base'
    ],
    'data': [
        'wizard/purchase_requisition_doc_view.xml',
     ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
