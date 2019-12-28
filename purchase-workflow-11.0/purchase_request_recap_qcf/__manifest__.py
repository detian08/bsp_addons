{
    'name' : 'Purchase Request Recap QCF Excel',
    'version': '11.0',
    'author': 'putragolat@gmail.com',
    'category': 'Purchase',
    'license': 'LGPL-3',
    'support': 'putragolat@gmail.com',
    'website': 'https://www.bsp.com',
    'summary': 'Recap Excel sheet for Purchase Request',
    'description': """ Purchase Request recap qcf excel report""",
    'depends': [
        'purchase_request','base'
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/purchase_request_qcf_xls_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}