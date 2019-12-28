from odoo import models, fields, api
from datetime import date
from odoo.exceptions import Warning
from datetime import date,datetime, timedelta


class wizardGetReport(models.TransientModel):
    _name = "wizard.get.report"
    
    name = fields.Many2one("report.definition", name="Report Name")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    
    
    @api.multi
    def get_report(self):
        
#         define data that tdo generate report
        format          =  "%Y-%m-%d"
        if datetime.strptime(str(self.end_date), format) < datetime.strptime(str(self.start_date), format):
            raise Warning("End date should be lower than start date")
        
        data = {}        
        data["start_date"]     = str(self.start_date)
        data["end_date"]       = str(self.end_date)
        data['report_def_obj'] = self.name  
        
#         call function generte report in report result to generate report
        self.env['report.result'].generate_report(data)             
        
