# -*- coding: utf-8 -*-
# (C) 2017 Smile (<http://www.smile.fr>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "@api.depends filtering",
    "version": "0.1",
    "depends": ["smile_filtered_from_domain"],
    "author": "Smile",
    "license": 'AGPL-3',
    "description": """
@api.depends filtering
======================

This module allows to filter records to recompute
by specifying a domain for a trigger.

Example:
    @api.depends(
        ('product_id.lst_price', [('invoice_id.state', '=', 'draft')]))

To work, this module must be defined as a wide module.

Suggestions & Feedback to: Corentin Pouhet-Brunerie
    """,
    "website": "http://www.smile.fr",
    'category': 'Tools',
    "sequence": 0,
    "data": [
        "security/ir.model.access.csv",
    ],
    "auto_install": True,
    "installable": True,
    "application": False,
}
