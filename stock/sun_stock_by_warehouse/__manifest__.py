{
    'name': 'Product stock by warehouse / Warehouse Inventory Report',
    'version': '11.0.3',
    'category': 'Inventory',
    'summary': 'Product stock by warehouse / Warehouse Inventory Report',
    'description': """ Using this module you can get product stock by warehouse/Inventory.
    """,
    'price': 0,
    'currency': 'EUR',
    'author': 'Kiran Kantesariya',
    'email': 'risingsuntechcs@gmail.com',
    'license': 'OPL-1',
    'depends': ['base', 'stock'],
    "live_test_url" : "https://www.youtube.com/watch?v=H56TvLfY--Y&feature=youtu.be",
    'data': [
             'wizard/warehouse_product_wizard_view.xml',
             'report/report.xml',
             'report/report_stock_inventory.xml',
    ],
    'qweb': [
        ],
    'images': ['static/description/icon.png'],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
