# -*- coding: utf-8 -*-
# (C) 2011 Smile (<http://www.smile.fr>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models, SUPERUSER_ID


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    def _search(
            self, args, offset=0, limit=None, order=None, count=False,
            access_rights_uid=None):
        if self.env.uid != SUPERUSER_ID:
            menu_id = self.env['ir.model.data'].xmlid_to_res_id(
                'smile_access_control.menu_action_superadmin')
            args = [('id', '!=', menu_id)] + (args or [])
        return super(IrUiMenu, self)._search(
            args, offset, limit, order, count, access_rights_uid)
