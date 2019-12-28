# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Stock Picking Purchase Request Link',
    'summary': """
        Link between picking and purchase Request""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'erickalvino@gmail.com',
    'website': 'https://github.com/OCA/stock-logistics-workflow',
    "application": False,
    "installable": True,
    'depends': [
        'purchase'
    ],
    'data': [
        'views/stock_picking_view.xml',
    ],
}
