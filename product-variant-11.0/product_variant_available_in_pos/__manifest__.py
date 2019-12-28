# Copyright 2016 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Product Variant Available In Pos',
    'summary': 'Available In Pos in product level',
    'version': '11.0.1.0.0',
    'category': 'Point Of Sale',
    'license': 'AGPL-3',
    'author': 'Agile Business Group, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/product-variant/tree/'
               '11.0/product_variant_available_in_pos',
    'depends': [
        'point_of_sale',
    ],
    'post_init_hook': 'post_init_hook',
}
