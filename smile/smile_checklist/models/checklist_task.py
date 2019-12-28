# -*- coding: utf-8 -*-
# (C) 2011 Smile (<http://www.smile.fr>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ChecklistTask(models.Model):
    _name = 'checklist.task'
    _description = 'Checklist Task'
    _order = 'sequence'

    name = fields.Char(required=True, translate=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer('Priority', required=True, default=15)
    checklist_id = fields.Many2one(
        'checklist', 'Checklist', required=True, ondelete='cascade',
        auto_join=True)
    active_field = fields.Boolean(
        "Field 'Active'", related='checklist_id.active_field')
    mandatory = fields.Boolean('Required to make active object')
    filter_domain = fields.Char('Apply on')
    complete_domain = fields.Char('Complete if')
    model = fields.Char(related='checklist_id.model_id.model')

    @api.model
    def create(self, vals):
        task = super(ChecklistTask, self).create(vals)
        task._manage_task_instances()
        return task

    @api.multi
    def write(self, vals):
        self = self._filter_tasks_to_update(vals)
        if not self:
            return True
        result = super(ChecklistTask, self).write(vals)
        self._manage_task_instances()
        return result

    @api.multi
    def unlink(self):
        checklists = self.mapped('checklist_id')
        result = super(ChecklistTask, self).unlink()
        checklists._compute_progress_rates()
        return result

    @api.multi
    def _filter_tasks_to_update(self, vals):
        # INFO: avoid to trigger checklist computation
        # when updating a module if checklist didn't change
        for task in self:
            taskinfo = task.read(vals.keys(), load='_classic_write')[0]
            try:
                shared_items = set(taskinfo.items()) & set(vals.items())
            except Exception:  # Case of x2m fields
                shared_items = {}
            if len(shared_items) == len(vals):
                self -= task
        return self

    @api.multi
    def _manage_task_instances(self, records=None):
        for checklist in self.mapped('checklist_id'):
            _records = records
            if not _records:
                _records = self.env[checklist.model_id.model]. \
                    sudo().with_context(active_test=False).search([])
            if 'x_checklist_task_instance_ids' not in \
                    _records._fields:
                checklist._update_models()
            self.filtered(lambda task: task.checklist_id == checklist). \
                _update_task_instances_list(_records)
            _records = _records.with_context(checklist_computation=True)
            checklist._compute_progress_rates(_records)

    @api.one
    def _update_task_instances_list(self, records):
        for record in records:
            task_inst = self.env['checklist.task.instance'].search([
                ('task_id', '=', self.id),
                ('res_id', '=', record.id),
            ])
            valid_record = record.filtered_from_domain(self.filter_domain)
            if valid_record and not task_inst:
                task_inst.create({'task_id': self.id, 'res_id': record.id})
            elif not valid_record and task_inst:
                task_inst.unlink()
