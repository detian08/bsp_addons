# -*- coding: utf-8 -*-
# Copyright 2016, 2019 codefish
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "codefish Original Backend Theme",
    "summary": "Odoo 11.0 community backend theme",
    "version": "11.0.1.0.4",
    "category": "Themes/Backend",
    "website": "https://www.codefish.com.eg",
	"description": """
		Backend theme for Odoo 11.0 community edition.
    """,
	'images':[
        'images/screen.png'
	],
    "author": "codefish",
    "license": "LGPL-3",
    "installable": True,
    "depends": [
        'web_responsive',
    ],
    "data": [
        'views/assets.xml',
        'views/res_company_view.xml',
        'views/users.xml',
        'views/sidebar.xml',
        'views/web.xml',
    ],
}

