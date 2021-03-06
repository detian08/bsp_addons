{
    "name": "Purchase Request Generic",
    "author": "ErickAlvino@gmail.com",
    "version": "11.0.1.2.3",
    "category": "Purchase Management",
    "depends": [
        "purchase",
        "product",
        "purchase_request",
        "purchase_request_department",
        "hr",
        "stock_buffer"
    ],
    "data": ['views/purchase_request_generic_view.xml',
             'views/purchase_order_view.xml',
             'views/purchase_request_generic_menu_views.xml',
             'reports/purchase_request_report_views.xml',
             'security/ir.model.access.csv',
             'data/purchase_request_sequence.xml',
             "wizard/purchase_request_line_make_purchase_order_view.xml",
             "wizard/purchase_request_line_make_purchase_requisition_view.xml",],
    'demo': [],
    "license": 'LGPL-3',
    'installable': True,
    'application': True,
}
