# -*- coding: utf-8 -*-
# (C) 2014 Smile (<http://www.smile.fr>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import os
import psutil
import sys
from threading import Thread

from odoo import api, fields, models

from odoo.addons.smile_log.tools import SmileDBLogger

from .impex_template import LOG_LEVELS
from ..tools import get_hostname, s2human, with_impex_cursor

_logger = logging.getLogger(__name__)


STATES = [
    ('running', 'Running'),
    ('done', 'Done'),
    ('exception', 'Exception'),
    ('killed', 'Killed'),
]


class IrModelImpex(models.AbstractModel):
    _name = 'ir.model.impex'
    _description = 'Import/Export'
    _rec_name = 'create_date'
    _order = 'create_date desc'

    @api.one
    @api.depends('from_date', 'to_date')
    def _get_time(self):
        if not self.from_date:
            self.time = 0
        else:
            to_date = self.to_date or fields.Datetime.now()
            timedelta = fields.Datetime.from_string(to_date) \
                - fields.Datetime.from_string(self.from_date)
            self.time = timedelta.total_seconds()

    @api.one
    def _convert_time_to_human(self):
        self.time_human = s2human(self.time)

    create_date = fields.Datetime('Creation Date', readonly=True)
    create_uid = fields.Many2one('res.users', 'Creation User', readonly=True)
    from_date = fields.Datetime('Start date', readonly=True)
    to_date = fields.Datetime('End date', readonly=True)
    time = fields.Integer(compute='_get_time')
    time_human = fields.Char(
        'Time', compute='_convert_time_to_human', store=False)
    test_mode = fields.Boolean('Test Mode', readonly=True)
    new_thread = fields.Boolean('New Thread', readonly=True)
    state = fields.Selection(
        STATES, 'State', readonly=True, required=True, default='running')
    pid = fields.Integer('Process Id', readonly=True)
    hostname = fields.Char('Hostname', readonly=True)
    args = fields.Text('Arguments', readonly=True)
    log_level = fields.Selection(LOG_LEVELS)
    log_returns = fields.Boolean('Log returns', readonly=True)
    returns = fields.Text('Returns', readonly=True)

    @api.multi
    def process(self):
        res = []
        for record in self:
            if record.new_thread or record.test_mode:
                thread = Thread(target=IrModelImpex._process_with_new_cursor,
                                args=(self,))
                thread.start()
                res.append((record.id, True))
            else:
                res.append((record.id, record._process()))
        return res

    @api.multi
    @with_impex_cursor(autocommit=False)
    def _process_with_new_cursor(self):
        self._process()

    @api.multi
    def _process(self):
        self.ensure_one()
        logger = SmileDBLogger(self._cr.dbname, self._name, self.id, self._uid)
        logger.setLevel(self.log_level)
        self = self.with_context(logger=logger)
        hostname = get_hostname()
        self.write({'state': 'running', 'from_date': fields.Datetime.now(),
                    'pid': os.getpid(), 'hostname': hostname,
                    'to_date': False})
        try:
            result = self._execute()
            vals = {'state': 'done', 'to_date': fields.Datetime.now()}
            if self.log_returns:
                vals['returns'] = repr(result)
            self.write(vals)
            if self.test_mode:
                self._cr.rollback()
            return result
        except Exception as e:
            logger.error(repr(e))
            try:
                self.write({
                    'state': 'exception',
                    'to_date': fields.Datetime.now(),
                })
            except Exception:
                logger.warning("Cannot set import to exception")
            e.traceback = sys.exc_info()
            raise

    @api.multi
    def _execute(self):
        raise NotImplementedError

    @api.model
    def _kill_impex(self):
        # Search all process created on this host and set them as
        # killed if they are not running anymore on the host
        hostname = get_hostname()
        impex_infos = self.search_read([
            ('state', '=', 'running'),
            '|',
            ('hostname', '=', hostname),
            ('hostname', '=', False),
        ], ['pid'], order='id')
        impex_ids = []
        for impex in impex_infos:
            if not psutil.pid_exists(impex['pid']):
                impex_ids.append(impex['id'])
        if impex_ids:
            self.browse(impex_ids).write({'state': 'killed'})
