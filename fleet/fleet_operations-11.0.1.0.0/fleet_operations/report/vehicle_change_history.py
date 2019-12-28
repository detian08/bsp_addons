# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

import time
from odoo import api, models, _
from odoo.exceptions import UserError


class VehicalChangeHistoryReport(models.AbstractModel):
    _name = 'report.fleet_operations.vehicle_change_history_qweb'

    def get_vehicle_history(self, date_range):
        engine_obj = self.env['engine.history']
        color_obj = self.env['color.history']
        vin_obj = self.env['vin.history']
        domain = []
        if date_range.get('date_from'):
            domain += [('changed_date', '>=', date_range.get('date_from'))]
        if date_range.get('date_to'):
            domain += [('changed_date', '<=', date_range.get('date_to'))]
        if date_range.get('fleet_id'):
            domain += [('vehicle_id', '=', date_range.get('fleet_id'))]

        engine_ids = engine_obj.search(domain)
        color_ids = color_obj.search(domain)
        vin_ids = vin_obj.search(domain)
        vehicle_change_history = []
        if engine_ids:
            for engine_rec in engine_ids:
                seq = engine_rec.vehicle_id and \
                    engine_rec.vehicle_id.name or ''
                values = {
                    'description': seq,
                    'vehicle_type': engine_rec.vehicle_id and
                    engine_rec.vehicle_id.vechical_type_id and
                    engine_rec.vehicle_id.vechical_type_id.name or '',
                    'color_id': engine_rec.vehicle_id and
                    engine_rec.vehicle_id.vehical_color_id and
                    engine_rec.vehicle_id.vehical_color_id.name or '',
                    'vin': engine_rec.vehicle_id and
                    engine_rec.vehicle_id.vin_sn or '',
                    'plate': engine_rec.vehicle_id and
                    engine_rec.vehicle_id.license_plate or '',
                    'old_engine': engine_rec.previous_engine_no or '',
                    'new_engine': engine_rec.new_engine_no or '',
                    'old_color': '',
                    'new_color': '',
                    'old_vin': '',
                    'new_vin': '',
                    'change_date': engine_rec.changed_date or False,
                    'work_order': engine_rec.workorder_id and
                    engine_rec.workorder_id.name or '',
                    'wo_close_date': engine_rec.workorder_id and
                    engine_rec.workorder_id.date_close or False,
                    'remarks': engine_rec.note or '',
                    'seq': seq + 'a'
                    }
                vehicle_change_history.append(values)
        if color_ids:
            for color_rec in color_ids:
                seq = color_rec.vehicle_id and color_rec.vehicle_id.name or ''
                cvalues = {
                    'description': seq,
                    'vehicle_type': color_rec.vehicle_id and
                    color_rec.vehicle_id.vechical_type_id and
                    color_rec.vehicle_id.vechical_type_id.name or '',
                    'color_id': color_rec.vehicle_id and
                    color_rec.vehicle_id.vehical_color_id and
                    color_rec.vehicle_id.vehical_color_id.name or '',
                    'vin': color_rec.vehicle_id and
                    color_rec.vehicle_id.vin_sn or '',
                    'plate': engine_rec.vehicle_id and
                    engine_rec.vehicle_id.license_plate or '',
                    'old_engine': '',
                    'new_engine': '',
                    'old_color': color_rec.previous_color_id and
                    color_rec.previous_color_id.name or '',
                    'new_color': color_rec.current_color_id and
                    color_rec.current_color_id.name or '',
                    'old_vin': '',
                    'new_vin': '',
                    'change_date': color_rec.changed_date or False,
                    'work_order': color_rec.workorder_id and
                    color_rec.workorder_id.name or '',
                    'wo_close_date': color_rec.workorder_id and
                    color_rec.workorder_id.date_close or False,
                    'remarks': color_rec.note or '',
                    'seq': seq + 'b'
                    }
                vehicle_change_history.append(cvalues)
        if vin_ids:
            for vin_rec in vin_ids:
                seq = vin_rec.vehicle_id and vin_rec.vehicle_id.name or ''
                vvalues = {
                    'description': seq,
                    'vehicle_type': vin_rec.vehicle_id and
                    vin_rec.vehicle_id.vechical_type_id and
                    vin_rec.vehicle_id.vechical_type_id.name or '',
                    'color_id': vin_rec.vehicle_id and
                    vin_rec.vehicle_id.vehical_color_id and
                    vin_rec.vehicle_id.vehical_color_id.name or '',
                    'vin': vin_rec.vehicle_id and
                    vin_rec.vehicle_id.vin_sn or '',
                    'plate': engine_rec.vehicle_id and
                    engine_rec.vehicle_id.license_plate or '',
                    'old_engine': '',
                    'new_engine': '',
                    'old_color': '',
                    'new_color': '',
                    'old_vin': vin_rec.previous_vin_no or '',
                    'new_vin': vin_rec.new_vin_no or '',
                    'change_date': vin_rec.changed_date or False,
                    'work_order': vin_rec.workorder_id and
                    vin_rec.workorder_id.name or '',
                    'wo_close_date': vin_rec.workorder_id and
                    vin_rec.workorder_id.date_close or False,
                    'remarks': vin_rec.note or '',
                    'seq': seq + 'c'
                    }
                vehicle_change_history.append(vvalues)
        if vehicle_change_history:
            vehicle_change_history = sorted(vehicle_change_history,
                                            key=lambda k: k['seq'])
        return vehicle_change_history

    @api.model
    def get_report_values(self, docids, data=None):
        if not data.get('form') or \
                not self.env.context.get('active_model') or \
                not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, \
                    this report cannot be printed."))

        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        result = self.get_vehicle_history(data.get('form'))
        return {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'get_vehicle_history': result
        }