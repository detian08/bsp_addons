# -*- coding: utf-8 -*-
{
    'name' : 'BPPB & QCF Report PDF, Excel, Docx & Print',
    'version': '11.0',
    'author': 'ian.popeye@gmail.com',
    'category': 'Purchase',
    'license': 'LGPL-3',
    'website': '',
    'summary': 'BPPB & QCF Report',
    'description': """ """,
    'depends': ['purchase_request','base'],
    'data': [
        'wizard/bppb_report_wizard_view.xml',
        'wizard/qcf_report_wizard_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
