##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, models


class StockImmediateTransfer(models.TransientModel):
    _inherit = 'stock.immediate.transfer'

    # @api.models
    # def default_get(self, fields):
    #     res = {}
    #     print ' xxxxxxxxxxx'
    #     active_id = self._context.get('picking_id')
    #     if active_id:
    #         res = {'pick_id': active_id}
    #     return res

    @api.multi
    def process(self):
        res = super(StockImmediateTransfer, self).process()
        picking = self.env['stock.picking'].browse(
            # if we came, for eg, from a sale order, active_id would be the
            # sale order id
            # self._context.get('active_id'))
            # TODO we should also fix odoo methods
            self._context.get('picking_id'))
        # solo viene con vouchers en entrega total, sin backorder
        # si hay backorder se termina imprimiendo desde el backorder
        # confirmation
        if picking.book_required and picking.voucher_ids:
            return {
                'actions': [
                    res,
                    picking.do_print_voucher(),
                ],
                'type': 'ir.actions.act_multi',
            }
        else:
            return res
