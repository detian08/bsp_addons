from odoo import models, fields, api


class ReportPurchaseRequest(models.TransientModel):
    _name = 'report.purchase.request'
    _description = 'Wizard for report.purchase.request'
    _inherit = 'xlsx.report'

    # Search Criteria
    company_id = fields.Many2one(
        'res.company',
        string='Company',
    )
    # Report Result, purchase.request
    results = fields.Many2many(
        'purchase.request',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing stored in database',
    )

    @api.multi
    def _compute_results(self):
        """ On the wizard, result will be computed and added to results line
        before export to excel, by using xlsx.export
        """
        self.ensure_one()
        Result = self.env['purchase.request']
        domain = []
        if self.company_id:
            domain += [('company_id', '=', self.company_id.id)]
        self.results = Result.search(domain)