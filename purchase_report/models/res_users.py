from odoo import fields, models, api, _

class ResUsers(models.Model):
    _inherit = 'res.users'
    
    digital_signature = fields.Binary("Digital Signature", attachment=True)
