# coding: utf-8
from odoo import models, fields, api
from logging import getLogger
from datetime import date


def log(**to_output):
    for key, value in to_output.items():
        getLogger().info("\n\n\n{0}: {1}\n\n".format(key, value))


class Training(models.Model):
    _name = 'hrms.training'
    _rec_name = 'training_name'

    employee_id = fields.Many2one('hr.employee')
    employee_ids = fields.Many2many('hr.employee',
                                    string='Attendees',
                                    required=True)

    training_name = fields.Char(required=True)
    subject = fields.Char('Training Subject', required=True)
    training_type = fields.Selection([
        ('Online', 'Online'),
        ('Classroom', 'Classroom'),
        ('Self-paced', 'Self-paced')
    ])
    date_completed = fields.Date()
    date = fields.Date()
    venue = fields.Char()
    trainor = fields.Char('Trainer', required=True)
    cost = fields.Float()
    sponsor = fields.Char()
    organizer = fields.Char()
    duration = fields.Integer('Duration (hr/s)')
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    acquire_certificate = fields.Boolean()
    description = fields.Text()
    venue = fields.Text()
    on_premises = fields.Boolean()
    status = fields.Selection([
        ('Proposed', 'Proposed'),
        ('Scheduled', 'Scheduled'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled')
    ], default='Proposed', compute="_set_status", store=True)

    @api.multi
    def done(self):
        self.write({
            'status': 'Completed'
        })

        return True

    @api.multi
    def cancel(self):
        self.write({
            'status': 'Cancelled'
        })

        return True

    @api.depends('start_date')
    def _set_status(self):
        for rec in self:
            if rec.start_date and (rec.start_date > date.today()):
                rec.status = 'Scheduled'


class Employee(models.Model):
    _inherit = 'hr.employee'

    training_ids = fields.One2many('hrms.training', 'employee_id',
                                   compute="_get_trainings",
                                   string='Assigned Training')

    @api.depends('name')
    def _get_trainings(self):
        for rec in self:
            rec.training_ids = self.env['hrms.training'].search([
            ]).filtered(lambda x: rec.id in x.employee_ids.ids)
