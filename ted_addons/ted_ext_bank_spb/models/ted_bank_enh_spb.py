from odoo import api, fields, models, _

#
class TedBankEnhancementSPB(models.Model):
    _inherit = 'res.partner.bank'
    _description = 'Add custom fields for Bank information'

    bank_account_name = fields.Char(string='Atas Nama')
    bank_branch_name = fields.Char(string='Nama Cabang')
    bank_branch_addr1 = fields.Char(string='Alamat Cabang')
