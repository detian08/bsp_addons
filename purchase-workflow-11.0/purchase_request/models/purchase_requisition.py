# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import _, api, exceptions, fields, models


class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"

    name = fields.Char("Description")
    purchase_request_lines = fields.Many2many(
        'purchase.request.line',
        'purchase_request_purchase_requisition_line_rel',
        'purchase_requisition_line_id',
        'purchase_request_line_id',
        'Purchase Request Lines', readonly=True, copy=False)

    @api.multi
    def action_openRequestLineTreeView(self):
        """
        :return dict: dictionary value for created view
        """
        request_line_ids = []
        for line in self:
            request_line_ids += line.purchase_request_lines.ids

        domain = [('id', 'in', request_line_ids)]

        return {'name': _('Purchase Request Lines'),
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.request.line',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'domain': domain}

    @api.multi
    def _prepare_purchase_order_line(self, name, product_qty=0.0, price_unit=0.0, taxes_ids=False):
        self.ensure_one()
        requisition = self.requisition_id
        if self.purchase_request_lines.id:
            return {
                'name': name,
                'product_id': self.product_id.id,
                'product_uom': self.product_id.uom_po_id.id,
                'product_qty': product_qty,
                'price_unit': price_unit,
                'taxes_id': [(6, 0, taxes_ids)],
                'date_planned': requisition.schedule_date or fields.Date.today(),
                'account_analytic_id': self.account_analytic_id.id,
                'move_dest_ids': self.move_dest_id and [(4, self.move_dest_id.id)] or [],
                'purchase_request_lines': [(4, self.purchase_request_lines.id)],
            }
        else:
            return {
                'name': name,
                'product_id': self.product_id.id,
                'product_uom': self.product_id.uom_po_id.id,
                'product_qty': product_qty,
                'price_unit': price_unit,
                'taxes_id': [(6, 0, taxes_ids)],
                'date_planned': requisition.schedule_date or fields.Date.today(),
                'account_analytic_id': self.account_analytic_id.id,
                'move_dest_ids': self.move_dest_id and [(4, self.move_dest_id.id)] or [],
            }
