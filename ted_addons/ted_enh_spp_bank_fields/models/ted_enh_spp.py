from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare


class TedSPPPayment(models.Model):
    _inherit = 'spp'

    @api.onchange('payment_dest_bank_acc_id')
    def _onchange_bank_acc_id(self):

        if self.payment_dest_bank_acc_id:
            bank_info = self.payment_dest_bank_acc_id
            self.payment_dest_bank_acc_name = bank_info.bank_account_name
            self.payment_dest_bank_acc_no = bank_info.acc_number
            self.payment_dest_bank_name = bank_info.bank_name
            self.payment_dest_bank_branch_name = bank_info.bank_branch_name
            self.payment_dest_bank_branch_address = bank_info.bank_branch_addr1

        else:
            self.payment_dest_bank_acc_name = ''
            self.payment_dest_bank_acc_no = ''
            self.payment_dest_bank_name = ''
            self.payment_dest_bank_branch_name = ''
            self.payment_dest_bank_branch_address = ''
    up_value = fields.Char(string='UP')
    acknowledged_1 = fields.Many2one(comodel_name='res.users',
                                     string='Supervisor')
    payment_dest_bank_acc_id = fields.Many2one(comodel_name='res.partner.bank',
                                               string='Id Rekening Bank'
                                               )
    payment_dest_bank_acc_no = fields.Char(string='No. Rekening',
                                           store=True,
                                           track_visibility='onchange')
    payment_dest_bank_acc_name = fields.Char(string='Nama Rekening',
                                             store=True,
                                             track_visibility='onchange')
    payment_dest_bank_name = fields.Char(string='Nama Bank',
                                         store=True,
                                         track_visibility='onchange')
    payment_dest_bank_branch_name = fields.Char(string='Nama Cabang',
                                                store=True,
                                                track_visibility='onchange')
    payment_dest_bank_branch_address = fields.Char(string='Alamat Cabang',
                                                   store=True,
                                                   track_visibility='onchange')

