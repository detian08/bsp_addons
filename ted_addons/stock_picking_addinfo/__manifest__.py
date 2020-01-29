{
    'name': 'Surat Permohonan Pembayaran - Add Bank Information Fields',
    'summary': 'Bank Enhancement for Surat Permohonan Pembayaran',
    'version': '11.0.1.0.1',
    'category': 'Invoice',
    'author': "teddy_r@binasanprima.com",
    'license': 'AGPL-3',
    'website': 'http://bis2.binasanprima.com',
    'summary': 'Add Bank Information Fields',
    'description': """
        What's new:
            - add Bank Account Name. 
            - add Bank Branch Name.
            - add Bank Branch Address.
    """,
    "depends": ['account', 'purchase', 'smile_advance_payment_purchase_ext_discount'],
    'data': [
            'views/ted_enh_spp.xml',
            ],
}
