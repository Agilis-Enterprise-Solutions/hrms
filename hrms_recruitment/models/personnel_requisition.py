# coding: utf-8
from odoo import models, fields, api, _
from logging import getLogger
from odoo.exceptions import UserError, ValidationError
import re


def log(**to_output):
    for key, value in to_output.items():
        getLogger().info("\n\n\n{0}: {1}\n\n".format(key, value))


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
    department_id = fields.Many2one('hr.department', string="Department",
                                    related='job_position_id.department_id',
                                    readonly=True, store=True)
    job_location_id = fields.Many2one('res.partner', string="Job Location",
                                      related='job_position_id.address_id',
                                      readonly=True, store=True)
    website_id = fields.Char(string="Website",
                             related='job_position_id.address_id.website',
                             readonly=True, store=True)
    skills_ids = fields.One2many('hrmsv3.skills',
                                 'personnel_requisition_id',
                                 string="Skills")

    skill_name_ids = fields.One2many('hrmsv3.skills_name', 'requisition_id',
                                     string="Skills")

    responsible_id = fields.Many2one('res.users',  string="Responsible")
    email_alias = fields.Char(string="Email Alias")
    @api.constrains('email_alias')
    def _check_email(self):
        emailPattern = re.compile(r'[\w.-]+@[\w-]+[.]+[\w.-]')
        if self.email_alias:
            if (self.email_alias
                and not emailPattern.match(self.email_alias)):
                raise ValidationError("Email is in Incorrect format \n e.g. example@company.com")
    job_description = fields.Text(string="Job Description",
                                  related='job_position_id.description',
                                  readonly=True,
                                  store=True)
    job_qualification = fields.Text(string="Job Qualification")
    number_of_applicants = fields.Char(string="Number of Applicants",
                                       readonly=True)
    number_of_employees = fields.Char(string="Number of Employees",
                                      readonly=True)
    expected_new_employee = fields.Integer(string="Expected New Employee",
                                           required=True)
    proposed_salary = fields.Float(string="Proposed Salary")
    replacement_for_id = fields.Many2many('hr.employee', string="Replacement For",
                                          )
    replacement_emp_job_id = fields.Many2one('hr.job', string='Job Position',
                                             related='replacement_for_id.job_id',
                                             store=True)
    replacement_contract = fields.Many2many('hr.contract',
                                            string="Current Contract",
                                            compute='get_contract',
                                            )
    replacement_for_id_check_box = fields.Boolean(string='Replacement')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('for_approval', 'Waiting for Approval'),
        ('approved', 'Approved'),
        ('canceled', 'Canceled')
    ], string="Status", default="draft", readonly=True, copy=False)

    @api.model
    def create(self, vals):
        if vals.get('job_req_id_seq', _('New')) == ('New'):
            vals['job_req_id_seq'] = self.env['ir.sequence'].next_by_code(
                'job.requisition.sequence') or _('New')
        result = super(PersonnelRequisition, self).create(vals)
        return result

    @api.depends('replacement_for_id')
    def get_contract(self):
        result = []
        for record in self:
            replacement_ids = record.replacement_for_id
            for rec in replacement_ids:
                if rec.contract_id:
                    result.append(rec.contract_id.id)
        self.update({
            'replacement_contract': [(6, 0, result)]
        })

        return True

    @api.constrains('replacement_for_id', 'expected_new_employee')
    def check_replacement_employee_count(self):
        counter = 0
        for record in self:
            replacement_ids = record.replacement_for_id
            for rec in replacement_ids:
                counter += 1
                if counter > record.expected_new_employee:
                    raise UserError(
                        _('Number of employees to be replaced should not exceed number of expected employees.'))

    # Submit Button Function
    @api.multi
    def submit_jobreq_form(self):
        self.write({
            'state': 'for_approval',
        })
        return True

    # Approve Button Function
    @api.multi
    def approve_jobreq_form(self):
        for record in self:
            user_id = record.responsible_id.id
            job_qualification = record.job_qualification
            expected_new_employee = record.expected_new_employee
            skills_ids = record.skills_ids
            job_position = record.job_position_id
            proposed_salary = record.proposed_salary
            for rec in job_position:
                if skills_ids:
                    rec.skills_ids = skills_ids
                rec.write({
                    'user_id': user_id,
                    'no_of_recruitment': expected_new_employee,
                    'job_qualification': job_qualification,
                    'proposed_salary': proposed_salary
                })
        self.write({
            'state': 'approved',
        })
        return True

    # Cancel Button Function
    @api.multi
    def cancel_jobreq_form(self):
        self.write({
            'state': 'canceled',
        })
        return True

    # Commented out function. Redundant
    # Update Job Post Button Function
    # @api.multi
    # def action_hr_job_form(self):
        # for record in self:
        #     user_id = record.responsible_id.id
        #     job_qualification = record.job_qualification
        #     expected_new_employee = record.expected_new_employee
        #     skills_ids = record.skills_ids
        #     job_position = record.job_position_id
        #     proposed_salary = record.proposed_salary
        #     for rec in job_position:
        #         if skills_ids:
        #             rec.skills_ids = skills_ids
        #         rec.write({
        #             'user_id': user_id,
        #             'no_of_recruitment': expected_new_employee,
        #             'job_qualification': job_qualification,
        #             'proposed_salary': proposed_salary
        #         })
        # self.write({
        #     'state': 'approved',
        # })

    #     return True


class Skills(models.Model):
    _name = 'hrmsv3.skills'
    _rec_name = 'skill_name'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']

    # @api.depends('skill_name')
    # def _get_last_skill_level(self):
    #     for rec in self:
    #         if rec.skill_name.skill_level_ids:
    #             rec.skill_level_id = rec.skill_name.skill_level_ids[-1]

    employee_id = fields.Many2one('hr.employee')

    personnel_requisition_id = fields.Many2one('hrmsv3.personnel_requisition',
                                               string="Personnel Requisition ID")
    skill_name = fields.Many2one('hrmsv3.skills_name', string="Skill Name",
                                 required=True)
    skill_type_id = fields.Many2one('hrmsv3.skills_type',
                                    related='skill_name.skill_type_id',
                                    string="Skill Type")
    skill_description = fields.Text(string="Skill Description", related="skill_name.skill_description")
    skill_level_id = fields.Many2one('hrmsv3.skills_level',
                                     domain="[('skill_name_id', '=',skill_name)]",
                                     string="Skill Level")


class SkillName(models.Model):
    _name = 'hrmsv3.skills_name'
    _rec_name = 'skill_name'

    requisition_id = fields.Many2one('hrmsv3.personnel_requisition')

    skill_name = fields.Char(string="Skill Name", required=True)
    skill_type_id = fields.Many2one('hrmsv3.skills_type', string="Skill Type")
    skill_description = fields.Text()

    skill_level_ids = fields.One2many('hrmsv3.skills_level', 'skill_name_id',
                                      string="Skill Levels")


class SkillsType(models.Model):
    _name = 'hrmsv3.skills_type'
    _rec_name = 'skill_type'

    skill_type = fields.Char(string="Skill Type")


class SkillsLevel(models.Model):
    _name = 'hrmsv3.skills_level'
    _rec_name = 'skill_level'

    skill_name_id = fields.Many2one('hrmsv3.skills_name')

    skill_level = fields.Char(string="Skill Level")
    skill_level_description = fields.Char(string="Skill Level Description")
