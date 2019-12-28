from odoo import http
from odoo.http import request


class Reminders(http.Controller):

    @http.route('/pop-up_reminders/all_reminder', type='json', auth="public")
    def all_reminder(self):
        reminder = []

        for i in request.env['popup.reminder'].search([]):

            reminder.append(i.name)
        return reminder

    @http.route('/pop-up_reminders/reminder_active', type='json', auth="public")
    def reminder_active(self, **kwargs):
        reminder_value = kwargs.get('reminder_name')
        value = []

        for i in request.env['popup.reminder'].search([('name', '=', reminder_value)]):
            value.append(i.model_name.model)
            value.append(i.model_field.name)
            value.append(i.search_by)
            value.append(i.date_set)
            value.append(i.date_from)
            value.append(i.date_to)
        # peeps=request.env[value[0]].search([('birthday', '=',value[3])])
        # for i in peeps:
        #     print i.work_email
        return value
