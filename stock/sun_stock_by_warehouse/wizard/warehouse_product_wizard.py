# -*- coding: utf-8 -*-
#################################################################################

from odoo import models, fields, api, _
from datetime import datetime, date


class warehouse_inventory_wizard(models.TransientModel):
    _name = "warehouse.inventory.wizard"

    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id.id, required=True)
    warehouse_ids = fields.Many2many('stock.warehouse', 'warehouse_wizard_stock_rel', string="Warehouse")

    @api.onchange('company_id')
    def onchange_company_id(self):
        if self.company_id:
            self.warehouse_ids = False

    @api.multi
    def generate_pdf_report(self):
        if not self.warehouse_ids:
            warehouse_ids = self.warehouse_ids
        else:
            warehouse_ids = self.env['stock.warehouse'].search([('company_id', '=', self.company_id.id)])
        datas = {'form':
                    {
                        'company_id': self.company_id.id,
                        'warehouse_ids': [y.id for y in warehouse_ids],
                        'id': self.id,
                    },
                }
        return self.env.ref('sun_stock_by_warehouse.action_report_stock_inventory').report_action(self, data=datas)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: