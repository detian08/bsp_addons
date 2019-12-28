from odoo import api, fields, models


# configuration for report
class resConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    file_store = fields.Char(string="File Store")
    
#     set value for file_store
    def set_values(self):
        super(resConfigSettings, self).set_values()
        set_param = self.env['ir.config_parameter'].set_param
        set_param('path_file_store', (self.file_store or '').strip())
       
    
#     get value for file_store using params   
    @api.model
    def get_values(self):
        res = super(resConfigSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        res.update(
            file_store=get_param('path_file_store', default=''),
            
        )
        return res
    
#     return all values configuration
    def get_path(self):
        return self.get_values()
    
    

