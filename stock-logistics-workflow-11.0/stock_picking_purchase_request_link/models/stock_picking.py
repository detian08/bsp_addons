# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def action_view_purchase_request(self):
        """This function returns an action that display existing purchase request
        base on purchase order
        of given picking.
        """
        """
                :return dict: dictionary value for created view
        """
        self.ensure_one()
        request_line_ids = []
        for line in self.purchase_id.order_line:
            request_line_ids += line.purchase_request_lines.ids

        domain = [('id', 'in', request_line_ids)]

        return {'name': _('Purchase Request Lines'),
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.request.line',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'domain': domain}
