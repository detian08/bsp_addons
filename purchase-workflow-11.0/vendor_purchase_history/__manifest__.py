# © 2018-Today Aktiv Software (http://www.aktivsoftware.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': "Vendor Purchase History",

    'summary': """
        User can view the products which are brought by vendors
        just in a View easily.With the help of
        this module you can learn more about your Vendors
        and your shopping habits.""",


    'description': """
        This module will help the user to see
        the purchase history from the Vendor Easily.
    """,

    'author': "Aktiv Software",
    'website': "http://www.aktivsoftware.com",
    'license': "AGPL-3",

    'category': 'Purchases',
    'version': '11.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['purchase', 'product'],

    # always loaded
    'data': [
        'views/res_partner_views.xml',
    ],
    'images': [
        'static/description/banner.jpg',
    ],
    'installable': True,
}
