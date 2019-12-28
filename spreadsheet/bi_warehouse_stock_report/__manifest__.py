# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2018 Bassam Infotech LLP(<https://www.bassaminfotech.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Warehouse Stock Report',
    'version': '1.0',
    'category': 'Inventory',
    'summary': 'Warehouse Stock Report XLS',
    'license':'AGPL-3',
    'description': """
    This module will create a excel report containing the important details of available products in a particular warehouse between a specific time interval.
""",
    'author' : 'Bassam Infotech LLP',
    'website' : 'https://www.bassaminfotech.com',
    'depends': ['stock'],
    'images': ['static/description/banner.jpg'],
    'data': [
        'wizard/warehouse_stock_report_view.xml'
    ],
    'installable': True,
    'auto_install': False,
}
