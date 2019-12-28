# -*- coding: utf-8 -*-
# (C) 2013 Smile (<http://www.smile.fr>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
from odoo.modules.registry import Registry


def state_cleaner(method):
    def wrapper(self, cr, *args, **kwargs):
        res = method(self, cr, *args, **kwargs)
        env = api.Environment(cr, SUPERUSER_ID, {})
        if env.registry.get('smile.script.intervention'):
            cr.execute("select relname from pg_class "
                       "where relname='smile_script_intervention'")
            if cr.rowcount:
                env['smile.script.intervention'].search(
                    [('state', '=', 'running')]). \
                    write({'state': 'exception'})
        return res
    return wrapper


class ScriptIntervention(models.Model):
    _name = 'smile.script.intervention'
    _description = 'Maintenance Intervention'
    _rec_name = 'create_date'
    _order = 'create_date DESC'

    def __init__(self, pool, cr):
        super(ScriptIntervention, self).__init__(pool, cr)
        model = pool[self._name]
        if not getattr(model, '_state_cleaner', False):
            model._state_cleaner = True
            setattr(Registry, 'setup_models', state_cleaner(
                getattr(Registry, 'setup_models')))

    script_id = fields.Many2one(
        'smile.script', 'Script', required=True, readonly=True)
    create_date = fields.Datetime(
        'Start date', required=True, readonly=True,
        default=fields.Datetime.now)
    end_date = fields.Datetime('End date', readonly=True)
    create_uid = fields.Many2one(
        'res.users', 'User', required=True, readonly=True)
    state = fields.Selection([
        ('running', 'Running'),
        ('done', 'Done'),
        ('exception', 'Exception'),
    ], readonly=True, required=True, default='running')
    test_mode = fields.Boolean('Test Mode', readonly=True)
    result = fields.Text(readonly=True)
    log_ids = fields.One2many(
        'smile.log', 'res_id', 'Logs', readonly=True,
        domain=[('model_name', '=', 'smile.script.intervention')])

    @api.multi
    def unlink(self):
        if not all(self.mapped('test_mode')):
            raise UserError(_('Intervention cannot be deleted'))
        return super(ScriptIntervention, self).unlink()
