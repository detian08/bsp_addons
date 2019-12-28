# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Bukti Serah Terima Barang Report',
    'version': '0.1',
    'category': 'Purchases',
    'website': 'http://www.binasanprima.com',
    'description': """
This module allows you to print your Material Transfer Out.
==================================================================
""",
    'author': 'bam@binasanprima.com',
    'website': 'http://bis2.binasanprima.com',
    'depends' : ['base', 'purchase_request','material_transfer_in_out'],
    'demo': [],
    'data': ['reports/bsp_purchase_bstb_report.xml',
             ],
    'images' : ['static/bsp.bmp']
}
