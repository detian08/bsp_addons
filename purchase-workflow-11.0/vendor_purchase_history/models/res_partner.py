# © 2018-Today Aktiv Software (http://www.aktivsoftware.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"
    vendor_purchase_count = fields.Integer(string='',
                                           compute='_compute_vendor_purchase_count')

    @api.multi
    def _compute_vendor_purchase_count(self):
        PurchaseOrder = self.env['purchase.order.line']
        for partner in self:
            partner.vendor_purchase_count = PurchaseOrder.search_count(
                [('partner_id', 'child_of', partner.id)])
