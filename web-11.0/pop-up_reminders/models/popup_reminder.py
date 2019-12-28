from odoo import models, fields


class PopupReminder(models.Model):
    _name = 'popup.reminder'

    name = fields.Char(string='Title', required=True)
    description = fields.Char(string='description', required=True)
    model_name = fields.Many2one('ir.model', string="Model", required=True)
    model_field = fields.Many2one('ir.model.fields', string='Field',
                                  domain="[('model_id', '=',model_name),('ttype', 'in', ['datetime','date'])]",
                                  required=True)
    
    search_by = fields.Selection([('today', 'Today'),
                                  ('set_period', 'Set Duration'),
                                  ('set_date', 'Set Date'), ],
                                 required=True, string="Search By")
    date_set = fields.Date(string='Select Date')
    date_from = fields.Date(string="Start Date")
    date_to = fields.Date(string="End Date")
