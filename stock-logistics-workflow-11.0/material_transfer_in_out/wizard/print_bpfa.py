from odoo import api, fields, models, _


class BPFAPrintout(models.Model):
    _name = 'bpfa.print.out'
    _description = 'Print out Docx Bukti Penerimaan Fixed Asset'

    bpfa_filename = fields.Char('Name')
    bpfa_filedata = fields.Binary('Docx Report', readonly=True)


class BPFAPrintParam(models.Model):
    _name = 'bpfa.print.param'
    _description = 'Parameter Print Out Docx Bukti Penerimaan Fixed Asset'

    @api.multi
    def construct_data(self):
        return_value = {}
        return return_value

    @api.multi
    def do_print(self):
        print_return = {}
        print_data = self.construct_data
        # load template
        return print_return
