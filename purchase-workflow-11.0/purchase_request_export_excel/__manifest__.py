{'name': 'Purchase Request Export To Excel',
 'version': '11.0.1.0.0',
 'author': 'erickalvino@gmail.com',
 'license': 'AGPL-3',
 'category': 'Tools',
 'depends': ['excel_import_export',
             'purchase_request'],
 'data': ['report/report_purchase_request.xml',
          'report/templates.xml',
          'report_action/purchase_request/report.xml',
          'report_action/purchase_request/templates.xml',
          ],
 'installable': True,
 }