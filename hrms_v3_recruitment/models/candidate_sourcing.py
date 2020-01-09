# coding: utf-8
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date
import re
from logging import getLogger


def log(**to_output):
    for key, value in to_output.items():
        getLogger().info("\n\n\n{0}: {1}\n\n".format(key, value))


class Contract(models.Model):
    _inherit = 'hr.contract'

    def _get_default_employee_id_wage(self):
        try:
            return self._context['employee_id'], self._context['wage']
        except KeyError:
            return None

    employee_id = fields.Many2one('hr.employee', string='Employee',
                                  default=(lambda self:
                                           self._get_default_employee_id_wage()[0]))
    wage = fields.Monetary('Wage', digits=(16, 2), required=True,
                           default=(lambda self:
                                    self._get_default_employee_id_wage()[1]),
                           track_visibility="onchange",
                           help="Employee's monthly gross wage.")


class Allowance(models.Model):
    _name = 'hr.allowance'

    job_offer_id = fields.Many2one('hr.job.offer')
    allowance_description = fields.Text(required=True)
    amount_per_cut_off = fields.Float(required=True)
    allowance_type = fields.Selection([
        ('Recurring', 'Recurring'),
        ('Until Validity Date', 'Until Validity Date')
    ])
    until_validity_date = fields.Date()


class JobOffer(models.Model):
    _name = 'hr.job.offer'
    _description = 'Job Offer'

    allowance_ids = fields.One2many('hr.allowance', 'job_offer_id')
    name = fields.Char('Job Offer Reference', required=True)
    active = fields.Boolean(default=True)
    employee_id = fields.Many2one('hr.employee', string='Employee')
    department_id = fields.Many2one('hr.department', string="Department")
    type_id = fields.Many2one('hr.contract.type', string="Employee Category",
                              required=True,
                              default=lambda self: self.env['hr.contract.type'].search([],
                                                                                       limit=1))
    job_id = fields.Many2one('hr.job', string='Job Position')
    date_start = fields.Date('Start Date', required=True,
                             default=fields.Date.today,
                             help="Start date of the contract.")
    date_end = fields.Date('End Date',
                           help="End date of the contract (if it's a fixed-term contract).")
    trial_date_end = fields.Date('End of Trial Period',
                                 help="End date of the trial period (if there is one).")
    resource_calendar_id = fields.Many2one(
        'resource.calendar', 'Working Schedule',
        default=lambda self: self.env['res.company']._company_default_get().resource_calendar_id.id)
    wage = fields.Monetary('Wage', digits=(16, 2), required=True,
                           track_visibility="onchange",
                           help="Employee's monthly gross wage.")
    advantages = fields.Text('Advantages')
    notes = fields.Text('Notes')
    state = fields.Selection([
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected')
    ], string='Status', group_expand='_expand_states',
                             track_visibility='onchange',
                             help='Status of the contract',
                             default='New')
    company_id = fields.Many2one('res.company',
                                 default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one(string="Currency",
                                  related='company_id.currency_id',
                                  readonly=True)
    permit_no = fields.Char('Work Permit No', related="employee_id.permit_no",
                            readonly=False)
    visa_no = fields.Char('Visa No', related="employee_id.visa_no",
                          readonly=False)
    visa_expire = fields.Date('Visa Expire Date',
                              related="employee_id.visa_expire", readonly=False)
    reported_to_secretariat = fields.Boolean('Social Secretariat',
                                             help='Click this button when the contract information has been transferred to the social secretariat.')

    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

    @api.multi
    def create_contract(self):
        log(employee_id=self.employee_id.id)

        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.contract',
            'context': {
                'employee_id': self.employee_id.id,
                'wage': self.wage
            }
        }

    @api.multi
    def accept_job_offer(self):
        self.write({
            'state': 'Accepted'
        })

        return True

    @api.multi
    def reject_job_offer(self):
        self.write({
            'state': 'Rejected'
        })

        return True

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            self.job_id = self.employee_id.job_id
            self.department_id = self.employee_id.department_id
            self.resource_calendar_id = self.employee_id.resource_calendar_id

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        if self.filtered(lambda c: c.date_end and c.date_start > c.date_end):
            raise ValidationError(_('Contract start date must be earlier than contract end date.'))

    # @api.model
    # def update_state(self):
    #     self.search([
    #         ('state', '=', 'open'),
    #         '|',
    #         '&',
    #         ('date_end', '<=', fields.Date.to_string(date.today()
    #                                                  + relativedelta(days=7))),
    #         ('date_end', '>=', fields.Date.to_string(date.today()
    #                                                  + relativedelta(days=1))),
    #         '&',
    #         ('visa_expire', '<=', fields.Date.to_string(date.today()
    #                                                     + relativedelta(days=60))),
    #         ('visa_expire', '>=', fields.Date.to_string(date.today()
    #                                                     + relativedelta(days=1))),
    #     ]).write({
    #         'state': 'pending'
    #     })

    #     self.search([
    #         ('state', 'in', ('open', 'pending')),
    #         '|',
    #         ('date_end', '<=', fields.Date.to_string(date.today()
    #                                                  + relativedelta(days=1))),
    #         ('visa_expire', '<=', fields.Date.to_string(date.today()
    #                                                     + relativedelta(days=1))),
    #     ]).write({
    #         'state': 'close'
    #     })

    #     return True

    # @api.multi
    # def _track_subtype(self, init_values):
    #     self.ensure_one()
    #     if 'state' in init_values and self.state == 'pending':
    #         return 'hr_contract.mt_contract_pending'
    #     elif 'state' in init_values and self.state == 'close':
    #         return 'hr_contract.mt_contract_close'
    #     return super(Contract, self)._track_subtype(init_values)


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

    assessment_ids = fields.One2many('hr.assessment','job_id',
                                     string="Assessments")

    @api.multi
    def create_job_offer(self):
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.job.offer'
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
                ('id', '!=' , self.id)
            ])
            duplicate_active = self.env['hr.applicant'].search([
                ('partner_name', '=', self.partner_name),
                ('active', '=', True),
                ('job_id', '=', self.job_id.id),
                ('id', '!=' , self.id)
            ])

            if duplicate_archived or duplicate_active:
                raise ValidationError("Application Not saved. Application has duplicate entry, please review other application")


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
            years_services = (str(int(int((rec.end_date - rec.start_date).days)
                                      / 365)) + " Years")
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
