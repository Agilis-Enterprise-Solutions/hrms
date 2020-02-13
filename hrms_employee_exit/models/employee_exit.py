# coding: utf-8
from odoo import models, fields, api
from datetime import datetime, date


class InheritEmployeeAddExit(models.Model):
    _inherit = 'hr.employee'

    date_started = fields.Date()
    date_exited = fields.Date()
    years_of_service = fields.Char('Year(s) of Service',
                                   compute="_get_years_of_service")
    status = fields.Selection([
        ('Active', 'Active'),
        ('Resigned', 'Resigned'),
        ('Retired', 'Retired'),
        ('Terminated', 'Terminated')
    ])
    exit_reason = fields.Text()

    @api.depends('date_started')
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
