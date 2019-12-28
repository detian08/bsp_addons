# -*- coding: utf-8 -*-
# (C) 2010 Smile (<http://www.smile.fr>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models, tools
from odoo.addons.fetchmail.models.fetchmail import _logger


class FetchmailServer(models.Model):
    _inherit = "fetchmail.server"

    @api.multi
    def fetch_mail(self):
        if not tools.config.get('enable_email_fetching'):
            _logger.warning('Email fetching not enabled')
            return False
        return super(FetchmailServer, self).fetch_mail()
