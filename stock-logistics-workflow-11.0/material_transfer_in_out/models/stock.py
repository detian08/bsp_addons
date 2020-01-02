# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round


class StockMove(models.Model):
    _inherit = 'stock.move'

    material_transfer_line_id = fields.Many2one('material.transfer.line',
                                                'Material Transfer Line',
                                                ondelete='set null',
                                                index=True,
                                                readonly=True)

    created_material_transfer_line_id = fields.Many2one('material.transfer.line',
                                                        'Stock Move for Outgoing Part of Material Transfer Line',
                                                        ondelete='set null',
                                                        readonly=True,
                                                        copy=False)
    receiving_material_transfer_line_id = fields.Many2one('material.transfer.line',
                                                          'Stock Move for Incoming Part of Material Transfer Line',
                                                          ondelete='set null',
                                                          readonly=True,
                                                          copy=False)

    @api.depends('move_line_ids')
    @api.multi
    def _get_aggr(self):
        for move in self:
            # for line in :
            debug = 0

    is_damage_aggr = fields.Boolean(String='Is Damage Product',
                                    readonly=True,
                                    compute='_get_aggr')
    damage_qty_aggr = fields.Float(String='Damage Qty',
                                   digits=dp.get_precision('Product Unit of Measure'),
                                   readonly=True,
                                   compute='_get_aggr')
    damage_uom_aggr = fields.Many2one(comodel_name='product.uom',
                                      string='Damaged Item UoM',
                                      readonly=True,
                                      compute='_get_aggr')

    is_not_match_aggr = fields.Boolean(String='Is Not Match Product',
                                       readonly=True,
                                       compute='_get_aggr')
    not_match_qty_aggr = fields.Float(String='Not Match Qty',
                                      digits=dp.get_precision('Product Unit of Measure'),
                                      readonly=True,
                                      compute='_get_aggr')
    not_match_uom_aggr = fields.Many2one('product.uom', 'Not Match Item UoM',
                                         readonly=True,
                                         compute='_get_aggr')


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    is_damage_line = fields.Boolean(String='Is Damage Product',
                                    default=False, )
    damage_qty_line = fields.Float(String='Damage Qty',
                                   digits=dp.get_precision('Product Unit of Measure'))
    damage_uom_line = fields.Many2one(comodel_name='product.uom',
                                      string='Damaged Item UoM')

    is_not_match_line = fields.Boolean(String='Is Not Match Product',
                                       default=False)
    not_match_qty_line = fields.Float(String='Not Match Qty', digits=dp.get_precision('Product Unit of Measure'),
                                      default=False)
    not_match_uom_line = fields.Many2one('product.uom', 'Not Match Item UoM',
                                         default=False)
    notes = fields.Text(string='Notes')

class EnhanceStockOverProcessedTransfer(models.TransientModel):
    _inherit = 'stock.overprocessed.transfer'

class EnhanceStockImmediateTransfer(models.TransientModel):
    _inherit = 'stock.immediate.transfer'

    def process(self):
        pick_to_backorder = self.env['stock.picking']
        pick_to_do = self.env['stock.picking']
        material_transfer_pointer = self.env['material.transfer']
        material_transfer_line_pointer = self.env['material.transfer.line']
        for picking in self.pick_ids:
            # If still in draft => confirm and assign
            if picking.state == 'draft':
                picking.action_confirm()
                if picking.state != 'assigned':
                    picking.action_assign()
                    if picking.state != 'assigned':
                        raise UserError(_("Could not reserve all requested products. Please use the \'Mark as Todo\' button to handle the reservation manually."))
            for move in picking.move_lines.filtered(lambda m: m.state not in ['done', 'cancel']):
                for move_line in move.move_line_ids:
                    move_line.qty_done = move_line.product_uom_qty
            if picking._check_backorder():
                pick_to_backorder |= picking
                continue
            pick_to_do |= picking
            debug = 0
            current_mto = material_transfer_pointer.search([('id','in',picking.material_transfer_id.ids)])
            if current_mto:
                for mto in current_mto:
                    mto.button_reassign_movement()
        # Process every picking that do not require a backorder, then return a single backorder wizard for every other ones.

        if pick_to_do:
            pick_to_do.action_done()
        if pick_to_backorder:
            return pick_to_backorder.action_generate_backorder_wizard()
        return False

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    material_transfer_id = fields.Many2one('material.transfer',
                                           related='move_lines.material_transfer_line_id.transfer_id',
                                           string="Material Transfer", readonly=True)

    @api.multi
    def button_validate(self):
        self.ensure_one()
        if not self.move_lines and not self.move_line_ids:
            raise UserError(_('Please add some lines to move'))

        # If no lots when needed, raise error
        picking_type = self.picking_type_id
        precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        no_quantities_done = all(float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in
                                 self.move_line_ids.filtered(lambda m: m.state not in ('done', 'cancel')))
        no_reserved_quantities = all(
            float_is_zero(move_line.product_qty, precision_rounding=move_line.product_uom_id.rounding) for move_line in
            self.move_line_ids)
        if no_reserved_quantities and no_quantities_done:
            raise UserError(_(
                'You cannot validate a transfer if you have not processed any quantity. You should rather cancel the transfer.'))

        if picking_type.use_create_lots or picking_type.use_existing_lots:
            lines_to_check = self.move_line_ids
            if not no_quantities_done:
                lines_to_check = lines_to_check.filtered(
                    lambda line: float_compare(line.qty_done, 0,
                                               precision_rounding=line.product_uom_id.rounding)
                )

            for line in lines_to_check:
                product = line.product_id
                if product and product.tracking != 'none':
                    if not line.lot_name and not line.lot_id:
                        raise UserError(_('You need to supply a lot/serial number for %s.') % product.display_name)

        if no_quantities_done:
            view = self.env.ref('stock.view_immediate_transfer')
            wiz = self.env['stock.immediate.transfer'].create({'pick_ids': [(4, self.id)]})
            return {
                'name': _('Immediate Transfer?'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.immediate.transfer',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }

        if self._get_overprocessed_stock_moves() and not self._context.get('skip_overprocessed_check'):
            view = self.env.ref('stock.view_overprocessed_transfer')
            wiz = self.env['stock.overprocessed.transfer'].create({'picking_id': self.id})
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.overprocessed.transfer',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }

        # Check backorder should check for other barcodes
        if self._check_backorder():
            return self.action_generate_backorder_wizard()
        self.action_done()
        if self.material_transfer_id:
        #     update move_dest_ids/move_receive_ids
            debug = 0
            current_mto = self.env['material.transfer'].search([('id','in',self.material_transfer_id.ids)])
            for mto in current_mto:
                mto.button_reassign_movement()
        return


class StockLocation(models.Model):
    _inherit = 'stock.location'
    related_dept = fields.Many2one(comodel_name='hr.department',
                                   string='Related Department',
                                   domain=lambda self: [('company_id', 'in', self.env.user.company_id.ids)])
