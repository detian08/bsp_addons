from odoo import models, fields, api, _
from addons import decimal_precision as dp

# import logging
# Logger for debug
# _logger = logging.getLogger(__name__)

TEMPLATE_FIELDS = ['product_min_qty', 'product_max_qty', 'qty_multiple', 'group_id', 'company_id',
                   'lead_days', 'lead_type', 'warehouse_id', 'location_id']


#######################
# Orderpoint Template #
#######################
class CXOrderpointTemplate(models.Model):
    _name = "cx.orderpoint.template"
    _description = "Minimum Inventory Rule Template"

    name = fields.Char(string="Name", compute='name_compose',
                       store=False)
    active = fields.Boolean(string='Active', default=True)
    category_id = fields.Many2one(string='Product Category', comodel_name='product.category', copy=False,
                                  ondelete='cascade')
    attr_val_ids = fields.Many2many(string="Attribute Values",
                                    comodel_name='product.attribute.value',
                                    relation='cx_op_tpl_pr_attr_val_rel',
                                    column1='cx_op_template_id',
                                    column2='attr_val_id')
    product_min_qty = fields.Float(string='Minimum Quantity', digits=dp.get_precision('Product Unit of Measure'),
                                   required=True)
    product_max_qty = fields.Float(string='Maximum Quantity', digits=dp.get_precision('Product Unit of Measure'),
                                   required=True)
    qty_multiple = fields.Float(string='Qty Multiple', digits=dp.get_precision('Product Unit of Measure'),
                                default=1, required=True)
    group_id = fields.Many2one('procurement.group', 'Procurement Group', copy=False)
    company_id = fields.Many2one(string='Company', comodel_name='res.company', required=True,
                                 default=lambda self: self.env.user.company_id.id)
    lead_days = fields.Integer(sting='Lead Time', default=1)
    lead_type = fields.Selection(
        [('net', 'Day(s) to get the products'), ('supplier', 'Day(s) to purchase')], 'Lead Type',
        required=True, default='supplier')
    warehouse_id = fields.Many2one(comodel_name='stock.warehouse', string='Warehouse',
                                   ondelete="cascade", required=False)
    location_id = fields.Many2one(comodel_name='stock.location', string='Location',
                                  ondelete="cascade", required=False)
    rule_ids = fields.One2many(string="Related Rules", comodel_name='stock.warehouse.orderpoint',
                               inverse_name='template_id')
    rule_ids_count = fields.Integer(string="Rules Count", compute="_rule_ids_count")

    _sql_constraints = [('tmpl_name_uniq', 'unique(category_id, company_id)',
                         'Such template already exists for this company!')]

# -- Count related rules
    @api.depends('rule_ids')
    @api.multi
    def _rule_ids_count(self):
        for rec in self:
            rec.rule_ids_count = len(rec.rule_ids)

# -- Compose name
    @api.depends('category_id')
    @api.multi
    def name_compose(self):
        for rec in self:
            prefix = rec.category_id.name_get()[0][1] if rec.category_id else False
            if prefix:
                rec.name = prefix
            else:
                rec.name = _('Global')

# -- Compose name -- PRO
    @api.depends('category_id', 'attr_val_ids')
    @api.multi
    def name_compose_pro(self):
        self.ensure_one()
        prefix = self.category_id.name if self.category_id else False
        suffix = [attr_val_id.name for attr_val_id in self.attr_val_ids] if len(self.attr_val_ids) > 0 else False
        if not prefix and not suffix:
            self.name = False
        elif prefix and suffix:
            self.name = '%s > %s' % (prefix, suffix)
        elif prefix:
            self.name = prefix
        else:
            self.name = suffix

# -- Apply template
    @api.multi
    def apply_template(self):
        for rec in self:
            is_global = False
            if rec.category_id:
                # Local templates
                products = self.env['product.product'].search([('categ_id', '=', rec.category_id.id),
                                                               ('type', '=', 'product')])
            else:
                # Global template
                products = self.env['product.product'].search([('type', '=', 'product')])
                is_global = True

            # Apply template to products
            for product in products:
                # Get existing rules
                existing_rules = self.env['stock.warehouse.orderpoint'].search([('product_id', '=', product.id)])
                len_existing_rules = len(existing_rules)

                # Do not apply Global template if rules exist
                if is_global and len_existing_rules > 0 and len(existing_rules.filtered(lambda t: not t.template_id)) == 0:
                    continue

                vals = {
                    'product_id': product.id,
                    'template_id': rec.id,
                    'product_min_qty': rec.product_min_qty,
                    'product_max_qty': rec.product_max_qty,
                    'qty_multiple': rec.qty_multiple,
                    'group_id': rec.group_id.id,
                    'lead_days': rec.lead_days,
                    'lead_type': rec.lead_type,
                }
                if rec.warehouse_id:
                    vals.update({'warehouse_id': rec.warehouse_id.id})
                if rec.location_id:
                    vals.update({'location_id': rec.location_id.id})

                # Update existing reordering rules or create new
                if len_existing_rules > 0:
                    existing_rules.filtered("template_control").write(vals)
                else:
                    vals.update({'template_control': True})
                    self.env['stock.warehouse.orderpoint'].create(vals)

# -- Create
    @api.model
    def create(self, vals):

        res = super(CXOrderpointTemplate, self).create(vals)
        res.apply_template()
        return res

