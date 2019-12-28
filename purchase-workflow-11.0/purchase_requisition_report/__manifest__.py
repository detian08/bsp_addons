# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Purchase Agreements Reports',
    'version': '0.1',
    'category': 'Purchases',
    'website': 'http://www.binasanprima.com',
    'description': """
This module allows you to manage your Purchase Agreements Reports.
==================================================================
""",
    'depends' : ['purchase'],
    'demo': [],
    'data': ['report/purchase_requisition_report.xml',
             'report/report_purchaserequisition.xml',
             ],
}
