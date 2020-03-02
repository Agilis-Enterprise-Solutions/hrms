# coding: utf-8
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date
import re
import logging
from logging import getLogger
_logger = logging.getLogger("_name_")


def log(**to_output):
    for key, value in to_output.items():
        getLogger().info("\n\n\n{0}: {1}\n\n".format(key, value))


class Contract(models.Model):
    _inherit = 'hr.contract'

    allowance_ids = fields.One2many('hr.allowance', 'contract_id')


class Allowance(models.Model):
    _name = 'hr.allowance'

    contract_id = fields.Many2one('hr.contract')
    allowance_description = fields.Char(required=True)
    amount_per_cut_off = fields.Float(required=True)
    allowance_type = fields.Selection([
        ('Recurring', 'Recurring'),
        ('Until Validity Date', 'Until Validity Date')
    ])
    until_validity_date = fields.Date()


class Applicant(models.Model):
    _inherit = "hr.applicant"

    skills_ids = fields.Many2many(
        'hrmsv3.skills',
        string="Skills", compute="get_skills")

    @api.depends("job_id")
    def get_skills(self):
        self.update({
            'skills_ids': [(6, 0, self.job_id.skills_ids.ids)],
        })
        return True

    blacklisted = fields.Boolean(string="Blacklisted")

    character_reference = fields.One2many('hr.character.reference',
                                          'character_id',
                                          string="Character References")

    candiddate_skills = fields.One2many('hrmsv3.skills', 'candidate_sourcing_id',
                                        string="Candidate Skill")

    candiddate_education = fields.One2many('hr.candidate.education',
                                           'education_id',
                                           string="Candidate Education")

    candiddate_work_history = fields.One2many('hr.candidate.work.history',
                                              'work_history_id',
                                              string="Candidate Work History")

    assessment_ids = fields.Many2many('hr.assessment',
                                    #   'job_id',
                                      string="Assessments"
                                      )

    requisition_id = fields.Many2one('hrmsv3.personnel_requisition',
                                     string="Job Requisition",
                                     )

    @api.multi
    def create_contract(self):
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.contract'
        }

    @api.multi
    def action_get_assessment_tree_view(self):
        return {
            'name': _('Assessments'),
            'domain': [('applicant_name', '=', self.partner_name)],
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'view_id': False,
            'res_model': 'hr.assessment',
        }

    @api.multi
    def archive_applicant(self):
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'candidate_refuse.wizard',
            'target': 'new',
        }

    @api.multi
    def toggle_active(self):
        """ Inverse the value of the field ``active`` on the records in ``self``. """
        for record in self:
            if not self.blacklisted:
                record.active = not record.active
            else:
                return {
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'blocked.candidate.wizard',
                    'target': 'new',
                }

    @api.multi
    def reset_applicant(self):
        for record in self:
            if not self.blacklisted:
                record.active = not record.active
            else:
                return {
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'blocked.candidate.wizard',
                    'target': 'new',
                }

    @api.constrains('partner_name')
    def _duplicate_application(self):
        if self.partner_name and self.job_id:
            duplicate_archived = self.env['hr.applicant'].search([
                ('partner_name', '=', self.partner_name),
                ('active', '=', False),
                ('job_id', '=', self.job_id.id),
                ('id', '!=', self.id)
            ])
            duplicate_active = self.env['hr.applicant'].search([
                ('partner_name', '=', self.partner_name),
                ('active', '=', True),
                ('job_id', '=', self.job_id.id),
                ('id', '!=', self.id)
            ])

            if duplicate_archived or duplicate_active:
                raise ValidationError(
                    "Application Not saved. Application has duplicate entry, please review other application")


class CharacterReference(models.Model):
    _name = "hr.character.reference"
    _rec_name = "character_name"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']

    character_id = fields.Many2one('hr.applicant')
    character_name = fields.Char("Name", required=True)
    character_email = fields.Char("Email", required=True)
    character_number = fields.Char("Mobile Number", required=True, size=11)
    character_credentials = fields.Char("Credentials", required=True)

    @api.constrains('character_email')
    def _check_email(self):
        emailPattern = re.compile(r'[\w.-]+@[\w-]+[.]+[\w.-]')
        if self.character_email:
            if (self.character_email
                    and not emailPattern.match(self.character_email)):
                raise ValidationError(
                    "Email is in Incorrect format \n e.g. example@company.com")


