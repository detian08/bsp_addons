# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2018 BroadTech IT Solutions Pvt Ltd 
#    (<http://broadtech-innovations.com>).
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
import io
import base64


class StockReport(models.TransientModel):
    _name = "print.stock.report"
    _description = "Stock Inventory Report"
    
    inventory_date = fields.Datetime('Inventory at Date', default=lambda self: fields.Datetime.now())
    stock_report_file = fields.Binary('Inventory Report')
    file_name = fields.Char('File Name')
    inventory_printed = fields.Boolean('Payment Report Printed')

    @api.multi
    def action_print_stock_report(self):
        ctx = dict(self.env.context) or {}
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Inventory')
        column_heading_style = xlwt.easyxf('font:height 200;font:bold True;')
        
        row = 2
        for wizard in self:
            report_head = 'Stock Take Report'
            if wizard.inventory_date:
                report_head += ' (' + wizard.inventory_date + ')'
            worksheet.write_merge(0, 0, 0, 2, report_head, xlwt.easyxf('font:height 300; align: vertical center; align: horiz center;pattern: pattern solid, fore_color black; font: color white; font:bold True;' "borders: top thin,bottom thin"))
            worksheet.write(1, 0, _('Internal Reference'), column_heading_style) 
            worksheet.write(1, 1, _('Product'), column_heading_style) 
            worksheet.write(1, 2, _('Quantity On Hand'), column_heading_style)
            worksheet.col(0).width = 5000
            worksheet.col(1).width = 10000
            worksheet.col(2).width = 5000
            worksheet.row(0).height = 500
            
            ctx.update({'to_date': wizard.inventory_date})
            product_objs = self.env['product.product'].with_context(ctx).search([], order='name')
            for product in product_objs:
                if product.qty_available > 0:
                    if product.default_code:
                        worksheet.write(row, 0, product.default_code)
                    worksheet.write(row, 1, product.name)
                    worksheet.write(row, 2, product.qty_available)
                    row += 1
            
            fp = io.BytesIO()
            workbook.save(fp)
            excel_file = base64.encodestring(fp.getvalue())
            wizard.stock_report_file = excel_file
            wizard.file_name = 'Stock Take Report.xls'
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
    


# vim:expandtab:smartindent:tabstop=2:softtabstop=2:shiftwidth=2:


