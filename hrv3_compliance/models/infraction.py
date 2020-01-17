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


class Policy(models.Model):
    _name = "hr.company.policy"
    _rec_name = 'name'

    name = fields.Char(string="Policy Code")
    offense_code_id = fields.Many2one('hr.company.offense',string="Offense Code")
    description = fields.Text(string="Policy Description")


class Offense(models.Model):
    _name = "hr.company.offense"
    _rec_name = "name"

    name = fields.Char(string="Offense Code")
    # frequency = fields.Integer(string="Frequency")
    # corrective_action = fields.Char(string="Corrective Action")
    description = fields.Text(string="Offense Code Description")