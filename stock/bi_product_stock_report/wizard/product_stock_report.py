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

from odoo import api, fields, models, _

from odoo.tools.misc import xlwt
from odoo.exceptions import UserError, AccessError
import io
import base64
import operator
import itertools

class StockReport(models.TransientModel):
	_name = "print.stock.report"
	_description = "Stock Inventory Report"
	
	inventory_date = fields.Datetime('Inventory at Date', default=lambda self: fields.Datetime.now())
	stock_report_file = fields.Binary('Inventory Report')
	file_name = fields.Char('File Name')
	inventory_printed = fields.Boolean('Payment Report Printed')
	start_date = fields.Datetime('Start Date', default=lambda self: fields.Datetime.now())
	wstart_date = fields.Datetime('Start Date(Optional)')
	end_date = fields.Datetime('End Date', default=lambda self: fields.Datetime.now())
	location_id = fields.Many2one('stock.location', string= 'Location') 
	product_id = fields.Many2one('product.product', string='Product')

	@api.multi
	def action_product_stock_report(self):
		invoice_obj1 = self.env['check.stock'].search([])
		if invoice_obj1:
			invoice_obj1[-1].write(
							{'start_date':self.start_date,
							'wstart_date':self.wstart_date,
							'end_date':self.end_date,
							'location_id':self.location_id.id,
							})
		if not invoice_obj1:
			invoice_obj1.create(
							{'start_date':self.start_date,
							'wstart_date':self.wstart_date,
							'end_date':self.end_date,
							'location_id':self.location_id.id,
							})
		invoice_obj = self.env['check.stock'].search([])[-1]
		workbook = xlwt.Workbook()
		column_heading_style = xlwt.easyxf('font:height 200;font:bold True;')
		if invoice_obj.location_id:
			worksheet = workbook.add_sheet(invoice_obj.location_id.branch_id.name)
		else:
			worksheet = workbook.add_sheet("All Branches")

		for result in invoice_obj:
			row = 1
			col = 0
			new_row = row 
			y = 'Yes'
			n = 'No'
			worksheet.write(1, 0, _('Sl.no'), column_heading_style)
			worksheet.write(1, 1, _('Product'), column_heading_style)
			worksheet.write(1, 2, _('Internal Reference'), column_heading_style)
			worksheet.write(1, 3, _('Quantity'), column_heading_style)
			worksheet.write(1, 4, _('Rate'), column_heading_style)
			worksheet.col(1).width = 10000
			worksheet.col(2).width = 5000
			worksheet.row(0).height = 500
			i = 0
			line_ids = []
			lines = []
			vals = {
				 'product_name': '',
				 'quantity': 0.0,
				 'price': 0.0,
				 'default_code': 0.0,
			}
			domain=[('in_date','>=',result.start_date),('in_date','<=',result.end_date),('location_id','=',result.location_id.id)]
			if self.product_id:
				domain = [('product_id','=',self.product_id.id)]
			for line in self.env['stock.quant'].search(domain):
				vals = {
						 'product_name': line.product_id.name,
						 'default_code': line.product_id.default_code,
						 'quantity':line.quantity,
						 'price': line.product_id.list_price,
					}
				lines.append(vals)
				
			line1 = sorted(lines, key=operator.itemgetter('product_name'))
			for key, value in itertools.groupby(line1, key=operator.itemgetter('product_name')):
				quantity = 0
				for item in list(value):
					quantity+=int(item['quantity'])
				line_ids.append({'default_code': item['default_code'], 'price': item['price'], 'quantity': quantity, 'product_name': item['product_name']})
  
			for result in line_ids:
				i+=1
				row+=1
				worksheet.write(row, 0, i)
				worksheet.write(row, 1, result['product_name'])
				worksheet.write(row, 2, result['default_code'])
				worksheet.write(row, 3, result['quantity'])
				worksheet.write(row, 4, result['price'])

		for wizard in self:
			report_head = 'Product Stock Report'
			worksheet.write_merge(0, 0, 0, 4, report_head, xlwt.easyxf('font:height 300; align: vertical center; align: horiz center;pattern: pattern solid, fore_color black; font: color white; font:bold True;' "borders: top thin,bottom thin"))
			fp = io.BytesIO()
			workbook.save(fp)
			excel_file = base64.encodestring(fp.getvalue())
			wizard.stock_report_file = excel_file
			wizard.file_name = 'Product Stock Report.xls'
			wizard.inventory_printed = True
			fp.close()
			return {
					'view_mode': 'form',
					'res_id': wizard.id,
					'res_model': 'print.stock.report',
					'view_type': 'form',
					'type': 'ir.actions.act_window',
					'context': self.env.context,
					'target': 'new',
			}
	
class CheckStock(models.Model):
	_name = 'check.stock'

	start_date = fields.Datetime()
	end_date = fields.Datetime()
	location_id = fields.Many2one('stock.location', string= 'Location') 
	product_id = fields.Many2one('product.product', string='Product')