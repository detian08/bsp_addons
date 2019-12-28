from odoo import api, models


class KontraBon(models.Model):
    _name = "kontra.bon"
    _inherit = ['kontra.bon', 'tier.validation']
    _state_from = ['draft','to_approve']
    _state_to = ['approved','open']

    @api.model
    def _get_under_validation_exceptions(self):
        res = super(KontraBon, self)._get_under_validation_exceptions()
        res.append('route_id')
        return res
