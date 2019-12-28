from odoo import api, fields, models
# from lxml import etree
# from odoo.osv.orm import setup_modifiers


# change attribute invisible for any field in element
# def _visible_fields(self, result):
#     doc = etree.XML(result['arch'])
#     fields = ['vehicle_id', 'vehicle_model', 'vehicle_model_year', 'vehicle_last_odometer', 'vehicle_repair_status',
#               'est_amount_total1', 'est_amount_total2', 'last_service', 'partner_id', 'partner_id1', 'partner_id2',
#               'estimated_cost1', 'estimated_cost2']
#     for f in fields:
#         for node in doc.xpath("//field[@name='"+f+"']"):
#             node.set('invisible', '0')
#             setup_modifiers(node, result['fields'][node.get('name')])
#     result['arch'] = etree.tostring(doc, encoding='unicode')
#     return result

class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    vehicle_id = fields.Many2one('fleet.vehicle',
                                 string='License Plate',
                                 help='License plate number of the vehicle (i = plate number for a car)')
    vehicle_model = fields.Many2one('fleet.vehicle.model',
                                    related='vehicle_id.model_id',
                                    string='Model',
                                    store=True,
                                    readonly=True,
                                    help='Model of the vehicle')
    vehicle_model_year = fields.Char(related='vehicle_id.model_year',
                                     string='model year',
                                     store=True,
                                     readonly=True,
                                     help='Year of the model')
    vehicle_last_odometer = fields.Integer(string='Last Odometer',
                                           help='Odometer measure of the vehicle at the moment of this log',
                                           default=0)
    vehicle_repair_status = fields.Selection([('notyet', 'Not yet repair'),
                                              ('inservice', 'In service'),
                                              ('already', 'Already repaired')],
                                             string='Status',
                                             index=True, copy=False, default='notyet')
    # est_amount_total1 = fields.Float(string='Est.Total-1', store=True, readonly=True, compute='_amount_all',
    #                                  default=0.0)
    # est_amount_total2 = fields.Float(string='Est.Total-2', store=True, readonly=True, compute='_amount_all',
    #                                  default=0.0)

    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False):
    #     context = self._context
    #     result = super(PurchaseRequest, self).fields_view_get(view_id, view_type, toolbar=toolbar)
    #     if context.get('default_doc_type') == 'K1':
    #         # dynamic view header doc
    #         if view_type == 'tree' and result['name'] == 'purchase.request.tree':
    #             _visible_fields(self, result)
    #         if view_type == 'form' and result['name'] == 'purchase.request.form':
    #             _visible_fields(self, result)
    #             # dynamic view tree line
    #             res = result['fields']['line_ids']['views']['tree']
    #             if res:
    #                 _visible_fields(self, res)
    #             # dynamic view tree line
    #             res = result['fields']['line_ids']['views']['form']
    #             if res:
    #                 _visible_fields(self, res)
    #     return result