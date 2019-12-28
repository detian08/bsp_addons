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
	_name = "warehouse.stock.report"
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
	def action_warehouse_stock_report(self):
		invoice_obj1 = self.env['check.stock'].search([])
		if invoice_obj1:
			invoice_obj1[-1].write(
							{
							'location_id':self.location_id.id,
							})
		if not invoice_obj1:
			invoice_obj1.create(
							{
							'location_id':self.location_id.id,
							})
		invoice_obj = self.env['check.stock'].search([])[-1]
		ctx = dict(self.env.context) or {}
		workbook = xlwt.Workbook()
		worksheet = workbook.add_sheet('Inventory')
		column_heading_style = xlwt.easyxf('font:height 200;font:bold True;')
		row = 2
		lines = []
		line_ids = []
		ctot_val = 0.0
		mtot_val = 0.0
		cost_tot_val = 0.0
		mrp_tot_val = 0.0
		for result in invoice_obj:
			report_head = 'Warehouse Stock Report'
			# if result.inventory_date:
			#     report_head += ' (' + result.inventory_date + ')'
			worksheet.write_merge(0, 0, 0, 7, report_head, xlwt.easyxf('font:height 300; align: vertical center; align: horiz center;pattern: pattern solid, fore_color black; font: color white; font:bold True;' "borders: top thin,bottom thin"))
			worksheet.write(1, 0, _('Internal Reference'), column_heading_style) 
			worksheet.write(1, 1, _('Product'), column_heading_style) 
			worksheet.write(1, 2, _('Description'), column_heading_style)
			worksheet.write(1, 3, _('Quantity'), column_heading_style)
			worksheet.write(1, 4, _('Cost'), column_heading_style)
			worksheet.write(1, 5, _('Cost Valuation'), column_heading_style)
			worksheet.write(1, 6, _('MRP'), column_heading_style)
			worksheet.write(1, 7, _('MRP Valuation'), column_heading_style)
			worksheet.col(0).width = 5000
			worksheet.col(1).width = 10000
			worksheet.col(2).width = 5000
			worksheet.col(5).width = 5000
			worksheet.col(7).width = 5000
			worksheet.row(0).height = 500
			worksheet.col(4).width = 5000
			vals = {
				 'product_name': '',
				 'description': '',
				 'cost': 0.0,
				 'quantity': 0.0,
				 'price': 0.0,
				 'default_code': 0.0,
				 'ctot_amount': 0.0,
				 'mtot_amount': 0.0,
			}
			# ctx.update({'to_date': wizard.inventory_date})
			# raise UserError(str(self.start_date))
			if self.wstart_date:
				domain = [('in_date','<=',result.end_date), ('in_date','>=',self.wstart_date), ('location_id','=',result.location_id.id)]
			else:
				domain = [('in_date','<=',result.end_date),('location_id','=',result.location_id.id)]
			# product_objs = self.env['product.product'].with_context(ctx).search([], order='name')
			product_objs = self.env['stock.quant'].search(domain)
			for product in product_objs:
				vals = {
						 'product_name': product.product_id.name,
						 'description': product.product_id.description,
						 'default_code': product.product_id.default_code,
						 'quantity':product.quantity,
						 'cost': product.product_id.standard_price,
						 'price': product.product_id.list_price,
					}
				lines.append(vals)
				# if product.qty_available > 0:
				#     if product.default_code:
				#         worksheet.write(row, 0, product.default_code)
				#     worksheet.write(row, 1, product.name)
				#     worksheet.write(row, 2, product.qty_available)
				#     row += 1
			line1 = sorted(lines, key=operator.itemgetter('default_code'))
			for key, value in itertools.groupby(line1, key=operator.itemgetter('default_code')):
				quantity = 0
				for item in list(value):
					quantity+=int(item['quantity'])
				ctot_amount = int(item['quantity']) * int(item['cost'])
				ctot_val += int(item['cost'])
				cost_tot_val += ctot_amount
				mtot_amount = int(item['quantity']) * int(item['price'])
				mtot_val += int(item['price'])
				mrp_tot_val += mtot_amount
				line_ids.append({'ctot_amount': ctot_amount, 'mtot_amount': mtot_amount, 'default_code': item['default_code'], 'description': item['description'], 'price': item['price'], 'cost': item['cost'], 'quantity': quantity, 'product_name': item['product_name']})
  
			for result in line_ids:
				row+=1
				worksheet.write(row, 0, result['default_code'])
				worksheet.write(row, 1, result['product_name'])
				worksheet.write(row, 2, result['description'])
				worksheet.write(row, 3, result['quantity'])
				worksheet.write(row, 4, result['cost'])
				worksheet.write(row, 5, result['ctot_amount'])
				worksheet.write(row, 6, result['price'])
				worksheet.write(row, 7, result['mtot_amount'])
			row+=5
			worksheet.write(row, 1, _('Total Valuation'), column_heading_style)
			worksheet.write(row, 4, ctot_val)
			worksheet.write(row, 5, cost_tot_val)
			worksheet.write(row, 6, mtot_val)
			worksheet.write(row, 7, mrp_tot_val)
		for wizard in self:
			# report_head = 'Warehouse Stock Report'
			fp = io.BytesIO()
			workbook.save(fp)
			excel_file = base64.encodestring(fp.getvalue())
			wizard.stock_report_file = excel_file
			wizard.file_name = 'Warehouse Stock Report.xls'
			wizard.inventory_printed = True
			fp.close()
			return {
					'view_mode': 'form',
					'res_id': wizard.id,
					'res_model': 'warehouse.stock.report',
					'view_type': 'form',
					'type': 'ir.actions.act_window',
					'context': self.env.context,
					'target': 'new',
			}
	
class CheckStock(models.Model):
	_name = 'check.stock'

	start_date = fields.Datetime()
	end_date = fields.Datetime()
	wstart_date = fields.Datetime()
	location_id = fields.Many2one('stock.location', string= 'Location') 
	product_id = fields.Many2one('product.product', string='Product')