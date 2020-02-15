import xlsxwriter
import base64
from odoo import fields, models, api
from datetime import datetime, timedelta
from io import BytesIO
from collections import OrderedDict
import pytz
import string
from pytz import timezone

STATE = {
    'draft': 'RFQ',
    'sent': 'RFQ Sent',
    'to approve': 'To Approve',
    'approved': 'Approved',
    'purchase': 'Purchase Order',
    'done': 'Done',
    'purchase_done': 'Purchase Order and Done',
    'cancel': 'Cancelled',
    False: '',
    None: '',
    '': '',
}

class BspPurchaseReportWizard(models.TransientModel):
    _name = "bsp.purchase.report.wizard"
    _description = "Purchase Report Wizard"
    
    @api.model
    def get_default_date_model(self):
        return pytz.UTC.localize(datetime.now()).astimezone(timezone(self.env.user.tz or 'Asia/Jakarta'))
    
    data = fields.Binary('File', readonly=True)
    name = fields.Char('Filename', readonly=True)
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date', default=fields.Date.context_today)
    partner_ids = fields.Many2many('res.partner', 'bsp_purchase_report_wizard_partner_rel', 'bsp_purchase_report_wizard_id',
        'partner_id', 'Supplier')
    report_type = fields.Selection([
        ('summary','PO Summary'),
        ('detail','PO Detail'),
        ('bppb','BPPB Summary'),
        ('summary_purchasing','PO Summary (Purchasing)'),
        ('qcf','QCF Summary'),
    ], required=True, string='Report Type', default='summary')
    state = fields.Selection([
        ('draft','RFQ'),
        ('sent','RFQ Sent'),
        ('to approve','To Approve'),
        ('approved','Approved'),
        ('purchase','Purchase Order'),
        ('done','Done'),
        ('purchase_done','Purchase Order and Done'),
        ('cancel','Cancelled'),
    ], string='State', default='purchase_done')
    
    def print_excel_report(self):
        query_where = ' 1=1 '
        if self.start_date :
            start_date = (datetime.strptime(self.start_date + ' 00:00:00', '%Y-%m-%d %H:%M:%S') - timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
            query_where +=" AND po.date_order >= '%s'"%(start_date)
        if self.end_date :
            end_date = (datetime.strptime(self.end_date + ' 23:59:59', '%Y-%m-%d %H:%M:%S') - timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
            query_where +=" AND po.date_order <= '%s'"%(end_date)
        if self.partner_ids :
            query_where +=" AND po.partner_id in %s"%str(tuple(self.partner_ids.ids)).replace(',)', ')')
        if self.state :
            if self.state == 'purchase_done' :
                query_where +=" AND po.state in ('purchase','done') "
            else :
                query_where +=" AND po.state = '%s'"%(self.state)

        datetime_string = self.get_default_date_model().strftime("%Y-%m-%d %H:%M:%S")
        date_string = self.get_default_date_model().strftime("%Y-%m-%d")
        
        timezone = self.env.user.tz or 'Asia/Jakarta'
        if timezone == 'Asia/Jayapura' :
            tz = '9 hours'
        elif timezone == 'Asia/Pontianak' :
            tz = '8 hours'
        else :
            tz = '7 hours'

        new_values = []
        if self.report_type == 'summary' :
            report_name = 'Purchase Report Summary'
            query = """
                SELECT
                    po.name as po_number, 
                    po.date_order + interval '%s' as po_date,
                    rp.name as supplier, 
                    po.amount_total,
                    po.state,
                    type.name as po_type,
                    po.amount_other_tax as ppn,
                    po.amount_wht as pph,
                    po.notes
                FROM
                    purchase_order po
                LEFT JOIN 
                    res_partner rp on rp.id = po.partner_id
                LEFT JOIN 
                    purchase_order_type type on type.id = po.order_type
                WHERE 
                    %s
                ORDER BY 
                    po_number
            """%(tz,query_where)
            
            self._cr.execute(query)
            result = self._cr.dictfetchall()
            
            fp = BytesIO()
            workbook = xlsxwriter.Workbook(fp)
            wbf, workbook = self.add_workbook_format(workbook)
            
            worksheet = workbook.add_worksheet(report_name)
            worksheet.set_column('A1:A1', 5)
            worksheet.set_column('B1:B1', 20)
            worksheet.set_column('C1:C1', 20)
            worksheet.set_column('D1:D1', 20)
            worksheet.set_column('E1:E1', 20)
            worksheet.set_column('F1:F1', 20)
            worksheet.set_column('G1:G1', 20)
            worksheet.set_column('H1:H1', 20)
            worksheet.set_column('I1:I1', 20)
            worksheet.set_column('J1:J1', 40)
            
            worksheet.write('A1', self.env.user.company_id.name, wbf['company'])
            worksheet.write('A2', report_name, wbf['title_doc'])
            worksheet.write('A3', 'Period %s to %s'%('-' if not self.start_date else self.start_date, '-' if not self.end_date else self.end_date), wbf['content_datetime'])
            
            row=5
            
            worksheet.write('A%s' %(row), 'No', wbf['header'])
            worksheet.write('B%s' %(row), 'Purchase Number', wbf['header'])
            worksheet.write('C%s' %(row), 'Purchase Date', wbf['header'])
            worksheet.write('D%s' %(row), 'Supplier', wbf['header'])        
            worksheet.write('E%s' %(row), 'PO Type', wbf['header'])
            worksheet.write('F%s' %(row), 'Amount Total', wbf['header'])
            worksheet.write('G%s' %(row), 'PPN', wbf['header'])
            worksheet.write('H%s' %(row), 'PPH', wbf['header'])
            worksheet.write('I%s' %(row), 'Status', wbf['header'])
            worksheet.write('J%s' %(row), 'Notes', wbf['header'])
            
            row+=1
            row1=row
            no=1
            
            for res in result :
                worksheet.write('A%s' %row, no, wbf['content'])
                worksheet.write('B%s' %row, res.get('po_number', ''), wbf['content'])
                worksheet.write('C%s' %row, res.get('po_date', ''), wbf['content'])
                worksheet.write('D%s' %row, res.get('supplier', ''), wbf['content'])
                worksheet.write('E%s' %row, res.get('po_type', ''), wbf['content'])
                worksheet.write('F%s' %row, res.get('amount_total', 0), wbf['content_float'])
                worksheet.write('G%s' %row, res.get('ppn', 0), wbf['content_float'])
                worksheet.write('H%s' %row, res.get('pph', 0), wbf['content_float'])
                worksheet.write('I%s' %row, STATE[res.get('state', False)], wbf['content'])
                worksheet.write('J%s' %row, res.get('note', ''), wbf['content'])
                
                row+=1
                no+=1
            
            worksheet.merge_range('A%s:B%s'%(row,row), 'Total', wbf['total'])
            worksheet.write('C%s' %row, '', wbf['total_float'])
            worksheet.write('D%s' %row, '', wbf['total_float'])
            worksheet.write('E%s' %row, '', wbf['total_float'])
            worksheet.write_formula('F%s' %row, '{=subtotal(9,F%s:F%s)}'%(row1, row-1), wbf['total_float'])
            worksheet.write_formula('G%s' %row, '{=subtotal(9,G%s:G%s)}'%(row1, row-1), wbf['total_float'])
            worksheet.write_formula('H%s' %row, '{=subtotal(9,H%s:H%s)}'%(row1, row-1), wbf['total_float'])
            worksheet.write('I%s' %row, '', wbf['total_float'])
            worksheet.write('J%s' %row, '', wbf['total_float'])
            worksheet.write('A%s'%(row+2), '%s %s'%(datetime_string, self.env.user.name), wbf['footer'])
            workbook.close()
            out=base64.encodestring(fp.getvalue())
            fp.close()
        elif self.report_type == 'detail' :
            report_name = 'Purchase Report Detail'
            query = """
                SELECT
                    po.id
                FROM
                    purchase_order po
                LEFT JOIN 
                    res_partner rp on rp.id = po.partner_id
                LEFT JOIN 
                    purchase_order_type type on type.id = po.order_type
                WHERE 
                    %s
                ORDER BY 
                    id
            """%(query_where)
            
            self._cr.execute(query)
            po_ids = self._cr.fetchall()
            po_ids = [po[0] for po in po_ids]

            fp = BytesIO()
            workbook = xlsxwriter.Workbook(fp)
            wbf, workbook = self.add_workbook_format(workbook)
            worksheet = workbook.add_worksheet(report_name)

            worksheet.write('A1', self.env.user.company_id.name, wbf['company'])
            worksheet.write('A2', report_name, wbf['title_doc'])
            worksheet.write('A3', 'Period %s to %s'%('-' if not self.start_date else self.start_date, '-' if not self.end_date else self.end_date), wbf['content_datetime'])

            row=5
            for po_id in po_ids :
                order_id = self.env['purchase.order'].browse(po_id)

                worksheet.set_column('A1:A1', 5)
                worksheet.set_column('B1:B1', 30)
                worksheet.set_column('C1:C1', 30)
                worksheet.set_column('D1:D1', 20)
                worksheet.set_column('E1:E1', 20)
                worksheet.set_column('F1:F1', 20)
                worksheet.set_column('G1:G1', 20)
                worksheet.set_column('H1:H1', 20)
                worksheet.set_column('I1:I1', 20)
                worksheet.set_column('J1:J1', 20)
                worksheet.set_column('K1:K1', 20)
                worksheet.set_column('L1:L1', 20)
                worksheet.set_column('M1:M1', 20)
                worksheet.set_column('N1:N1', 20)
                worksheet.set_column('O1:O1', 20)
                worksheet.set_column('P1:P1', 20)

                worksheet.write('B%s' %(row), 'PO Number : %s'%(order_id.name), wbf['content'])
                worksheet.write('D%s' %(row), 'Vendor    : %s'%(order_id.partner_id.name), wbf['content'])
                row+=1
                worksheet.write('B%s' %(row), 'PO Date      : %s'%((datetime.strptime(order_id.date_order, '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')), wbf['content'])
                worksheet.write('D%s' %(row), 'Status     : %s'%(STATE[order_id.state]), wbf['content'])
                row+=2
                
                worksheet.write('A%s' %(row), 'No', wbf['header'])
                worksheet.write('B%s' %(row), 'Product', wbf['header'])
                worksheet.write('C%s' %(row), 'Description', wbf['header'])
                worksheet.write('D%s' %(row), 'Scheduled Date', wbf['header'])        
                worksheet.write('E%s' %(row), 'Quantity', wbf['header'])
                worksheet.write('F%s' %(row), 'Qty to Receive', wbf['header'])
                worksheet.write('G%s' %(row), 'Received Qty', wbf['header'])
                worksheet.write('H%s' %(row), 'Qty to Bill', wbf['header'])
                worksheet.write('I%s' %(row), 'Returned Qty', wbf['header'])
                worksheet.write('J%s' %(row), 'Billed Qty', wbf['header'])
                worksheet.write('K%s' %(row), 'Refunded Qty', wbf['header'])
                worksheet.write('L%s' %(row), 'UoM', wbf['header'])
                worksheet.write('M%s' %(row), 'Unit Price', wbf['header'])
                worksheet.write('N%s' %(row), 'Discount', wbf['header'])
                worksheet.write('O%s' %(row), 'Taxes', wbf['header'])
                worksheet.write('P%s' %(row), 'Subtotal', wbf['header'])
                
                row+=1
                row1=row
                no=1
                
                for line in order_id.order_line :
                    worksheet.write('A%s' %row, no, wbf['content'])
                    worksheet.write('B%s' %row, line.product_id.name_get()[0][1], wbf['content'])
                    worksheet.write('C%s' %row, line.name, wbf['content'])
                    worksheet.write('D%s' %row, (datetime.strptime(line.date_planned, '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S'), wbf['content'])
                    worksheet.write('E%s' %row, line.product_qty, wbf['content_float'])
                    worksheet.write('F%s' %row, line.qty_to_receive, wbf['content_float'])
                    worksheet.write('G%s' %row, line.qty_received, wbf['content_float'])
                    worksheet.write('H%s' %row, line.qty_returned, wbf['content_float'])
                    worksheet.write('I%s' %row, line.qty_to_invoice, wbf['content_float'])
                    worksheet.write('J%s' %row, line.qty_invoiced, wbf['content_float'])
                    worksheet.write('K%s' %row, line.qty_refunded, wbf['content_float'])
                    worksheet.write('L%s' %row, line.product_uom.name, wbf['content'])
                    worksheet.write('M%s' %row, line.price_unit, wbf['content_float'])
                    worksheet.write('N%s' %row, line.discount, wbf['content_float'])
                    worksheet.write('O%s' %row, ', '.join([tax.name for tax in line.taxes_id]), wbf['content'])
                    worksheet.write('P%s' %row, line.price_subtotal, wbf['content_float'])
                    
                    row+=1
                    no+=1
                
                worksheet.merge_range('A%s:B%s'%(row,row), 'Total', wbf['total'])
                worksheet.write('C%s' %row, '', wbf['total_float'])
                worksheet.write('D%s' %row, '', wbf['total_float'])
                worksheet.write_formula('E%s' %row, '{=subtotal(9,E%s:E%s)}'%(row1, row-1), wbf['total_float'])
                worksheet.write_formula('F%s' %row, '{=subtotal(9,F%s:F%s)}'%(row1, row-1), wbf['total_float'])
                worksheet.write_formula('G%s' %row, '{=subtotal(9,G%s:G%s)}'%(row1, row-1), wbf['total_float'])
                worksheet.write_formula('H%s' %row, '{=subtotal(9,H%s:H%s)}'%(row1, row-1), wbf['total_float'])
                worksheet.write_formula('I%s' %row, '{=subtotal(9,I%s:I%s)}'%(row1, row-1), wbf['total_float'])
                worksheet.write_formula('J%s' %row, '{=subtotal(9,J%s:J%s)}'%(row1, row-1), wbf['total_float'])
                worksheet.write_formula('K%s' %row, '{=subtotal(9,K%s:K%s)}'%(row1, row-1), wbf['total_float'])
                worksheet.write_formula('L%s' %row, '{=subtotal(9,L%s:L%s)}'%(row1, row-1), wbf['total_float'])
                worksheet.write_formula('M%s' %row, '{=subtotal(9,M%s:M%s)}'%(row1, row-1), wbf['total_float'])
                worksheet.write_formula('N%s' %row, '{=subtotal(9,N%s:N%s)}'%(row1, row-1), wbf['total_float'])
                worksheet.write('O%s' %row, '', wbf['total_float'])
                worksheet.write_formula('P%s' %row, '{=subtotal(9,P%s:P%s)}'%(row1, row-1), wbf['total_float'])

                row += 3
            
            worksheet.write('A%s'%(row), '%s %s'%(datetime_string, self.env.user.name), wbf['footer'])
            workbook.close()
            out=base64.encodestring(fp.getvalue())
            fp.close()
        elif self.report_type in ('bppb','summary_purchasing'):
            if self.report_type == 'summary_purchasing' :
                self = self.with_context({'purchase':True})
            bppb_wizard_id = self.env['wizard.purchase.request.recap.reports'].create({
                'date_start': self.start_date,
                'date_end': self.end_date,
            })
            actions = bppb_wizard_id.action_purchase_request_recap_report()
            bppb_id = self.env['purchase.request.recap.reports'].browse(actions['res_id'])
            new_values = [bppb_id.purchase_request_recap_data, bppb_id.file_name]
        elif self.report_type == 'qcf' :
            qcf_wizard_id = self.env['wizard.purchase.request.recap.qcf.reports'].create({
                'date_start': self.start_date,
                'date_end': self.end_date,
            })
            actions = qcf_wizard_id.action_purchase_request_qcf_report()
            qcf_id = self.env['purchase.request.recap.qcf.reports'].browse(actions['res_id'])
            new_values = [qcf_id.purchase_request_data, qcf_id.file_name]
        
        if not new_values :
            filename = '%s %s'%(report_name,date_string)
            filename += '%2Exlsx'
        else :
            filename, out = new_values

        self.write({'data':out, 'name':filename})
        url = "web/content/?model="+self._name+"&id="+str(self.id)+"&field=data&download=true&filename="+filename
        return {
            'name': 'Purchase Report',
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }

    def add_workbook_format(self, workbook):
        colors = {
            'white_orange': '#FFFFDB',
            'orange': '#FFC300',
            'red': '#FF0000',
            'yellow': '#F6FA03',
        }

        wbf = {}
        wbf['header'] = workbook.add_format({'bold': 1,'align': 'center','bg_color': '#FFFFDB','font_color': '#000000'})
        wbf['header'].set_border()

        wbf['header_orange'] = workbook.add_format({'bold': 1,'align': 'center','bg_color': colors['orange'],'font_color': '#000000'})
        wbf['header_orange'].set_border()

        wbf['header_yellow'] = workbook.add_format({'bold': 1,'align': 'center','bg_color': colors['yellow'],'font_color': '#000000'})
        wbf['header_yellow'].set_border()
        
        wbf['header_no'] = workbook.add_format({'bold': 1,'align': 'center','bg_color': '#FFFFDB','font_color': '#000000'})
        wbf['header_no'].set_border()
        wbf['header_no'].set_align('vcenter')
                
        wbf['footer'] = workbook.add_format({'align':'left'})
        
        wbf['content_datetime'] = workbook.add_format({'num_format': 'yyyy-mm-dd hh:mm:ss'})
        wbf['content_datetime'].set_left()
        wbf['content_datetime'].set_right()
        
        wbf['content_date'] = workbook.add_format({'num_format': 'yyyy-mm-dd'})
        wbf['content_date'].set_left()
        wbf['content_date'].set_right() 
        
        wbf['title_doc'] = workbook.add_format({'bold': 1,'align': 'left'})
        wbf['title_doc'].set_font_size(12)
        
        wbf['company'] = workbook.add_format({'align': 'left'})
        wbf['company'].set_font_size(11)
        
        wbf['content'] = workbook.add_format()
        wbf['content'].set_left()
        wbf['content'].set_right() 
        
        wbf['content_float'] = workbook.add_format({'align': 'right','num_format': '#,##0.00'})
        wbf['content_float'].set_right() 
        wbf['content_float'].set_left()

        wbf['content_number'] = workbook.add_format({'align': 'right', 'num_format': '#,##0'})
        wbf['content_number'].set_right() 
        wbf['content_number'].set_left() 
        
        wbf['content_percent'] = workbook.add_format({'align': 'right','num_format': '0.00%'})
        wbf['content_percent'].set_right() 
        wbf['content_percent'].set_left() 
                
        wbf['total_float'] = workbook.add_format({'bold':1, 'bg_color':colors['white_orange'], 'align':'right', 'num_format':'#,##0.00'})
        wbf['total_float'].set_top()
        wbf['total_float'].set_bottom()            
        wbf['total_float'].set_left()
        wbf['total_float'].set_right()         
        
        wbf['total_number'] = workbook.add_format({'align':'right','bg_color': colors['white_orange'],'bold':1, 'num_format': '#,##0'})
        wbf['total_number'].set_top()
        wbf['total_number'].set_bottom()            
        wbf['total_number'].set_left()
        wbf['total_number'].set_right()
        
        wbf['total'] = workbook.add_format({'bold':1, 'bg_color':colors['white_orange'], 'align':'center'})
        wbf['total'].set_left()
        wbf['total'].set_right()
        wbf['total'].set_top()
        wbf['total'].set_bottom()

        wbf['total_float_yellow'] = workbook.add_format({'bold':1, 'bg_color':colors['yellow'], 'align':'right', 'num_format':'#,##0.00'})
        wbf['total_float_yellow'].set_top()
        wbf['total_float_yellow'].set_bottom()            
        wbf['total_float_yellow'].set_left()
        wbf['total_float_yellow'].set_right()         
        
        wbf['total_number_yellow'] = workbook.add_format({'align':'right','bg_color': colors['yellow'],'bold':1, 'num_format': '#,##0'})
        wbf['total_number_yellow'].set_top()
        wbf['total_number_yellow'].set_bottom()            
        wbf['total_number_yellow'].set_left()
        wbf['total_number_yellow'].set_right()
        
        wbf['total_yellow'] = workbook.add_format({'bold':1, 'bg_color':colors['yellow'], 'align':'center'})
        wbf['total_yellow'].set_left()
        wbf['total_yellow'].set_right()
        wbf['total_yellow'].set_top()
        wbf['total_yellow'].set_bottom()

        wbf['total_float_orange'] = workbook.add_format({'bold':1, 'bg_color':colors['orange'], 'align':'right', 'num_format':'#,##0.00'})
        wbf['total_float_orange'].set_top()
        wbf['total_float_orange'].set_bottom()            
        wbf['total_float_orange'].set_left()
        wbf['total_float_orange'].set_right()         
        
        wbf['total_number_orange'] = workbook.add_format({'align':'right','bg_color': colors['orange'],'bold':1, 'num_format': '#,##0'})
        wbf['total_number_orange'].set_top()
        wbf['total_number_orange'].set_bottom()            
        wbf['total_number_orange'].set_left()
        wbf['total_number_orange'].set_right()
        
        wbf['total_orange'] = workbook.add_format({'bold':1, 'bg_color':colors['orange'], 'align':'center'})
        wbf['total_orange'].set_left()
        wbf['total_orange'].set_right()
        wbf['total_orange'].set_top()
        wbf['total_orange'].set_bottom()
        
        wbf['header_detail_space'] = workbook.add_format({})
        wbf['header_detail_space'].set_left()
        wbf['header_detail_space'].set_right()
        wbf['header_detail_space'].set_top()
        wbf['header_detail_space'].set_bottom()
        
        wbf['header_detail'] = workbook.add_format({'bg_color': '#E0FFC2'})
        wbf['header_detail'].set_left()
        wbf['header_detail'].set_right()
        wbf['header_detail'].set_top()
        wbf['header_detail'].set_bottom()
        
        return wbf, workbook
