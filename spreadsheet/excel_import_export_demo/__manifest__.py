# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{'name': 'Excel Import/Export/Report Demo',
 'version': '11.0.1.0.0',
 'author': 'Ecosoft,Odoo Community Association (OCA)',
 'license': 'AGPL-3',
 'website': 'https://github.com/OCA/server-tools/',
 'category': 'Tools',
 'depends': ['excel_import_export',
             'sale_management'],
 'data': ['import_export_sale_order/actions.xml',
          'import_export_sale_order/templates.xml',
          'report/report.xml',
          'report/templates.xml',
          'import_sale_orders/menu_action.xml',
          'import_sale_orders/templates.xml',
          # Use report action
          'report_action/purchase_request/report.xml',
          'report_action/purchase_request/templates.xml',
          'report_action/partner_list/report.xml',
          'report_action/partner_list/templates.xml',
          'report_action/partner_list/report_partner_list.xml',
          ],
 'installable': True,
 'development_status': 'alpha',
 'maintainers': ['kittiu'],
 }
