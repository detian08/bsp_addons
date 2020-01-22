{
    'name' : 'TED - Form Permohonan Pembayaran',
    'version': '11.0.1.0.1',
    'author': 'teddy_r@mail.binasanprima.com',
    'category': 'Purchase',
    'license': 'LGPL-3',
    'support': 't.rachmayadi@gmail.com',
    'website': 'https://www.binasanprima.com',
    'summary': 'Transaksi Pembuatan Form Permohonan Pembayaran',
    'description': """ Transaksi Form Permohonan Pembayaran
        - 
    """,
    'depends': [
        'purchase',
        'base',
        'account'
    ],
    'data': [
        'views/ted_form_spb.xml',
        'views/ted_spb_docx.xml',
        'data/spb_sequence.xml',
        'data/spb_data_messaging.xml',
        # # 'security/ir.model.access.csv',
        # # 'security/ted_spb.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}