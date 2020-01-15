# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging
_logger = logging.getLogger("_name_")


class PersonnelRequisition(models.Model):
    _name = "hrmsv3.personnel_requisition"
    _rec_name = "job_req_id_seq"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']

    STATUS = [
        ('draft', 'Draft'),
        ('for_approval', 'Waiting for Approval'),
        ('approved', 'Approved'),
        ('canceled', 'Canceled')
    ]
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
                                    readonly=True,
                                    store=True
                                    )
    job_location_id = fields.Many2one('res.partner', string="Job Location",
                                      related='job_position_id.address_id',
                                      readonly=True,
                                      store=True
                                      )
    website_id = fields.Char(string="Website",
                             related='job_position_id.address_id.website',
                             readonly=True,
                             store=True
                             )
    skills_ids = fields.Many2many(
        'hrmsv3.skills',
        string="Skills")

    responsible_id = fields.Many2one('res.users',  string="Responsible")
    email_alias = fields.Char(string="Email Alias")
    job_description = fields.Text(string="Job Description",
                                  related='job_position_id.description',
                                  readonly=True,
                                  store=True
                                  )
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
    replacement_emp_job_id = fields.Many2one('hr.job', string='Job Position',
                                             related='replacement_for_id.job_id',
                                            #  readonly=True,
                                             store=True
                                             )
    replacement_contract = fields.Many2one('hr.contract', string="Current Contract",
                                           related='replacement_for_id.contract_id',
                                        #    readonly=True,
                                           store=True
                                           )
    replacement_for_id_check_box = fields.Boolean(
        string='Replacement')

    

    state = fields.Selection(STATUS, string="Status",
                             default="draft", readonly=True, copy=False)

    @api.model
    def create(self, vals):
        if vals.get('job_req_id_seq', _('New')) == ('New'):
            vals['job_req_id_seq'] = self.env['ir.sequence'].next_by_code(
                'job.requisition.sequence') or _('New')
        _logger.info('\n\n\n{}\n\n\n'.format(vals))
        result = super(PersonnelRequisition, self).create(vals)
        return result

    @api.multi
    def submit_jobreq_form(self):
        self.write({
            'state': 'for_approval',
        })
        return True

    @api.multi
    def approve_jobreq_form(self):
        self.write({
            'state': 'approved',
        })
        return True

    @api.multi
    def cancel_jobreq_form(self):
        self.write({
            'state': 'canceled',
        })
        return True

    @api.multi
    def action_hr_job_form(self):
        # vals = []
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

        return True
        # {
        #     'name': _('Job Form'),
        #     'view_type': 'form',
        #     'res_model': 'hr.job',
        #     'view_id': False,
        #     'view_mode': 'form',
        #     'type': 'ir.actions.act_window',
        #     'res_id': self.job_position_id.id,
        # }


class Skills(models.Model):
    _name = 'hrmsv3.skills'
    _rec_name = 'skill_name'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']

    personnel_requisition_id = fields.Many2one(
        'hrmsv3.personnel_requisition',
        string="Personnel Requisition ID"
    )
    skill_name = fields.Many2one(
        'hrmsv3.skills_name',
        string="Skill Name",
        required=True
    )
    skill_type_id = fields.Many2one('hrmsv3.skills_type', string="Skill Type")
    skill_description = fields.Text(string="Skill Description")
    skill_level_ids = fields.Many2one(
        'hrmsv3.skills_level', string="Skill Level")


class SkillName(models.Model):
    _name = 'hrmsv3.skills_name'
    _rec_name = 'skill_name'

    skill_name = fields.Char(string="Skill Name")


class SkillsType(models.Model):
    _name = 'hrmsv3.skills_type'
    _rec_name = 'skill_type'
    skill_type = fields.Char(string="Skill Type")


class SkillsLevel(models.Model):
    _name = 'hrmsv3.skills_level'
    _rec_name = 'skill_level'

    skill_id = fields.Many2one('hrmsv3.skills', string="Skill Name")

    skill_level = fields.Char(string="Skill Level")
    skill_level_description = fields.Char(string="Skill Level Description")
