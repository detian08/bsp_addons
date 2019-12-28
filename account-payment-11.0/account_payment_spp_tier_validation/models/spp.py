from odoo import api, models


class SPP(models.Model):
    _name = "spp"
    _inherit = ['spp', 'tier.validation']
    _state_from = ['draft','to_approve']
    _state_to = ['approved','open']

    @api.model
    def _get_under_validation_exceptions(self):
        res = super(SPP, self)._get_under_validation_exceptions()
        res.append('route_id')
        return res
