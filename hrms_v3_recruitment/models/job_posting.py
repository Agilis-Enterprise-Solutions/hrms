# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, timedelta
import logging
import itertools
import calendar
from odoo.exceptions import ValidationError
from num2words import num2words


class JobPosting(models.Model):
    _inherit = 'hr.job'

    personnel_requisition_id = fields.Many2one('hrmsv3.personnel_requisition')
    proposed_salary = fields.Float(
        string="Proposed Salary",
        related='personnel_requisition_id.proposed_salary',
        readonly=True,
        store=True
    )

    skill_type = fields.Char(
        string="Skill Type",
        related='personnel_requisition_id.skills_ids.skill_type_id.skill_type',
        readonly=True,
        store=True
    )
    skill_level = fields.Selection(
        string='skill_level',
        selection=[
            ('beginner', 'Beginner'),
            ('novice', 'Novice'),
            ('adept', 'Adept'),
            ('advanced', 'Advanced'),
            ('expert', 'Expert'),
        ],
        related='personnel_requisition_id.skill_level',
        readonly=True,
        store=True
    )
    skill_level_description = fields.Char(
        string="Skill Level Description",
        related="personnel_requisition_id.skill_level_description")

    job_qualification = fields.Text(string="Qualification",
                                    related='personnel_requisition_id.job_qualification',
                                    readonly=True,
                                    store=True
                                    )
