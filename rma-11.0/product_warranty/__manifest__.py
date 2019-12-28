{
    'name': 'Product Warranty',
    'version': '11.0.1.0.0',
    'category': 'Generic Modules/Product',
    'author': 'Akretion, Vauxoo, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/rma',
    'license': 'AGPL-3',
    'depends': ['product', 'sale', 'purchase'],
    'data': ['security/ir.model.access.csv',
             'views/res_company.xml',
             'views/product_warranty.xml',
             'views/product_template.xml'],
    'images': ['images/product_warranty.png'],
    'development_status': 'Production/Stable',
    'maintainers': [
        'osi-scampbell',
        'max3903',
    ]
}