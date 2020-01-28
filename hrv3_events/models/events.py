# coding: utf-8
from odoo import models, fields, api
from logging import getLogger


def log(**to_output):
    for key, value in to_output.items():
        getLogger().info("\n\n\n{0}: {1}\n\n".format(key, value))


class Training(models.Model):
    _inherit = 'event.event'

    employee_id = fields.Many2one('hr.employee')

    subject = fields.Char()
    training_type = fields.Selection([
        ('Online', 'Online'),
        ('Classroom', 'Classroom'),
        ('Self-paced', 'Self-paced')
    ], string="Type")
    date_completed = fields.Date()
    date = fields.Date()
    venue = fields.Char()
    trainor = fields.Char()
    hour = fields.Float()
    cost = fields.Float()
    sponsor = fields.Char()
    acquire_certificate = fields.Boolean()
    status = fields.Selection([
        ('Ongoing', 'Ongoing'),
        ('Completed', 'Completed')
    ])

    category_name = fields.Char(related='event_type_id.name')


class TrainingRegistration(models.Model):
    _inherit = 'event.registration'

    name = fields.Many2one('hr.employee', string='Attendee Name')


class Employee(models.Model):
    _inherit = 'hr.employee'

    training_ids = fields.One2many('event.event', 'employee_id',
                                   compute="_get_trainings",
                                   string='Assigned Training')

    @api.depends('name')
    def _get_trainings(self):
        for rec in self:
            rec.training_ids = self.env['event.event'].search([
                ('event_type_id.name', '=', 'Training')
            ])
