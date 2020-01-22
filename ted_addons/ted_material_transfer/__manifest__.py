{
    'name': 'Material Transfer In Out - Receiving User Enhancement',
    'summary': 'Bukti Serah Terima Barang',
    'version': '11.0.1.0.1',
    'category': 'Inventory',
    'author': "teddy_r@binasanprima.com",
    'license': 'AGPL-3',
    'website': 'http://bis2.binasanprima.com',
    'summary': 'Add Receiving User Field',
    'description': """
        What's new:
            - add Receiving User in header data. 
                Receiving User by default is filled from Employee field in Purchase Request 
                header data
    """,
    'depends': ['base', 'mail', 'stock', 'purchase_request', 'purchase', 'product'],
    'data': [
            'views/user_receiving_enh_all.xml',
            ],
}
