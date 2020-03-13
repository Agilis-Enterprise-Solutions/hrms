# coding: utf-8
from odoo import models, fields, api
from datetime import date


class InheritEmployeeAddExit(models.Model):
    _inherit = 'hr.employee'

    on_hold = fields.Boolean('On Hold')
    date_started = fields.Date('Date Started')
    date_exited = fields.Date('Exit Date')
    years_of_service = fields.Char('Year(s) of Service',
                                   compute="_get_years_of_service")
    status = fields.Selection([
        ('Active', 'Active'),
        ('Resigned', 'Resigned'),
        ('Retired', 'Retired'),
        ('Terminated', 'Terminated')
    ], default='Active', string="Status")
    exit_reason = fields.Text('Exit Reason')
    separation_id = fields.Many2one('hr.separation','Separation File')

    @api.depends('date_started','date_exited')
    def _get_years_of_service(self):
        for rec in self:
            if rec.date_started:
                years_services = str(int((date.today()
                                          - rec.date_started).days
                                         / 365)) + " Year(s)"
                month = int((date.today()
                             - rec.date_started).days * 0.0328767)
                if month > 12:
                    month_services = str(month % 12) + " Month(s)"
                else:
                    month_services = str(month) + " Month(s)"
                rec.years_of_service = years_services + " , " + month_services
