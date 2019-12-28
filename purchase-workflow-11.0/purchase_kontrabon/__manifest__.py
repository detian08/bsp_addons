{
    'name': 'Purchase Kontrabon',
    'summary': 'Kontrabon Pembelian',
    'version': '11.0.1.0.0',
    'category': 'Purchase',
    'author': "didin.komarudin@gmail.com",
    'license': 'AGPL-3',
    'website': 'http://bis2.com',
    'depends': ['base','purchase','account'],
    'data': ['wizard/select_payments_wizard_view.xml',
             'views/purchase_kontrabon_views.xml',
             'views/purchase_kontrabon_menu.xml'
             ],
    'installable': True,
    'auto_install': False,
}
