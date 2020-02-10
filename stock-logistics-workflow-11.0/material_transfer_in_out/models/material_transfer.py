from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare
from odoo.tools.misc import formatLang

from odoo import exceptions

MATERIAL_STATES = [
    ('draft', 'Draft'),
    ('open', 'In progress'),
    ('done', 'Done'),
    ('cancel', 'Cancelled')]


class PurchaseRequest(models.Model):
    _inherit = "purchase.request"

    @api.multi
    @api.depends('name')
    def name_get(self):
        result = []
        for pr in self:
            name = pr.name
            if self.env.context.get('show_pr_name_dept') and pr.department_id:
                name += ': ' + pr.department_id.name
            result.append((pr.id, name))
        return result


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.multi
    @api.depends('name', 'partner_ref')
    def name_get(self):
        result = []
        for po in self:
            name = po.name
            if po.partner_ref:
                name += ' (' + po.partner_ref + ')'
            if self.env.context.get('show_total_amount') and po.amount_total:
                name += ': ' + formatLang(self.env, po.amount_total, currency_obj=po.currency_id)
            if self.env.context.get('show_department_name') and po.department_name:
                name += ': ' + po.department_name
            result.append((po.id, name))
        return result


class MaterialTransfer(models.Model):
    _name = 'material.transfer'
    _description = 'material transfer'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def _company_get(self):
        company_id = self.env['res.company']._company_default_get(self._name)
        return self.env['res.company'].browse(company_id.id)

    # @api.onchange('name')
    # def _domain_picking_type(self):

    @api.multi
    def _default_picking_type(self):
        # self.ensure_one()

        # locations = self.env['stock.locations']
        type_obj = self.env['stock.picking.type']
        company_id = self.env.context.get('company_id') or \
                     self.env.user.company_id.id
        if self.env.user.employee_ids[0].department_id:
            debug = True
            types = type_obj.search([('code', '=', 'internal'),
                                     ('warehouse_id.company_id', '=', company_id),
                                     ('department_ids', 'in', self.env.user.employee_ids[0].department_id.ids)])
        else:
            types = type_obj.search([('code', '=', 'internal'),
                                     ('warehouse_id.company_id', '=', company_id)])
        if not types:
            types = type_obj.search([('code', '=', 'incoming'),
                                     ('warehouse_id', '=', False)])
        # self.picking_type_id = types[:1]
        picking_type = types[:1]
        for mto in self:
            if not mto.picking_type_id:
                mto.picking_type_id = picking_type.ids
        # return types[:1]
        return picking_type

    @api.depends('line_ids.move_ids.returned_move_ids',
                 'line_ids.move_ids.state',
                 'line_ids.move_ids.picking_id')
    def _compute_picking(self):
        for mt_order in self:
            pickings = self.env['stock.picking']
            for line in mt_order.line_ids:
                # We keep a limited scope on purpose. Ideally, we should also use move_orig_ids and
                # do some recursive search, but that could be prohibitive if not done correctly.
                moves = line.move_ids | line.move_ids.mapped('returned_move_ids')
                pickings |= moves.mapped('picking_id')
            mt_order.picking_ids = pickings
            mt_order.picking_count = len(pickings)

    name = fields.Char(String='MT Number', default='New', readonly=True)
    state = fields.Selection(selection=MATERIAL_STATES, string='Status',
                             copy=False, default='draft', index=True,
                             readonly=True, track_visibility='onchange',
                             )
    transfer_date = fields.Date(String='Transfer Date',
                                required=True,
                                default=fields.Date.context_today,
                                index=True,
                                states={'draft': [('readonly', False)]},
                                track_visibility='onchange')
    department_id = fields.Many2one('hr.department',
                                    'Requesting Department',
                                    states={'draft': [('readonly', False)]},
                                    track_visibility='onchange',
                                    # required=True
                                    )
    request_id = fields.Many2one('purchase.request',
                                 String='Purchase Request',
                                 states={'draft': [('readonly', False)]},
                                 domain=lambda self: [('id', 'in', self._get_default_purchase_request())],
                                 track_visibility='onchange',
                                 )
    order_id = fields.Many2one('purchase.order',
                               String='Purchase Order',
                               states={'draft': [('readonly', False)]},
                               # domain=[('state', 'in', ['purchase'])],
                               domain=lambda self: [('id', 'in', self._get_default_purchase_order())],
                               track_visibility='onchange',
                               # required=True
                               )
    line_ids = fields.One2many('material.transfer.line',
                               'transfer_id',
                               'Products to Transfer',
                               readonly=False,
                               copy=True, )
    picking_count = fields.Integer(compute='_compute_picking', string='Transfer',
                                   default=0, store=True,
                                   compute_sudo=True)
    # picking_ids = fields.Many2many('stock.picking',
    picking_ids = fields.One2many(comodel_name='stock.picking',
                                  inverse_name='material_transfer_id',
                                  compute='_compute_picking',
                                  string='Transfer',
                                  copy=False,
                                  store=True, compute_sudo=True)
    final_location = fields.Many2one('stock.location', 'Destination Location', required=True)
    picking_type_id = fields.Many2one('stock.picking.type',
                                      'Picking Type', required=True,
                                      default=_default_picking_type,
                                      states={'draft': [('readonly', False)]},
                                      track_visibility='onchange'
                                      )

    company_id = fields.Many2one('res.company', 'Company',
                                 required=True,
                                 default=_company_get,
                                 states={'draft': [('readonly', False)]}, )
    sender_employee = fields.Many2one('hr.employee', string='Karyawan Pengirim')
    receiver_employee = fields.Many2one('hr.employee', string='Karyawan Penerima')
    assigned_to = fields.Many2one(
        'res.users', 'Approver', track_visibility='onchange',
        domain=lambda self: [('groups_id', 'in', self.env.ref(
            'purchase_request.group_purchase_request_manager').id)]
    )
    notes = fields.Text(string='Material Transfer Notes')

    bpfa_flag = fields.Boolean(string='is BPFA',
                               index=True)
    bpfa_name = fields.Char(string='No. BPFA', default='New')
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

    # @api.onchange('order_id')
    # def _order_id_onchange(self):
    #     if self.order_id:
    #         order = self.order_id
    #         self.request_id = order.order_line.purchase_request_lines[0].purchase_request_line_id
    # return {'domain': {'product_uom_id': [('category_id', '=', product.uom_id.category_id.id)]}}
    # self._add_domain()

    # @api.multi
    # def _add_domain(self):
    #     req_line_ids = []
    #     for line in self.order_id.order_line:
    #         req_line_ids += line.purchase_request_lines.ids
    #     if len(req_line_ids) > 0:
    #         domain = [('id', 'in', req_line_ids)]
    #     else:
    #         domain = [('id', '=', -1)]
    #     res = {'domain': {'request_id': str(domain)}}
    #     return res

    @api.multi
    def _prepare_material_transfer_lines(self, product_id, product_qty, product_uom):
        test = 0
        return {'product_id': product_id,
                'product_qty': product_qty,
                'product_uom': product_uom}

    @api.multi
    def _add_product_material_transfer_lines_by_po(self, order_id):
        self.ensure_one()

        product_ids = [x.product_id.id for x in self.line_ids if x]  # already inputted product
        mto_lines = []
        # for order in order_id:
        debug = True
        for oline in order_id.order_line:
            mto_line = self._prepare_material_transfer_lines(oline.product_id.id,
                                                             oline.product_qty,
                                                             oline.product_uom.id)
            if oline.product_id.id in product_ids:
                mto_lines.append((1, 0, mto_line))
                product_ids.remove(oline.product_id.id)
            else:
                mto_lines.append((0, 0, mto_line))
        if len(product_ids) > 0:
            mto_lines.append((6, 0, product_ids))
        self.line_ids = mto_lines

    @api.multi
    def _add_product_material_transfer_lines(self, request_id):
        self.ensure_one()
        order_id = self.order_id
        order_lines = []
        product_ids = [x.product_id.id for x in self.line_ids if x]
        for oline in order_id.order_line:
            # jika ada Purchase Request untuk PO yang dipilih
            if request_id:
                prlines = oline.purchase_request_lines
                if len(prlines) > 0:
                    for x in prlines:
                        if x.request_id == request_id:
                            vals = self._prepare_material_transfer_lines(oline.product_id.id,
                                                                         oline.product_qty,
                                                                         oline.product_uom.id)
                            if oline.product_id.id in product_ids:
                                order_lines.append((1, 0, vals))  # update
                                product_ids.remove(oline.product_id.id)
                            else:
                                order_lines.append((0, 0, vals))  # add
            # PO tanpa Purchase Request
            else:
                vals = self._prepare_material_transfer_lines(oline.product_id.id, oline.product_qty,
                                                             oline.product_uom.id)
                if oline.product_id.id in product_ids:
                    order_lines.append((1, 0, vals))
                    product_ids.remove(oline.product_id.id)
                else:
                    order_lines.append((0, 0, vals))
        if len(product_ids) > 0:
            order_lines.append((6, 0, product_ids))
        self.line_ids = order_lines

    @api.onchange('picking_type_id')
    def _set_sender_employee(self):
        debug = True
        domain_val = {}
        if self.picking_type_id:
            if self.picking_type_id.department_ids:
                employees = self.env['hr.employee'].search(
                    [('department_id', 'in', self.picking_type_id.department_ids.ids)])
            else:
                employees = self.env['hr.employee'].search(
                    [('company_id', '=', self.env.user.company_id.id)])
            # domain_val = {'domain': {'sender_employee': [('id', 'in', emp_ids)]}}
        else:
            employees = self.env['hr.employee'].search([('company_id', '=', self.env.user.company_id.id)])
        domain_val = {'domain': {'sender_employee': [('id', 'in', employees.ids)]}}
        return domain_val

    @api.onchange('final_location')
    def _set_receiver_employee(self):
        debug = True
        domain_val = {}
        if self.final_location:
            employees = self.env['hr.employee'].search(
                [('department_id', 'in', self.final_location.related_dept.ids)])
        else:
            employees = self.env['hr.employee'].search([('company_id', '=', self.env.user.company_id.id)])
        domain_val = {'domain': {'receiver_employee': [('id', 'in', employees.ids)]}}
        return domain_val

    @api.onchange('department_id', 'name')
    def _department_id_onchange(self):
        test = 0
        if self.department_id:
            return {'domain':
                        {'request_id': [('department_id', '=', self.department_id.id)],
                         'final_location': ['|',
                                            ('related_dept', 'in', self.department_id.ids),
                                            ('company_id', 'in', self.department_id.company_id.ids)
                                            ]
                         }
                    }
        else:
            return {'domain':
                        {'request_id': [('company_id', '=', self.env.user.company_id.id)],
                         'order_id': [('company_id', '=', self.env.user.company_id.id)],
                         }
                    }

    @api.onchange('request_id', 'name')
    def _request_id_onchange(self):
        test = 0
        if self.request_id:
            pr = self.request_id
            emp_ids = [-1]
            po_ids = []
            for pr_line in pr.line_ids:
                for po_lines in pr_line.purchase_lines:
                    po_ids.append(po_lines.order_id.id)
            # po_ids = pr.line_ids.purchase_lines.order_id.ids
            list_of_po = self.env['purchase.order'].search([('id', 'in', po_ids), ('state', '=', 'done')])
            if self.department_id:
                emp_ids = self.env['hr.employee'].search([('company_id', '=', self.env.user.company_id.id)]).ids
            else:
                emp_ids = self.env['hr.employee'].search([('company_id', '=', self.env.user.company_id.id)]).ids
            return {'domain':
                        {'order_id': [('id', 'in', list_of_po.ids)],
                         # 'receiver_employee': [('id', 'in', emp_ids)]
                         }
                    }
        else:  # empty request id
            if self.department_id:
                return {'domain':
                            {'request_id': [('department_id', '=', self.department_id.id)],
                             'order_id': [('company_id', '=', self.env.user.company_id.id)],
                             }
                        }
            else:  # empty department
                return {'domain':
                            {'request_id': [('company_id', '=', self.env.user.company_id.id)],
                             'order_id': [('company_id', '=', self.env.user.company_id.id)],
                             # 'receiver_employee': [('company_id', '=', self.env.user.company_id.id)]
                             }
                        }

    def _get_default_purchase_order(self):
        if self.department_id:
            valid_po = self.env['purchase.order'].search([('department_name', 'in', self.department_id.name),
                                                          ('state', 'in', ['purchase'])]).ids
            return valid_po

    def _get_default_purchase_request(self):
        if self.department_id:
            valid_pr = self.env['purchase.request'].search([('handover_doc_dept', '=', self.department_id.id),
                                                            ('state', 'in', ['approved'])]).ids
            return valid_pr

    @api.onchange('order_id', 'name')
    def _order_id_onchange(self):
        test = 0
        if self.order_id:
            self.line_ids = [(5, 0, 0)]  # clear the lines
            self._add_product_material_transfer_lines_by_po(self.order_id)
        else:
            if self.department_id:
                return {'domain':
                            {'request_id': [('department_id', '=', self.department_id.id)],
                             # 'receiver_employee': [('company_id', '=', self.env.user.company_id.id)],
                             'order_id': [('company_id', '=', self.env.user.company_id.id)],
                             }
                        }
            else:  # empty department id
                return {'domain':
                            {'request_id': [('company_id', '=', self.env.user.company_id.id)],
                             'order_id': [('company_id', '=', self.env.user.company_id.id)],
                             # 'receiver_employee': [('company_id', '=', self.env.user.company_id.id)]
                             }
                        }

    @api.multi
    def _get_destination_location(self):
        test = 0
        self.ensure_one()
        return self.picking_type_id.default_location_dest_id.id

    @api.multi
    def _get_receive_picking_type(self, outgoing_picking):
        receive_picking_type = self.env['stock.picking.type'].search(
            [('default_location_src_id', '=', outgoing_picking.location_dest_id.id),
             ('default_location_dest_id', '=', self.final_location.id)])
        return receive_picking_type

    @api.multi
    def _get_source_location(self):
        test = 0
        self.ensure_one()
        return self.picking_type_id.default_location_src_id.id

    @api.model
    def _prepare_picking(self):
        # create outgoing
        is_dest_transit_loc = self._is_dest_transit_loc()
        picking_values = {}
        if is_dest_transit_loc:  # melalui virtual transit
            picking_values = {
                'picking_type_id': self.picking_type_id.id,
                'date': self.transfer_date,
                'origin': self.name,
                'location_dest_id': self._get_destination_location(),
                'location_id': self._get_source_location(),
                'company_id': self.company_id.id,
                # 'material_transfer_id':self.id
                'date_done': self.transfer_date,
            }
        else:  # langsung
            picking_values = {
                'picking_type_id': self.picking_type_id.id,
                'date': self.transfer_date,
                'origin': self.name,
                'location_dest_id': self._get_destination_location(),
                'location_id': self._get_source_location(),
                'company_id': self.company_id.id,
                # 'material_transfer_id':self.id
                'date_done': self.transfer_date,
                'receiving_dept': self.picking_type_id.default_location_dest_id.related_dept.id,
                'receiving_employee': self.receiver_employee.id
            }
        return picking_values

    # @api.multi
    # def _get_receive_source_location(self,outgoing_picking):
    #     test = 0
    #     self.ensure_one()
    #     receive_picking_type = self._get_receive_picking_type(outgoing_picking)
    #     receive_source = receive_picking_type.default_location_src_id
    #     return receive_source

    @api.model
    def _prepare_receive_picking(self, outgoing_picking):
        if self.final_location:
            picking_type_id = self._get_receive_picking_type(outgoing_picking)
            location_id = picking_type_id.default_location_src_id

            receive_picking_data = {
                'material_transfer_id': self.id,
                'picking_type_id': picking_type_id.id,
                'date': fields.Date.today(),
                'origin': self.name,
                'location_dest_id': self.final_location.id,
                'location_id': location_id.id,
                'company_id': self.company_id.id,
            }
            return receive_picking_data
        else:
            raise exceptions.ValidationError('Final Location Empty')

    @api.multi
    def action_view_picking(self):
        '''
        This function returns an action that display existing picking orders of given purchase order ids.
        When only one found, show the picking immediately.
        '''
        action = self.env.ref('stock.action_picking_tree_all')
        result = action.read()[0]

        # override the context to get rid of the default filtering on operation type
        result['context'] = {}
        pick_ids = self.mapped('picking_ids')
        # choose the view_mode accordingly
        if not pick_ids or len(pick_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % (pick_ids.ids)
        elif len(pick_ids) == 1:
            res = self.env.ref('stock.view_picking_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = pick_ids.id
        material_transfer_dict = dict(transfer_id=self.name)
        material_transfer_dict.update(create=False, delete=False, menu=False)
        result['context'] = material_transfer_dict
        return result

    @api.multi
    def _create_picking(self):
        StockPicking = self.env['stock.picking']
        for order in self:
            if any([ptype in ['product', 'consu'] for ptype in order.line_ids.mapped('product_id.type')]):
                # picking untuk Material Transfer Order dengan status bukan done/cancel
                pickings = order.picking_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
                if not pickings:  # sudah ada PO namun belum ada penerimaan item barang PO
                    res = order._prepare_picking()
                    # check jika ada transit location, tambahkan 1 transaksi
                    picking = StockPicking.create(res)
                else:
                    picking = pickings[0]
                moves = order.line_ids._create_stock_moves(picking)
                if moves:
                    moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
                    seq = 0
                    for move in sorted(moves, key=lambda move: move.date_expected):
                        seq += 5
                        move.sequence = seq
                    moves._action_assign()
                    picking.message_post_with_view('mail.message_origin_link',
                                                   values={'self': picking,
                                                           'origin': order},
                                                   subtype_id=self.env.ref('mail.mt_note').id)

                    for stock_move in moves:
                        order.write({
                            'move_dest_ids': [(0, 0, stock_move.ids)]
                        })

        return True

    @api.multi
    def _create_picking_ret_list(self):
        picking_retval = []
        StockPicking = self.env['stock.picking']
        for order in self:
            if any([ptype in ['product', 'consu'] for ptype in order.line_ids.mapped('product_id.type')]):
                # picking untuk Material Transfer Order dengan status bukan done/cancel
                pickings = order.picking_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
                if not pickings:  # sudah ada PO namun belum ada penerimaan item barang PO
                    res = order._prepare_picking()
                    # check jika ada transit location, tambahkan 1 transaksi
                    picking = StockPicking.create(res)
                else:
                    picking = pickings[0]
                moves = order.line_ids._create_stock_moves(picking)
                if moves:
                    moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
                    seq = 0
                    for move in sorted(moves, key=lambda move: move.date_expected):
                        seq += 5
                        move.sequence = seq
                    moves._action_assign()
                    picking.message_post_with_view('mail.message_origin_link',
                                                   values={'self': picking,
                                                           'origin': order},
                                                   subtype_id=self.env.ref('mail.mt_note').id)

                    for stock_move in moves:
                        order.write({
                            'move_dest_ids': [(0, 0, stock_move.ids)]
                        })

                    picking_retval.append(picking)
        return picking_retval

    @api.multi
    def _create_finalize_picking(self, outgoing_pickings):
        StockPickingPointer = self.env['stock.picking']
        StockMovePointer = self.env['stock.move']
        for mto in self:
            for picking in outgoing_pickings:
                incoming_picking_vals = self._prepare_receive_picking(picking)
                incoming_picking_res = StockPickingPointer.create(incoming_picking_vals)
                if incoming_picking_res != False:
                    stock_moves_res = mto.line_ids._create_stock_moves_receive(incoming_picking_res)
                    if stock_moves_res:
                        stock_moves_res = stock_moves_res.filtered(
                            lambda x: x.state not in ('done', 'cancel'))._action_confirm()
                        seq = 0
                        for move in sorted(stock_moves_res, key=lambda move: move.date_expected):
                            seq += 5
                            move.sequence = seq
                        stock_moves_res._action_assign()
                        incoming_picking_res.message_post_with_view('mail.message_origin_link',
                                                                    values={'self': incoming_picking_res,
                                                                            'origin': mto},
                                                                    subtype_id=self.env.ref('mail.mt_note').id)
                        for stock_move in stock_moves_res:
                            mto.write({
                                'move_receive_ids': [(0, 0, stock_move.ids)]
                            })
        return True

    @api.multi
    def button_reassign_movement(self, force=False):
        if self.state in ['done', 'open']:
            if self.line_ids:  # ada line id
                for mto_line in self.line_ids:
                    if mto_line.move_ids:  # ada movement
                        debug = 0
                        update_out_val = []
                        update_in_val = []
                        for move in mto_line.move_ids:
                            if '/OUT/' in move.reference:
                                search_res = mto_line.move_dest_ids.filtered(lambda x: x.id == move.id)
                                if not search_res:
                                    mto_line.write({'move_dest_ids': [(6, 0, move.ids)]})
                            elif '/IN/' in move.reference:
                                search_res = mto_line.move_receive_ids.filtered(lambda x: x.id == move.id)
                                if not search_res:
                                    mto_line.write({'move_receive_ids': [(6, 0, move.ids)]})
        for line in self.line_ids:
            line._count_quantity()

    @api.onchange('picking_type_id')
    def _onchange_picking_type_set_dest(self):
        # retval_value = False
        if not self.picking_type_id.default_location_dest_id.usage == 'transit':
            self.final_location = self.picking_type_id.default_location_dest_id.id
        else:
            self.final_location = {}
        # return retval_value

    @api.multi
    def button_create_picking(self, force=False):
        is_error = False
        self.ensure_one()
        for line_item in self.line_ids:
            if line_item.product_avail_qty <= 0:
                is_error = True
                break

        if not self.picking_ids and not is_error:
            is_dest_transit_loc = self._is_dest_transit_loc()
            outgoing_picking = []
            outgoing_picking = self._create_picking_ret_list()
            if is_dest_transit_loc:
                self._create_finalize_picking(outgoing_picking)
            return True
        else:
            if is_error:
                raise exceptions.ValidationError('Negative or Zero available quantity')
            else:
            #         sudah ada picking
                raise exceptions.ValidationError('Picking(s) already exist')

    def _is_dest_transit_loc(self):
        retval_value = False
        if self.picking_type_id.default_location_dest_id.usage == 'transit':
            retval_value = True
        return retval_value

    @api.multi
    def button_finish_picking(self, force=False):
        # self.button_reassign_movement()
        test = 0
        if self.final_location:
            # check udah pernah ada picking ke Intra/Inter Company
            for mto in self:
                outgoing_picking = self.env['stock.picking'].search([('id', 'in', mto.picking_ids.ids),
                                                                     ('state', '=', 'done'),
                                                                     ('picking_type_id', '=', mto.picking_type_id.ids)])
                if outgoing_picking:
                    self._create_finalize_picking(outgoing_picking)
                else:
                    raise exceptions.ValidationError('Create Outgoing Picking First')
        else:
            raise exceptions.ValidationError('Final Location Empty')
        # self.button_reassign_movement()
        return {}

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('material.transfer') or '/'
            if vals.get('bpfa_flag') == True and vals.get('bpfa_name', 'New') == 'New':
                vals['bpfa_name'] = self.env['ir.sequence'].next_by_code('mt.bpfa') or '/'
        mtransfer = super(MaterialTransfer, self).create(vals)
        if vals.get('assigned_to'):
            mtransfer.message_subscribe_users(user_ids=[mtransfer.assigned_to.id])
        return mtransfer

    @api.multi
    def write(self, vals):
        if vals.get('bpfa_flag') == True \
                and (vals.get('bpfa_name', 'New') == 'New'
                     or vals.get('bpfa_name') == '/'):
            vals['bpfa_name'] = self.env['ir.sequence'].next_by_code('mt.bpfa') or '/'
        res = super(MaterialTransfer, self).write(vals)
        for mtransfer in self:
            if vals.get('assigned_to'):
                self.message_subscribe_users(user_ids=[mtransfer.assigned_to.id])
        return res

    @api.multi
    def action_confirm(self):
        self.write({'state': 'open'})
        return True

    def action_draft(self):
        self.write({'state': 'draft'})
        return True

    def action_cancel(self):
        self.write({'state': 'cancel'})
        return True

    def action_done(self):
        self.write({'state': 'done'})
        return True


class MaterialTransferLine(models.Model):
    _name = 'material.transfer.line'
    _description = 'material transfer line'

    transfer_id = fields.Many2one('material.transfer',
                                  String='Material Transfer',
                                  ondelete='cascade',
                                  readonly=True)
    product_id = fields.Many2one('product.product',
                                 String='Product')

    product_avail_qty = fields.Float(String='Available Quantity',
                                     readonly=True,
                                     track_visibility='onchange',
                                     compute='_count_avail')
    product_avail_uom = fields.Many2one('product.uom',
                                        String='Available Quantity UoM',
                                        readonly=True,
                                        track_visibility='onchange',
                                        compute='_count_avail')

    product_qty = fields.Float(String='Quantity', track_visibility='onchange')
    product_uom = fields.Many2one('product.uom',
                                  String='Product Unit of Measure',
                                  required=True, track_visibility='onchange')
    retrieved_qty = fields.Float(String='Retrieved Qty',
                                 readonly=True,
                                 compute='_count_quantity',
                                 track_visibility='onchange')
    retrieved_uom = fields.Many2one('product.uom',
                                    String='Retrieved UoM',
                                    readonly=True,
                                    compute='_count_quantity',
                                    track_visibility='onchange')
    delivered_qty = fields.Float(String='Delivered Qty',
                                 readonly=True,
                                 compute='_count_quantity',
                                 track_visibility='onchange')
    delivered_uom = fields.Many2one('product.uom',
                                    String='Delivered UoM',
                                    track_visibility='onchange')
    is_damage = fields.Boolean(String='Is Damage Product', default=False)
    damage_qty = fields.Float(String='Damage Qty', )
    damage_uom = fields.Many2one('product.uom',
                                 String='Damaged UoM',
                                 track_visibility='onchange')
    is_not_match = fields.Boolean(String='Is Not Match Product', default=False,
                                  track_visibility='onchange')
    not_match_qty = fields.Float(String='Not Match Qty', track_visibility='onchange')
    not_match_uom = fields.Many2one('product.uom',
                                    String='Not Match UoM',
                                    track_visibility='onchange')
    description = fields.Char(String="Description")
    # all stock move
    move_ids = fields.One2many('stock.move',
                               'material_transfer_line_id',
                               string='Transfer Reservation',
                               readonly=True,
                               ondelete='set null',
                               copy=False)
    # outgoing stock move
    move_dest_ids = fields.One2many('stock.move',
                                    'created_material_transfer_line_id',
                                    'Downstream Moves')
    # incoming stock move
    move_receive_ids = fields.One2many('stock.move',
                                       'receiving_material_transfer_line_id',
                                       'Finalization Moves')

    @api.onchange('product_id')
    def _product_id_onchange(self):
        product = self.product_id
        self.product_uom = self.product_id.uom_id.id
        stock_quant_pointer = self.env['stock.quant'].search([('product_id', '=', self.product_id.id),
                                                              ('location_id', '=',
                                                               self.transfer_id.picking_type_id.default_location_src_id.id)])
        if stock_quant_pointer:
            self.product_avail_qty = stock_quant_pointer[0].quantity
            self.product_avail_uom = stock_quant_pointer[0].product_uom_id

        # calculate retrieved qty,retrieved uom
        # calculate delivered qty, delivered uom,
        # is damaged, damaged qty, damaged Uom
        # is not match, not match qty, not match Uom
        return {'domain': {'product_uom': [('category_id', '=', product.uom_id.category_id.id)]}}

    @api.multi
    def _prepare_stock_moves_receive(self, picking):
        self.ensure_one()
        res = []
        if self.product_id.type not in ['product', 'consu']:
            return res
        else:
            qty_all = 0.0
            price_unit = 0.0
            # filtered_moves = self.move_ids.filtered(lambda x: x.state != 'cancel' and not x.location_dest_id.usage == "supplier") #bukan retur
            filtered_moves = self.move_receive_ids.filtered(
                lambda x: x.state != 'cancel' and not x.location_dest_id.usage == "supplier")  # bukan retur
            for move in filtered_moves:
                # calculate all quantity
                qty_all += move.product_uom._compute_quantity(move.product_uom_qty,
                                                              self.product_uom,
                                                              rounding_method='HALF-UP')

            template = {
                # truncate to 2000 to avoid triggering index limit error
                # TODO: remove index in master?
                'name': (self.product_id.name or '')[:2000],
                'product_id': self.product_id.id,
                'product_uom': self.product_uom.id,
                'date': fields.Date.today(),  # change to today
                'location_id': self.transfer_id._get_destination_location(),  # get source from previous destination
                'location_dest_id': self.transfer_id.final_location.id,  # get destination from user input
                'picking_id': picking.id,
                # 'partner_id': self.order_id.dest_address_id.id,
                'move_receive_ids': [(4, x) for x in self.move_receive_ids.ids],
                'state': 'draft',
                'material_transfer_line_id': self.id,
                'company_id': self.transfer_id.company_id.id,
                'price_unit': price_unit,
                'picking_type_id': self.transfer_id._get_receive_picking_type(picking).id,
                # 'group_id': self.order_id.group_id.id,
                'origin': self.transfer_id.name,
                'route_ids': self.transfer_id._get_receive_picking_type(picking).warehouse_id and [
                    (6, 0,
                     [x.id for x in self.transfer_id._get_receive_picking_type(picking).warehouse_id.route_ids])] or [],
                'warehouse_id': self.transfer_id._get_receive_picking_type(picking).warehouse_id.id,
            }
            diff_quantity = self.product_qty - qty_all
            if float_compare(diff_quantity, 0.0, precision_rounding=self.product_uom.rounding) > 0:
                quant_uom = self.product_id.uom_id
                get_param = self.env['ir.config_parameter'].sudo().get_param
                if self.product_uom.id != quant_uom.id and get_param('stock.propagate_uom') != '1':
                    product_qty = self.product_uom._compute_quantity(diff_quantity, quant_uom,
                                                                     rounding_method='HALF-UP')
                    template['product_uom'] = quant_uom.id
                    template['product_uom_qty'] = product_qty
                else:
                    template['product_uom_qty'] = diff_quantity
                res.append(template)
            return res

    @api.multi
    def _prepare_stock_moves(self, picking):
        """ Prepare the stock moves data for one order line. This function returns a list of
        dictionary ready to be used in stock.move's create()
        """
        self.ensure_one()
        res = []
        if self.product_id.type not in ['product', 'consu']:
            return res
        qty = 0.0
        # price_unit = self._get_stock_move_price_unit()
        price_unit = 0.0
        filtered_moves = self.move_dest_ids.filtered(
            lambda x: x.state != 'cancel' and not x.location_dest_id.usage == "supplier")
        for move in filtered_moves:
            qty += move.product_uom._compute_quantity(move.product_uom_qty, self.product_uom, rounding_method='HALF-UP')

        template = {
            # truncate to 2000 to avoid triggering index limit error
            # TODO: remove index in master?
            'name': (self.product_id.name or '')[:2000],
            'product_id': self.product_id.id,
            'product_uom': self.product_uom.id,
            'date': self.transfer_id.transfer_date,
            # 'date_expected': self.date_planned,
            'location_id': self.transfer_id._get_source_location(),
            'location_dest_id': self.transfer_id._get_destination_location(),
            'picking_id': picking.id,
            # 'partner_id': self.order_id.dest_address_id.id,
            'move_dest_ids': [(4, x) for x in self.move_dest_ids.ids],
            'state': 'draft',
            'material_transfer_line_id': self.id,
            'company_id': self.transfer_id.company_id.id,
            'price_unit': price_unit,
            'picking_type_id': self.transfer_id.picking_type_id.id,
            # 'group_id': self.order_id.group_id.id,
            'origin': self.transfer_id.name,
            'route_ids': self.transfer_id.picking_type_id.warehouse_id and [
                (6, 0, [x.id for x in self.transfer_id.picking_type_id.warehouse_id.route_ids])] or [],
            'warehouse_id': self.transfer_id.picking_type_id.warehouse_id.id,
        }
        diff_quantity = self.product_qty - qty
        if float_compare(diff_quantity, 0.0, precision_rounding=self.product_uom.rounding) > 0:
            quant_uom = self.product_id.uom_id
            get_param = self.env['ir.config_parameter'].sudo().get_param
            if self.product_uom.id != quant_uom.id and get_param('stock.propagate_uom') != '1':
                product_qty = self.product_uom._compute_quantity(diff_quantity, quant_uom, rounding_method='HALF-UP')
                template['product_uom'] = quant_uom.id
                template['product_uom_qty'] = product_qty
            else:
                template['product_uom_qty'] = diff_quantity
            res.append(template)
        return res

    @api.multi
    def _create_stock_moves(self, picking):
        moves = self.env['stock.move']
        done = self.env['stock.move'].browse()
        with self.env.norecompute():
            # update_vals = []
            for line in self:
                new_vals = []
                for val in line._prepare_stock_moves(picking):
                    create_res = moves.create(val)
                    # update_vals.append((0,0,create_res))
                    done += create_res
        self.recompute()
        # self.write({
        #     'move_dest_ids': update_vals
        # })
        return done

    @api.multi
    def _create_stock_moves_receive(self, picking):
        moves = self.env['stock.move']
        done = self.env['stock.move'].browse()
        with self.env.norecompute():
            # update_vals = []
            for line in self:
                for val in line._prepare_stock_moves_receive(picking):
                    create_res = moves.create(val)
                    # update_val = {}
                    # update_val.update({'move_receive_ids': [(0, 0, create_res)]})
                    # line.write(update_val)
                    # update_vals.append((0,0,create_res))
                    done += create_res
        self.recompute()
        # self.write({
        #     'move_receive_ids': update_vals
        # })
        return done

    @api.depends('product_id', 'transfer_id')
    def _count_avail(self):
        debug = 0
        for item in self:
            stock_quant_pointer = []
            if item.transfer_id.picking_type_id.default_location_src_id.id:
                stock_quant_pointer = self.env['stock.quant'].search([('product_id', '=', item.product_id.id),
                                                                      ('location_id', '=',
                                                                       item.transfer_id.picking_type_id.default_location_src_id.id)])
                if stock_quant_pointer:
                    item.product_avail_qty = stock_quant_pointer[0].quantity
                    item.product_avail_uom = stock_quant_pointer[0].product_uom_id

    @api.depends('move_ids')
    def _count_quantity(self):
        for line in self:
            if line.move_dest_ids:
                retrieved_qty = 0
                for move_out in self.move_dest_ids:
                    retrieved_qty += line.product_uom._compute_quantity(move_out.product_qty,
                                                                        move_out.product_uom,
                                                                        rounding_method='HALF-UP')
                line.retrieved_qty = retrieved_qty
                line.retrieved_uom = line.product_uom.id
                line.write({'retrieved_qty': retrieved_qty})
                line.write({'retrieved_uom': line.product_uom.id})
            if line.move_receive_ids:
                delivered_qty = 0
                for move_in in line.move_receive_ids:
                    delivered_qty += line.product_uom._compute_quantity(move_in.product_qty,
                                                                        move_in.product_uom,
                                                                        rounding_method='HALF-UP')
                line.delivered_qty = delivered_qty
                line.delivered_uom = line.product_uom.id
                line.write({'delivered_qty': delivered_qty})
                line.write({'delivered_uom': line.product_uom.id})
            #   get damaged
            damaged_qty = 0
            not_match_qty = 0
            sorted_moves = line.move_ids.sorted(key='write_date', reverse=True)
            if sorted_moves:
                last_move = sorted_moves[0]
                for move_line in last_move.move_line_ids:
                    if move_line.is_damage_line == True:
                        damaged_qty += line.product_uom._compute_quantity(move_line.damage_qty_line,
                                                                          move_line.damage_uom_line,
                                                                          rounding_method='HALF-UP')
                    if move_line.is_not_match_line == True:
                        not_match_qty += line.product_uom._compute_quantity(move_line.not_match_qty_line,
                                                                            move_line.not_match_uom_line,
                                                                            rounding_method='HALF-UP')
                if damaged_qty > 0:
                    line.write({'damage_qty': damaged_qty})
                    line.write({'is_damage': True})
                    line.write({'damage_uom': move_line.damage_uom_line})
                if not_match_qty > 0:
                    line.write({'not_match_qty': not_match_qty})
                    line.write({'not_match_uom': move_line.not_match_uom_line})
                    line.write({'is_not_match': True})
