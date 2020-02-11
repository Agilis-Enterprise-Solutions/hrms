# coding: utf-8
from odoo import models, fields, api
from logging import getLogger


def log(**to_output):
    for key, value in to_output.items():
        getLogger().info("\n\n\n{0}: {1}\n\n".format(key, value))


class Training(models.Model):
    _name = 'hrv3.training'
    _rec_name = 'training_name'

    employee_id = fields.Many2one('hr.employee')
    employee_ids = fields.Many2many('hr.employee',
                                    string='Employees Attending')

    training_name = fields.Char(required=True)
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


class Employee(models.Model):
    _inherit = 'hr.employee'

    training_ids = fields.One2many('hrv3.training', 'employee_id',
                                   compute="_get_trainings",
                                   string='Assigned Training')

    @api.depends('name')
    def _get_trainings(self):
        for rec in self:
            rec.training_ids = self.env['hrv3.training'].search([
            ]).filtered(lambda x: rec.id in x.employee_ids.ids)