# -- Write
    @api.multi
    def write(self, vals):

        # Remove category and attribute values
        vals.pop('category_id', False)
        vals.pop('attr_val_ids', False)

        # Write
        res = super(CXOrderpointTemplate, self).write(vals)

        # Get new vals for rules
        rule_vals = {}

        for key in TEMPLATE_FIELDS:
            if key in vals:
                rule_vals.update({key: vals.get(key, False)})

        # Update all related rules
        if len(rule_vals) > 0:
            self.env['stock.warehouse.orderpoint'].search([('template_id', 'in', self.ids)]).write(rule_vals)

        return res

# -- Delete
    @api.multi
    def unlink(self):

        # Get products
        product_ids = self.mapped('rule_ids').mapped('product_id')

        # Delete templates
        res = super(CXOrderpointTemplate, self).unlink()

        # Re-apply template
        if len(product_ids) > 0:
            product_ids.reorder_rules_update()

        return res


##########################
# Minimum Inventory Rule #
##########################
class CXStockWarehouseOrderpoint(models.Model):
    _name = "stock.warehouse.orderpoint"
    _inherit = "stock.warehouse.orderpoint"

    template_id = fields.Many2one(string="Template", comodel_name='cx.orderpoint.template',
                                  ondelete='set null', auto_join=True)
    template_control = fields.Boolean(string="Control via Template",
                                      help="Modify rule automatically when template is modified\n")


####################
# Product Template #
####################
class CXProductTemplate(models.Model):
    _name = "product.template"
    _inherit = "product.template"

    no_auto_reorder = fields.Boolean(string="Don't create reordering rules from templates",
                                     help="Do not create reordering rules automatically.\n"
                                          "You can create reordering rules later manually")

# -- Create or Update reordering rules (minimum inventory)
    @api.multi
    def reorder_rules_update(self):
        """
        Automatically creates or updates existing reordering rules based on templates
        :return:
        """
        self.product_variant_ids.reorder_rules_update()

# -- Write
    @api.multi
    def write(self, vals):
        res = super(CXProductTemplate, self).write(vals)
        # Update reordering rules
        if 'categ_id' in vals:
            self.product_variant_ids.reorder_rules_update()
        return res


###################
# Product Product #
###################
class CXProductProduct(models.Model):
    _name = "product.product"
    _inherit = "product.product"

# -- Create
    @api.model
    def create(self, vals):
        res = super(CXProductProduct, self).create(vals)
        if not res.no_auto_reorder:
            res.reorder_rules_update()
        return res

# -- Write
    @api.multi
    def write(self, vals):
        res = super(CXProductProduct, self).write(vals)
        # Update reordering rules
        if 'categ_id' in vals:
            self.filtered(lambda rec: rec.no_auto_reorder is False).with_context(
                {'del_existing': True, 'attrs_only': False}).reorder_rules_update()
        elif 'attribute_value_ids' in vals:
            self.filtered(lambda rec: rec.no_auto_reorder is False).with_context(
                {'del_existing': True, 'attrs_only': True}).reorder_rules_update()
        return res

# -- Create or Update reordering rules (minimum inventory)
    @api.multi
    def reorder_rules_update(self):
        """
        Automatically creates or updates existing reordering rules based on templates
        :return:
        """

        # Check if attrs_only in vals. Attrs are limited to Pro version so avoid excessive computations
        if self._context.get("attrs_only", False):
            return

        # Get global template. Use this template in no other found
        templates = self.env['cx.orderpoint.template'].search([('category_id', '=', False)])
        global_template = templates[0] if len(templates) > 0 else False

        # Check if we need to delete existing reordering rules if no rule is found
        # This is used for "write" primary
        del_existing = self._context.get("del_existing", False)

        for rec in self:
            # Applied only to stockable products
            if not rec.type == 'product':
                continue

            # Check if auto creation is disabled
            if rec.no_auto_reorder:
                continue

            # Product Category Based
            templates = self.env['cx.orderpoint.template'].search([('category_id', '=', rec.categ_id.id)])

            # Use the first template found or fallback to global template
            if len(templates) > 0:
                template = templates[0]
            else:
                if global_template:
                    template = global_template
                else:
                    # Delete existing rules
                    if del_existing:
                        self.env['stock.warehouse.orderpoint'].search([('product_id', '=', rec.id),
                                                                       ('template_control', '=', True)]).unlink()
                    continue

            vals = {
                'product_id': rec.id,
                'template_id': template.id,
                'product_min_qty': template.product_min_qty,
                'product_max_qty': template.product_max_qty,
                'qty_multiple': template.qty_multiple,
                'group_id': template.group_id.id,
                'lead_days': template.lead_days,
                'lead_type': template.lead_type,
            }
            if template.warehouse_id:
                vals.update({'warehouse_id': template.warehouse_id.id})
            if template.location_id:
                vals.update({'location_id': template.location_id.id})

            # Update existing reordering rules or create new
            existing_rules = self.env['stock.warehouse.orderpoint'].search([('product_id', '=', rec.id)])
            if len(existing_rules) > 0:
                existing_rules.write(vals)
            else:
                vals.update({'template_control': True})
                self.env['stock.warehouse.orderpoint'].create(vals)
