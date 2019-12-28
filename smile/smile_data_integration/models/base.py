# -*- coding: utf-8 -*-
# (C) 2017 Smile (<http://www.smile.fr>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import sys

from odoo import api, fields, models, tools
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

if sys.version_info > (3,):
    long = int


class Base(models.AbstractModel):
    _inherit = 'base'

    @api.model_cr_context
    def _auto_init(self):
        name = 'old_id'
        if self._auto and name not in self._fields:
            field = fields.Integer(readonly=True)
            self._add_field(name, field)
        super(Base, self)._auto_init()

    @api.model
    def _setup_base(self):
        super(Base, self)._setup_base()
        name = 'old_id'
        if self._auto and name not in self._fields:
            field = fields.Integer(readonly=True)
            self._add_field(name, field)
            if tools.table_exists(self._cr, self._table):
                columns = tools.table_columns(self._cr, self._table)
                field.update_db_column(self, columns.get(name))

    @api.model
    def load(self, fields, data):
        if data:
            for index, field in enumerate(fields):
                if field.endswith('__id'):
                    fields[index] = field.replace('__id', ':id')
                if field in self._fields and \
                        self._fields[field].type == 'many2one' and \
                        isinstance(data[0][index], (int, long)):
                    fields[index] = field + '.id'
        res = super(Base, self).load(fields, data)
        if res['messages']:
            for message in res['messages']:
                _logger.error(message)
            if self._context.get('raise_load_exceptions'):
                raise UserError('\n'.join(map(str, res['messages'])))
        return res
