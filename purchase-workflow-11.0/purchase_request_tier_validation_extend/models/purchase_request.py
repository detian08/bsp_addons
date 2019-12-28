from odoo import api, models, fields


class PurchaseRequest(models.Model):
    _name = "purchase.request"
    _inherit = ['purchase.request']

    need_tobeaskedvalidation = fields.Boolean('Needs to be asked Validation', compute='_get_reviewers', store=True)

    @api.one
    def _get_reviewers(self):
            if len(list(self.review_ids)) > 0:
                self.need_tobeaskedvalidation = False
            else:
                self.need_tobeaskedvalidation = True
