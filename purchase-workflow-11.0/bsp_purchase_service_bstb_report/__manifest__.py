# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Purchase - BSTB Service',
    'version': '0.1',
    'category': 'Purchases',
    'website': 'http://www.binasanprima.com',
    'description': """ This module allows you to print your Purchase Order with product Type Service.""",
    'author': 'bam@binasanprima.com',
    'website': 'http://bis2.binasanprima.com',
    'depends' : ['base', 'smile_advance_payment_purchase_ext_discount'],
    'demo': [],
    'data': ['reports/bsp_purchase_bstb_report.xml',
             ],
    'images' : ['static/bsp.bmp']
}
