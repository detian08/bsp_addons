# -*- coding: utf-8 -*-
{
    'name': "Product Restriction on Users",

    'summary': """
    User Allowed Products Only.
    """,

    'description': """
        - This Module adds restriction on users for accessing products for any kind of operation.
        - User can not see the products if not allowed by the admin.
        - User can only see and operate on Allowed Products.
        - Restriction also applies to sales order, purchase order, stock transfer etc.
        - Admin can edit the user and add allowed produts to a specific user.
        - Note : This Restriction is Applied On Adminstrator.
    """,

    'author': "Techspawn Solutions",
    'website': "http://www.techspawn.com",

    'category': 'Others',
    'version': '0.1',

    'depends': ['base', 'stock', 'sale', 'product'],

    'data': [
        #'security/ir.models.access.csv',
        'security/security.xml', 
        'user_view.xml',
    ],
}
