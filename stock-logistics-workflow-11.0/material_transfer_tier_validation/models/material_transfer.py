from odoo import api, models


class MaterialTransfer(models.Model):
    _name = "material.transfer"
    _inherit = ['material.transfer', 'tier.validation']
    _state_from = ['draft']
    _state_to = ['open']

    @api.model
    def _get_under_validation_exceptions(self):
        res = super(MaterialTransfer, self)._get_under_validation_exceptions()
        res.append('route_id')
        return res
