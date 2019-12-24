# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, timedelta
import logging
import itertools
import calendar
from odoo.exceptions import ValidationError
from num2words import num2words


class PersonnelRequisition(models.Model):
    _name = "hrmsv3.personnel_requisition"
    _rec_name = "job_req_id_seq"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']

    job_req_id_seq = fields.Char(string="Job Requisition Number.",
                                 required=True,
                                 copy=False,
                                 readonly=True,
                                 index=True,
                                 default=lambda self: _('New'))

    company_id = fields.Many2one('res.company', string="Company")
    job_position_id = fields.Many2one('hr.job', string="Job Position")
    department_id = fields.Many2one('hr.department', string="Department")
    job_location_id = fields.Many2one('res.company', string="Job Location")
    website_id = fields.Char(string="Website",
                             related='company_id.website',
                             readonly=True,
                             store=True
                             )
    skills_ids = fields.One2many(
        'hrmsv3.skills', 'personnel_requisition_id', string="Skills")

    responsible_id = fields.Many2one('res.users',  string="Responsible")
    email_alias = fields.Char(string="Email Alias")
    job_description = fields.Text(string="Job Description")
    job_qualification = fields.Text(string="Job Qualification")
    number_of_applicants = fields.Char(
        string="Number of Applicants",
        readonly=True
    )
    number_of_employees = fields.Char(string="Number of Employees",
                                      readonly=True
                                      )
    expected_new_employee = fields.Char(string="Expected New Employee",
                                        required=True,
                                        )
    proposed_salary = fields.Float(string="Proposed Salary")
    replacement_for_id = fields.Many2one(
        'hr.employee', string="Replacement For")
    replacement_for_id_check_box = fields.Boolean(
        string='Replacement')

    @api.model
    def create(self, vals):
        if vals.get('job_req_id_seq', _('New')) == ('New'):
            vals['job_req_id_seq'] = self.env['ir.sequence'].next_by_code(
                'job.requisition.sequence') or _('New')
        result = super().create(vals)
        return result


class Skills(models.Model):
    _name = 'hrmsv3.skills'
    _rec_name = 'skill_name'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']

    personnel_requisition_id = fields.Many2one(
        'hrmsv3.personnel_requisition',
        string="Personnel Requisition ID"
    )
    skill_name = fields.Char(string="Skill Name",
                             required=True
                             )
    skill_type_id = fields.Many2one('hrmsv3.skills_type', string="Skill Type")
    skill_description = fields.Text(string="Skill Description")
    skill_level_ids = fields.One2many(
        'hrmsv3.skills_level', 'skill_id', string="Skill Level")


class SkillsType(models.Model):
    _name = 'hrmsv3.skills_type'
    _rec_name = 'skill_type'
    skill_type = fields.Char(string="Skill Type")


class SkillsLevel(models.Model):
    _name = 'hrmsv3.skills_level'
    _rec_name = 'skill_level'

    skill_id = fields.Many2one('hrmsv3.skills', string="Skill Name")
    skill_name = fields.Char(string="Skill Name")
    skill_level = fields.Selection(
        string='Skill Level',
        selection=[
            ('beginner', 'Beginner'),
            ('novice', 'Novice'),
            ('adept', 'Adept'),
            ('advanced', 'Advanced'),
            ('expert', 'Expert'),
        ]
    )
    skill_level_description = fields.Char(string="Skill Level Description")
