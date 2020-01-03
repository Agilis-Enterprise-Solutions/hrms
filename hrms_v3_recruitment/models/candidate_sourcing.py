# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date
import re
import logging

_logger = logging.getLogger("_name_")


class Applicant(models.Model):
    _inherit = "hr.applicant"

    skills_ids = fields.Many2many(
        'hrmsv3.skills',
        string="Skills")

    blacklisted = fields.Boolean(string="Blacklisted")

    character_reference = fields.One2many('hr.character.reference',
                                          'character_id',
                                          string="Character References")

    candiddate_skills = fields.One2many('hr.candidate.skill',
                                        'candidate_skill_id',
                                        string="Candidate Skill")

    candiddate_education = fields.One2many('hr.candidate.education',
                                           'education_id',
                                           string="Candidate Education")

    candiddate_work_history = fields.One2many('hr.candidate.work.history',
                                              'work_history_id',
                                              string="Candidate Work History")

    @api.multi
    def create_job_offer(self):
        pass

    @api.multi
    def action_get_assessment_tree_view(self):
        pass

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
        if self.character_email and not emailPattern.match(self.character_email):
            raise ValidationError("Email is in Incorrect format \n e.g. example@company.com")


class CandidateSkill(models.Model):
    _name = "hr.candidate.skill"
    _rec_name = "candidate_skill"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']

    candidate_skill_id = fields.Many2one('hr.applicant')
    candidate_skill = fields.Many2one('hr.candidate.skill.type', "Skill Name",
                                      required=True)
    candidate_skill_desc = fields.Text("Description", required=True)


class CandidateSkillType(models.Model):
    _name = "hr.candidate.skill.type"
    _rec_name = "candidate_skill"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']

    candidate_skill = fields.Char("Skill Name", required=True)


class CandidateWorkHistory(models.Model):
    _name = "hr.candidate.work.history"
    _rec_name = "work_history_id"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']

    work_history_id = fields.Many2one('hr.applicant')
    company_name = fields.Char("Company Name", required=True)
    line_of_business = fields.Many2one('hr.candidate.work.history.company',
                                       "Line Of Business")
    position = fields.Many2one('hr.candidate.work.history.position', "Position")
    address = fields.Char("Address")
    start_date = fields.Date("Date of Start", required=True)
    end_date = fields.Date("Date of End", required=True)
    years = fields.Char("Number of years", compute="get_year_services")

    @api.depends('start_date','end_date')
    def get_year_services(self):
        for rec in self:
            years_services = str(int(int((rec.end_date - rec.start_date).days) / 365)) + " Years"
            month = int(int((rec.end_date - rec.start_date).days) * 0.0328767)
            if month > 12:
                month_services = str(month % 12) + " Months"
            else:
                month_services = str(month) + " Months"
            rec.years = years_services + " , " + month_services


class CandidateCompanyLine(models.Model):
    _name = "hr.candidate.work.history.company"
    _rec_name = "line_of_business"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']

    line_of_business = fields.Char("Line Of Business", required=True)


class CandidateCompanyPosition(models.Model):
    _name = "hr.candidate.work.history.position"
    _rec_name = "position"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']

    position = fields.Char("Position", required=True)


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
    job_position = fields.Many2one('hr.job',"Job Position Applied",
                                   required=True)
    recruitment_stage = fields.Many2one('hr.recruitment.stage',
                                        "Recruitment Stage", required=True)
    responsible = fields.Many2one('res.users', "Responsible", required=True)
    reason = fields.Text("Reason", required=True, default="N/A")
    number_of_days = fields.Char("Number of Days", default="0")

    @api.multi
    def _default_stage_id(self):
        if self._context.get('default_job_id'):
            ids = self.env['hr.recruitment.stage'].search([
                '|',
                ('job_id', '=', False),
                ('job_id', '=', self._context['default_job_id']),
                ('fold', '=', False)
            ], order='sequence asc', limit=1).ids
            if ids:
                return ids[0]
        return False

    @api.multi
    def reset_applicant(self):
        """ Reinsert the applicant into the recruitment pipe in the first stage"""
        default_stage_id = self._default_stage_id()
        self.write({
            'active': True,
            'stage_id': default_stage_id
        })
