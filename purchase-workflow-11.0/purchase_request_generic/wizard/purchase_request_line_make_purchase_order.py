from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError


class PurchaseRequestLineMakePurchaseOrder(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.order"
    _description = "Purchase Request Line Make Purchase Order"

    @api.model
    def _prepare_item(self, line):  # overwrite, add price_unit and keep_price
        return {
            'line_id': line.id,
            'request_id': line.request_id.id,
            'product_id': line.product_id.id,
            'name': line.name or line.product_id.name,
            'product_qty': line.product_qty,
            'price_unit': line.price_unit,
            'product_uom_id': line.product_uom_id.id,
            'keep_price': True
        }

    @api.model
    def _prepare_purchase_order_line(self, po, item):  # overwrite, add compute_price
        product = item.product_id
        # Keep the standard product UOM for purchase order so we should
        # convert the product quantity to this UOM
        qty = item.product_uom_id._compute_quantity(
            item.product_qty, product.uom_po_id or product.uom_id)
        price = item.product_uom_id._compute_price(
            item.price_unit, product.uom_po_id or product.uom_id)
        # Suggest the supplier min qty as it's done in Odoo core
        min_qty = item.line_id._get_supplier_min_qty(product, po.partner_id)
        qty = max(qty, min_qty)
        vals = {
            'name': product.name,
            'order_id': po.id,
            'product_id': product.id,
            'product_uom': product.uom_po_id.id,
            'price_unit': price,
            'product_qty': qty,
            'account_analytic_id': item.line_id.analytic_account_id.id,
            'purchase_request_lines': [(4, item.line_id.id)],
            'date_planned': item.line_id.date_required,
            'move_dest_ids': [(4, x.id) for x in item.line_id.move_dest_ids]
        }
        self._execute_purchase_line_onchange(vals)
        return vals

    @api.multi
    def make_purchase_order(self):  # overwrite
        res = []
        purchase_obj = self.env['purchase.order']
        po_line_obj = self.env['purchase.order.line']
        pr_line_obj = self.env['purchase.request.line']
        purchase = False

        for item in self.item_ids:
            line = item.line_id
            if item.product_qty <= 0.0:
                raise UserError(
                    _('Enter a positive quantity.'))
            if self.purchase_order_id:
                purchase = self.purchase_order_id
            if not purchase:
                po_data = self._prepare_purchase_order(
                    line.request_id.picking_type_id,
                    line.request_id.group_id,
                    line.company_id,
                    line.origin)
                purchase = purchase_obj.create(po_data)

            # Look for any other PO line in the selected PO with same
            # product and UoM to sum quantities instead of creating a new
            # po line
            domain = self._get_order_line_search_domain(purchase, item)
            available_po_lines = po_line_obj.search(domain)
            new_pr_line = True
            if available_po_lines and not item.keep_description:
                new_pr_line = False
                po_line = available_po_lines[0]
                po_line.purchase_request_lines = [(4, line.id)]
                po_line.move_dest_ids |= line.move_dest_ids
            else:
                po_line_data = self._prepare_purchase_order_line(purchase,
                                                                 item)
                if item.keep_description:
                    po_line_data['name'] = item.name
                po_line = po_line_obj.create(po_line_data)
            new_qty = pr_line_obj._calc_new_qty(
                line, po_line=po_line,
                new_pr_line=new_pr_line)
            po_line.product_qty = new_qty
            po_line._onchange_quantity()
            # The onchange quantity is altering the scheduled date of the PO
            # lines. We do not want that:
            po_line.date_planned = item.line_id.date_required
            if item.price_unit:
                po_line.price_unit = item.line_id.price_unit
            res.append(purchase.id)

        return {
            'domain': [('id', 'in', res)],
            'name': _('RFQ'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'view_id': False,
            'context': False,
            'type': 'ir.actions.act_window'
        }


class PurchaseRequestLineMakePurchaseOrderItem(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.order.item"
    _description = "Purchase Request Line Make Purchase Order Item"

    keep_price = fields.Boolean(string='Copy Price to new PO',
                                help='Set true if you want to keep the '
                                     'price provided in the '
                                     'wizard in the new PO.',)
    price_unit = fields.Float(string='Price Unit', digits=dp.get_precision('Price Unit'))
