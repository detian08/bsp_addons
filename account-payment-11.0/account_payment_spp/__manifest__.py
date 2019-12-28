{
    "name": "Account Payment SPP",
    "version": "11.0.1.0.1",
    "summary": "Manage the Surat Permintaan Pembayaran of your payments",
    'license': 'AGPL-3',
    "depends": [
                # 'account',
                # 'purchase',
                'smile_advance_payment_purchase_ext_discount'
    ],
    'author': 'erickalvino@gmail.com',
    'website': 'https://www.binasanprima.com',
    'data': ['views/payment.xml',
             'security/spp.xml',
             'security/ir.model.access.csv',
             'data/spp_sequence.xml',
             'wizard/select_purchaseorder_wizard_view.xml',
             'views/spp_views.xml',
             'views/spp_menus.xml',
             ],
}
