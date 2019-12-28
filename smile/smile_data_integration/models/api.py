# -*- coding: utf-8 -*-
# (C) 2017 Smile (<http://www.smile.fr>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from six import string_types

from odoo import api, fields

native_call_kw_model = api.call_kw_model
native_call_kw_multi = api.call_kw_multi


def _convert_values(self, vals):
    for field in vals:
        if field in self._fields and isinstance(vals[field], string_types):
            if isinstance(self._fields[field], fields.Many2one):
                vals[field] = self.env['ir.model.data'].xmlid_to_res_id(
                    vals[field], raise_if_not_found=True)
            elif isinstance(self._fields[field], fields.Many2many):
                vals[field] = [
                    self.env['ir.model.data'].xmlid_to_res_id(
                        xml_id, raise_if_not_found=True)
                    for xml_id in vals[field].replace(' ', '').split(',')]


def _convert_domain(self, domain):
    for index, condition in enumerate(domain):
        if isinstance(condition, (tuple, list)) and condition[2] and \
                (isinstance(condition[2], string_types) or
                 (isinstance(condition[2], list) and
                  isinstance(condition[2][0], string_types))):
            if isinstance(condition, tuple):
                condition = list(condition)
            model = self
            for field_name in condition[0].split('.'):
                field = model._fields.get(field_name)
                relational_types = (fields.Many2one,
                                    fields.One2many, fields.Many2many)
                if isinstance(field, relational_types):
                    model = self.env[field.comodel_name]
                elif field_name != 'id':
                    break
            else:
                IrModelData = self.env['ir.model.data']
                if isinstance(condition[2], string_types):
                    condition[2] = IrModelData.xmlid_to_res_id(
                        condition[2], raise_if_not_found=True)
                else:
                    ids = []
                    for xmlid in condition[2]:
                        ids.append(IrModelData.xmlid_to_res_id(
                            xmlid, raise_if_not_found=True))
                    condition[2] = ids
            domain[index] = condition


def call_kw_model(method, self, args, kwargs):
    if method.__name__ in ['create', 'checklist_wrapper'] and args:
        _convert_values(self, args[0])
    if method.__name__ in ('search', 'search_read', 'search_count') and args:
        _convert_domain(self, args[0])
    return native_call_kw_model(method, self, args, kwargs)


def call_kw_multi(method, self, args, kwargs):
    if args:
        args = list(args)
        old_ids = args[0]
        if not isinstance(args[0], (list, tuple, set)):
            old_ids = [args[0]]
        new_ids = []
        for id_ in old_ids:
            if isinstance(id_, string_types):
                new_ids.append(self.env['ir.model.data'].xmlid_to_res_id(
                    id_, raise_if_not_found=True))
            else:
                new_ids.append(id_)
        args[0] = new_ids if hasattr(args[0], '__iter__') else new_ids[0]
        if method.__name__ == 'write' and len(args) > 1:
            _convert_values(self, args[1])
        args = tuple(args)
    return native_call_kw_multi(method, self, args, kwargs)


api.call_kw_model = call_kw_model
api.call_kw_multi = call_kw_multi
