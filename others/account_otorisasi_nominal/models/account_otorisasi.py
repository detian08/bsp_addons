from odoo import models, api, fields


class resusers(models.Model):
    _inherit = 'res.users'

    x_nominal_otorisasi = fields.Monetary(string='Nominal Otorisasi', store=True, default=0.0)

    # @api.onchange('x_nominal_otorisasi')
    # def onchange_x_nominal_otorisasi(self):
