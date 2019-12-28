# -*- coding: utf-8 -*-
{
    'name': 'Advanced Auto Reordering Rules Control. Create and Manage Reordering Rules using Templates, Automatic Reordering Rule Order Point Generator',
    'version': '11.0.1.1',
    'author': 'Ivan Sokolov',
    'category': 'Warehouse',
    'license': 'LGPL-3',
    'website': 'https://demo.cetmix.com',
    'live_test_url': 'https://demo.cetmix.com',
    'summary': """Create and manage reordering rules automatically using templates""",
    'description': """
    Create reordering rules automatically from templates. Create stock orderpoint automatically. Use template to manage
     reordering rules.
""",
    'depends': ['product', 'stock'],
    'images': ['static/description/banner.png'],
    'data': [
        'security/ir.models.access.csv',
        'views/cx_stock_product.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}