# class CandidateSkill(models.Model):
#     _name = "hr.candidate.skill"
#     _rec_name = "candidate_skill"
#     _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']
#
#     candidate_skill_id = fields.Many2one('hr.applicant')
#     candidate_skill = fields.Many2one('hr.candidate.skill.type', "Skill Name",
#                                       required=True)
#     candidate_skill_desc = fields.Text("Description", required=True)


# class CandidateSkillType(models.Model):
#     _name = "hr.candidate.skill.type"
#     _rec_name = "candidate_skill"
#     _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']
#
#     candidate_skill = fields.Char("Skill Name", required=True)


class CandidateWorkHistory(models.Model):
    _name = "hr.candidate.work.history"
    _rec_name = "work_history_id"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']

    work_history_id = fields.Many2one('hr.applicant')
    company_name = fields.Char("Company Name", required=True)
    line_of_business = fields.Many2one('hr.candidate.work.history.company',
                                       "Line Of Business")
    position = fields.Many2one('hr.job', "Position")
    address = fields.Char("Address")
    start_date = fields.Date("Date of Start", required=True)
    end_date = fields.Date("Date of End", required=True)
    years = fields.Char("Number of years", compute="get_year_services")

    @api.depends('start_date', 'end_date')
    def get_year_services(self):
        for rec in self:
            if rec.start_date and rec.end_date:
                years_services = str(int((rec.end_date
                                          - rec.start_date).days
                                         / 365)) + " Year(s)"
                month = int((rec.end_date
                             - rec.start_date).days * 0.0328767)
                if month > 12:
                    month_services = str(month % 12) + " Month(s)"
                else:
                    month_services = str(month) + " Month(s)"
                rec.years = years_services + " , " + month_services


class CandidateCompanyLine(models.Model):
    _name = "hr.candidate.work.history.company"
    _rec_name = "line_of_business"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']

    line_of_business = fields.Char("Line Of Business", required=True)


# class CandidateCompanyPosition(models.Model):
#     _name = "hr.candidate.work.history.position"
#     _rec_name = "position"
#     _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']
#
#     position = fields.Char("Position", required=True)


class CandidateEducation(models.Model):
    _name = "hr.candidate.education"
    _rec_name = "type_id"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']

    education_id = fields.Many2one('hr.applicant')
    type_id = fields.Many2one('hr.recruitment.degree', "Level of Education",
                              required=True)
    course = fields.Many2one('hr.candidate.education.strand', "Course/Strand")
    standard = fields.Char("Standard")
    year = fields.Integer("Year")
    school_name = fields.Char("School Name")
    address = fields.Char("Address")
    vital_info = fields.Char("Other vital Information")


class CandidateEducationCourseStrand(models.Model):
    _name = "hr.candidate.education.strand"
    _rec_name = "course_name"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']

    course_name = fields.Char("Course/Strand", required=True)


class CandidateBlacklisted(models.Model):
    _name = "hr.candidate.blacklisted"
    _rec_name = "applicant_name"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']

    applicant_name = fields.Char("Applicant Name", required=True)
    date_blocked = fields.Date("Date Blocked", required=True,
                               default=date.today())
    job_position = fields.Many2one('hr.job', "Job Position Applied",
                                   required=True)
    recruitment_stage = fields.Many2one('hr.recruitment.stage',
                                        "Recruitment Stage", required=True)
    responsible = fields.Many2one('res.users', "Responsible", required=True)
    reason = fields.Text("Reason", required=True, default="N/A")
    number_of_days = fields.Char("Number of Days", default="0")

    def reset_applicant(self):
        department = self.env['hr.applicant'].search([
            ('partner_name', '=', self.applicant_name),
            ('active', '=', False),
            ('job_id', '=', self.job_position.id)
        ])
        if department:
            department.write({
                'blacklisted': False,
                'active': True,
                'kanban_state': "normal"
            })
        self.unlink()

        return {
            'res_model': 'hr.applicant',
            'view_type': 'kanban',
            'view_mode': 'kanban',
            'view_id': False,
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
