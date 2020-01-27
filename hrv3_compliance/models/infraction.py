# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Infractions(models.Model):
    _name = 'hr.infraction'
    _rec_name = 'emp_id'

    emp_id = fields.Many2one('hr.employee', string="Employee")
    job_id = fields.Many2one('hr.job', string="Job",
                             related='emp_id.job_id',
                             readonly=True,
                             store=True
                             )
    manager_id = fields.Many2one('hr.employee', string="Manager",
                                 related='emp_id.parent_id',
                                 readonly=True,
                                 store=True
                                 )

    violation_id = fields.Char(string='Violation')
    policy_id = fields.Char(string='Policies Violated')
    frequency_id = fields.Char(string='Frequency')
    violation_date = fields.Date(string="Date of Violation")
    case_status = fields.Char(string='Case Status')
    state = fields.Selection(string='status',
                             selection=[
                                 ('open', 'Open'),
                                 ('in_progress', 'In Progress'),
                                 ('closure', 'For Case Closure'),
                                 ('closed', 'Closed')
                             ]
                             )
    violation_details = fields.Text(string="How Did It Occur?",
                                    required=True
                                    )
    corrective_action = fields.Text(string="Corrective Action")


class PolicyCode(models.Model):
    _name = "hr.company.policy"
    _rec_name = 'name'

    name = fields.Char(string="Policy Code")
    offense_code_id = fields.Many2one(
        'hr.company.offense', string="Offense Code")
    description = fields.Text(string="Policy Description")


class OffenseCode(models.Model):
    _name = "hr.company.offense"
    _rec_name = "name"

    name = fields.Char(string="Offense Code",
                       size=1
                       )
    corrective_action_ids = fields.Many2many(
        'hr.company.offense.frequency', string='Corrective Actions',)
    description = fields.Text(string="Offense Code Description")
    frequency = fields.Integer(string="Frequency", compute="_get_frequency")
    corrective_action_enumerate = fields.Text(string="Corrective Actions",
                                              readonly=True,
                                              compute="_get_frequency"
                                              )

    @api.depends("corrective_action_ids")
    def _get_frequency(self):
        counter = 0
        list = []
        for i in self.corrective_action_ids:
            counter += 1
            list.append(i.action)
        self.frequency = counter


class CorrectiveAction(models.Model):
    _name = "hr.company.offense.frequency"
    _rec_name = 'action'

    offense_code_id = fields.Many2one(
        'hr.company.offense', string="Offense Code")

    name = fields.Char(string="Offense Frequency", size=64)

    action = fields.Selection(
        string='Action',
        selection=[('verbal', 'Verbal Warning'),
                   ('written', 'Written Warning'),
                   ('suspension', 'Suspension'),
                   ('demotion', 'Demotion'),
                   ('dismissal', 'Dismissal'),
                   ]
    )


class Violation(models.Model):
    _name = "hr.company.violation"

    name = fields.Char(string="Violation", size=128)
    description = fields.Text(string="Violation Description")
    policy_violated_ids = fields.Many2many(
        'hr.company.violation.policy.offense', 'violation_id', string="Policy Violated")


class PolicyOffenseViolationLine(models.Model):
    _name = "hr.company.violation.policy.offense"

    policy_id = fields.Many2one('hr.company.policy', string="Policy Code")
    offense_id = fields.Many2one('hr.company.offense', string="Offense Code")

    @api.multi
    def name_get(self):
        data = []
        for i in self:
            display_value = '{} - {}'.format(i.policy_id.name,
                                             i.offense_id.name)
            data.append((i.id, display_value))
        return data


class ActionHistory(models.Model):
    _name = 'hr.infraction.action_history'


    stage = fields.Selection(
        string='Stage',
        selection=[
            ('incident_report', 'Incident Report'),
            ('inv_nte_issuance', 'Investigation and NTE Issuance'),
            ('collaboration', 'Collaboration with IMC'),
            ('corrective_action', 'Corrective Action'),
        ])

    corrective_action = fields.Many2one('hr.company.offense.frequency')
    violation_id = fields.Many2one('hr.company.violation', string="Violation")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    submit_nte = fields.Boolean(string="Submit NTE")
    attachment = fields.Binary(string='Attachment')
    notes = fields.Text(string="Notes")