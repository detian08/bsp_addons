from odoo import api, fields, models, tools


class PurchaseRequestReport(models.Model):
    _name = "purchase.request.report"
    _description = "Purchases Request Report"
    _auto = False
    _order = 'date_start desc, price_total desc'

    date_start = fields.Date('Creation Date', readonly=True, help="Date on which this document has been created")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'To be approved'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('done', 'Done')], 'Request Status', readonly=True)
    doc_type = fields.Selection([
        ('K0', 'Form-BPPB'),
        ('K1', 'Form-K1'),
        ('K2', 'Form-K2'),
        ('K3', 'Form-K3'),
        ('K4', 'Form-K4')], 'Doc Type', readonly=True)
    purchase_state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
        ], 'Purchase Status', readonly=True)
    name = fields.Char('Source Document', readonly=True)
    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    picking_type_id = fields.Many2one('stock.warehouse', 'Warehouse', readonly=True)
    partner_id = fields.Many2one('res.partner', 'Vendor', readonly=True)
    date_approve = fields.Date('Date Approved', readonly=True)
    product_uom = fields.Many2one('product.uom', 'Reference Unit of Measure', required=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True)
    currency_id = fields.Many2one('res.currency', 'Currency', readonly=True)
    user_id = fields.Many2one('res.users', 'Requested by', readonly=True)
    delay = fields.Float('Days to Validate', digits=(16, 2), readonly=True)
    delay_pass = fields.Float('Days to Deliver', digits=(16, 2), readonly=True)
    unit_quantity = fields.Float('Product Qty', digits=(16, 2), readonly=True)
    unit_qty_purchase = fields.Float('Qty Purchase Order', digits=(16, 2), readonly=True)
    net_price_total = fields.Float('Net Total Price', digits=(16, 2), readonly=True)
    net_price_average = fields.Float('Net Average Price', digits=(16, 2), readonly=True, group_operator="avg")
    negociation = fields.Float('Purchase-Standard Price', digits=(16, 2), readonly=True, group_operator="avg")
    price_standard = fields.Float('Products Value', digits=(16, 2), readonly=True, group_operator="sum")
    nbr_lines = fields.Integer('# of Lines', readonly=True)
    category_id = fields.Many2one('product.category', 'Product Category', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', 'Product Template', readonly=True)
    country_id = fields.Many2one('res.country', 'Partner Country', readonly=True)
    account_analytic_id = fields.Many2one('account.analytic.account', 'Analytic Account', readonly=True)
    commercial_partner_id = fields.Many2one('res.partner', 'Commercial Entity', readonly=True)
    weight = fields.Float('Gross Weight', readonly=True)
    volume = fields.Float('Volume', readonly=True)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'purchase_request_report')
        self._cr.execute("""
            create view purchase_request_report as (
                WITH currency_rate as (%s)
                select
                    min(l.id) as id,
                    s.name,
                    s.date_start,
                    s.doc_type,
                    s.date_approve,
                    s.state,
                    l.purchase_state,
                    spt.warehouse_id as picking_type_id,
                    s.partner_id as partner_id,
                    s.requested_by as user_id,
                    s.company_id as company_id,
                    l.product_id,
                    p.product_tmpl_id,
                    t.categ_id as category_id,
                    s.currency_id,
                    t.uom_id as product_uom,
                    sum(l.product_qty/u.factor*u2.factor) as unit_quantity,
                    extract(epoch from age(s.date_approve,s.date_start))/(24*60*60)::decimal(16,2) as delay,
                    extract(epoch from age(l.date_required,s.date_start))/(24*60*60)::decimal(16,2) as delay_pass,
                    count(*) as nbr_lines,
                    sum(l.net_price / COALESCE(NULLIF(cr.rate, 0), 1.0) * l.product_qty)::decimal(16,2) as net_price_total,
                    avg(100.0 * (l.net_price / COALESCE(NULLIF(cr.rate, 0),1.0) * l.product_qty) / NULLIF(ip.value_float*l.product_qty/u.factor*u2.factor, 0.0))::decimal(16,2) as negociation,
                    sum(ip.value_float*l.product_qty/u.factor*u2.factor)::decimal(16,2) as price_standard,
                    (sum(l.product_qty * l.net_price / COALESCE(NULLIF(cr.rate, 0), 1.0))/NULLIF(sum(l.product_qty/u.factor*u2.factor),0.0))::decimal(16,2) as net_price_average,
                    partner.country_id as country_id,
                    partner.commercial_partner_id as commercial_partner_id,
                    analytic_account.id as account_analytic_id,
                    sum(p.weight * l.product_qty/u.factor*u2.factor) as weight,
                    sum(p.volume * l.product_qty/u.factor*u2.factor) as volume,
		            sum(pol.product_qty) as unit_qty_purchase			
                from purchase_request_line l
                    join purchase_request s on (l.request_id=s.id)
                    left join res_partner partner on s.partner_id = partner.id
                    left join product_product p on (l.product_id=p.id)
                    left join product_template t on (p.product_tmpl_id=t.id)
                    left join ir_property ip on (ip.name='standard_price' AND ip.res_id=CONCAT('product.product,',p.id) AND ip.company_id=s.company_id)
                    left join product_uom u on (u.id=l.product_uom_id)
                    left join product_uom u2 on (u2.id=t.uom_id)
                    left join stock_picking_type spt on (spt.id=s.picking_type_id)
                    left join account_analytic_account analytic_account on (l.analytic_account_id = analytic_account.id)
                    left join purchase_request_purchase_order_line_rel m2m on (l.id = m2m.purchase_request_line_id)
                    left join purchase_order_line pol on (m2m.purchase_order_line_id = pol.id)
                    left join currency_rate cr on (cr.currency_id = s.currency_id and
                        cr.company_id = s.company_id and
                        cr.date_start <= coalesce(s.date_start, now()) and
                        (cr.date_end is null or cr.date_end > coalesce(s.date_start, now())))
                group by
                    s.doc_type,
                    s.date_approve,
                    s.company_id,
                    s.requested_by,
                    s.partner_id,
                    u.factor,
                    s.currency_id,
                    l.price_unit,
                    l.date_required,
                    l.product_uom_id,
                    l.product_id,
                    p.product_tmpl_id,
                    t.categ_id,
                    s.date_start,
                    s.state,
                    spt.warehouse_id,
                    u.uom_type,
                    u.category_id,
                    t.uom_id,
                    u.id,
                    u2.factor,
                    partner.country_id,
                    partner.commercial_partner_id,
                    analytic_account.id,
                    l.purchase_state,
                    s.name
                order by id asc
            )
        """ % self.env['res.currency']._select_companies_rates())