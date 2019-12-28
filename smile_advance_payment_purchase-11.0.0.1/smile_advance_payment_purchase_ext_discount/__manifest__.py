# -*- coding: utf-8 -*-
{
    "name": "Supplier Advance Payments Extend With Discount",
    "version": "0.1",
    "license": 'AGPL-3',
    "depends": [
        "purchase",
        "smile_advance_payment_base",
    ],
    "author": "erickalvino@gmail.com",
    "description": """Supplier Advance Payments Management
    with percentage type
    """,
    "website": "http://www.binasanprima.com",
    "category": "Accounting & Finance",
    "sequence": 32,
    "data": [
        "security/payment_confirm.xml",
        "security/ir.model.access.csv",
        "views/account_payment_view.xml",
        "views/purchase_order_view.xml"
    ],
    "demo": [],
    'test': [],
    "auto_install": False,
    "installable": True,
    "application": False,
}
