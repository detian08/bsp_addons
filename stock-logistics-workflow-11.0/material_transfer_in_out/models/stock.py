# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from addons import decimal_precision as dp


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

class BuktiPenerimaanFixedAsset(models.Model):
    _name = 'bukti.penerimaan.fixed.asset'
    bpfa_name = fields.Char(String='BPFA Number', default='New', readonly=True)
    bpfa_tgl_kirim = fields.Date(string='Tanggal Kirim',
                                 default=fields.Date.context_today,
                                 index=True)
    bpfa_tgl_terima = fields.Date(string='Tanggal Terima',
                                  default=fields.Date.context_today,
                                  index=True)
    bpfa_menyerahkan = fields.Many2one(comodel_name='hr.employee',
                                       string='Yang Menyerahkan')
    bpfa_menerima = fields.Many2one(comodel_name='hr.employee',
                                    string='Yang Menerima')
    bpfa_mengetahui = fields.Many2one(comodel_name='hr.employee',
                                      string='Mengetahui')
    # stock_picking_ids = fields.One2many(comodel_name=)
class StockPicking(models.Model):
    _inherit = 'stock.picking'

    material_transfer_id = fields.Many2one('material.transfer',
                                           related='move_lines.material_transfer_line_id.transfer_id',
                                           string="Material Transfer", readonly=True)
    bpfa_flag = fields.Boolean(string='Bukti Penerimaan Fixed Asset')
    bpfa_id = fields.Many2one(comodel_name='bukti.penerimaan.fixed.asset',
                              )
    
    bpfa_tgl_kirim = fields.Date(string='Tanggal Kirim',
                                 default=fields.Date.context_today,
                                 index=True)
    bpfa_tgl_terima = fields.Date(string='Tanggal Terima',
                                  default=fields.Date.context_today,
                                  index=True)
    bpfa_menyerahkan = fields.Many2one(comodel_name='hr.employee',
                                       string='Yang Menyerahkan')
    bpfa_menerima = fields.Many2one(comodel_name='hr.employee',
                                    string='Yang Menerima')
    bpfa_mengetahui = fields.Many2one(comodel_name='hr.employee',
                                      string='Mengetahui')

    # @api.model
    # def create(self, vals):
    #     # TDE FIXME: clean that brol
    #     defaults = self.default_get(['name', 'picking_type_id'])
    #     if vals.get('name', '/') == '/' and defaults.get('name', '/') == '/' and vals.get('picking_type_id', defaults.get('picking_type_id')):
    #         vals['name'] = self.env['stock.picking.type'].browse(vals.get('picking_type_id', defaults.get('picking_type_id'))).sequence_id.next_by_id()
    #
    #     # TDE FIXME: what ?
    #     # As the on_change in one2many list is WIP, we will overwrite the locations on the stock moves here
    #     # As it is a create the format will be a list of (0, 0, dict)
    #     if vals.get('move_lines') and vals.get('location_id') and vals.get('location_dest_id'):
    #         for move in vals['move_lines']:
    #             if len(move) == 3 and move[0] == 0:
    #                 move[2]['location_id'] = vals['location_id']
    #                 move[2]['location_dest_id'] = vals['location_dest_id']
    #     res = super(Picking, self).create(vals)
    #     res._autoconfirm_picking()
    #     return res
    @api.model
    def create(self, vals):
        if self.bpfa_flag:
            # create BPFA Name
            res = super(StockPicking, self).create(vals)
        else:
            res = super(StockPicking, self).create(vals)

class StockLocation(models.Model):
    _inherit = 'stock.location'
    related_dept = fields.Many2one(comodel_name='hr.department',
                                   string='Related Department',
                                   domain=lambda self: [('company_id', 'in', self.env.user.company_id.ids)])
