# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).


from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError


class PurchaseRequestLineMakePurchaseRequisition(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.requisition"
    _description = "Purchase Request Line Make Purchase Requisition"

    @api.model
    def _prepare_item(self, line): # overwrite, add price_unit and keep_price
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
    def _prepare_purchase_requisition_line(self, po, item):
        product = item.product_id
        # Keep the standard product UOM for purchase order so we should
        # convert the product quantity to this UOM
        qty = item.product_uom_id._compute_quantity(
            item.product_qty, product.uom_po_id or product.uom_id)
        price_unit = item.product_uom_id._compute_quantity(
            item.price_unit, product.uom_po_id or product.uom_id)
        # Suggest the supplier min qty as it's done in Odoo core
        min_qty = item.line_id._get_supplier_min_qty(product, po.vendor_id)
        qty = max(qty, min_qty)
        vals = {
            'name': product.name,
            'requisition_id': po.id,
            'product_id': product.id,
            'product_uom_id': product.uom_po_id.id,
            'price_unit': price_unit,
            'product_qty': qty,
            'account_analytic_id': item.line_id.analytic_account_id.id,
            'purchase_request_lines': [(4, item.line_id.id)],
            'schedule_date': item.line_id.date_required,
            'move_dest_id': [(4, x.id) for x in item.line_id.move_dest_ids]
        }
        self._execute_purchase_line_onchange(vals)
        return vals

    @api.multi
    def make_purchase_requisition(self):
        res = []
        purchase_obj = self.env['purchase.requisition']
        po_line_obj = self.env['purchase.requisition.line']
        pr_line_obj = self.env['purchase.request.line']
        purchase = False

        for item in self.item_ids:
            line = item.line_id
            if item.product_qty <= 0.0:
                raise UserError(
                    _('Enter a positive quantity.'))
            if self.purchase_requisition_id:
                purchase = self.purchase_requisition_id
            if not purchase:
                po_data = self._prepare_purchase_requisition(
                    line.request_id.picking_type_id,
                    line.request_id.group_id,
                    line.company_id,
                    line.origin)
                purchase = purchase_obj.create(po_data)

            # Look for any other PR line in the selected PR with same
            # product and UoM to sum quantities instead of creating a new
            # PR line
            domain = self._get_order_line_search_domain(purchase, item)
            available_po_lines = po_line_obj.search(domain)
            new_pr_line = True
            if available_po_lines and not item.keep_description:
                new_pr_line = False
                po_line = available_po_lines[0]
                po_line.purchase_request_lines = [(4, line.id)]
                po_line.move_dest_ids |= line.move_dest_ids
            else:
                po_line_data = self._prepare_purchase_requisition_line(purchase,
                                                                 item)
                if item.keep_description:
                    po_line_data['name'] = item.name
                po_line = po_line_obj.create(po_line_data)

            new_qty = pr_line_obj._calc_new_qty_purchase_requisition(
                line, po_line=po_line,
                new_pr_line=new_pr_line)
            po_line.product_qty = new_qty
            #po_line._onchange_quantity()
            # The onchange quantity is altering the scheduled date of the PO
            # lines. We do not want that:
            po_line.schedule_date = item.line_id.date_required
            if item.keep_price:
                po_line.price_unit = item.line_id.price_unit
            res.append(purchase.id)

        return {
            'domain': [('id', 'in', res)],
            'name': _('PurchaseTender'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'purchase.requisition',
            'view_id': False,
            'context': False,
            'type': 'ir.actions.act_window'
        }


class PurchaseRequestLineMakePurchaseRequisitionItem(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.requisition.item"
    _description = "Purchase Request Line Make Purchase Requisition Item"

    keep_price = fields.Boolean(string='Copy Price to new PA(QCF)',
                                help='Set true if you want to keep the '
                                     'price provided in the '
                                     'wizard in the new PA(QCF).', )
    price_unit = fields.Float(string='Price Unit', digits=dp.get_precision('Price Unit'))
