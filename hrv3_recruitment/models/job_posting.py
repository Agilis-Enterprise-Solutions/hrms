# -*- coding: utf-8 -*-
from odoo import models, fields, api


class JobPosting(models.Model):
    _inherit = 'hr.job'

    personnel_requisition_id = fields.Many2one('hrmsv3.personnel_requisition')
    proposed_salary = fields.Float(
        string="Proposed Salary",
        related='personnel_requisition_id.proposed_salary',
        readonly=True,
        store=True
    )

    skills_ids = fields.Many2many(
        'hrmsv3.skills',
        # 'personnel_requisition_id',
        string="Skills")

    # skill_name = fields.Many2one(
    #     'hrmsv3.skills_name',
    #     string="Skill Name",
    #     related='personnel_requisition_id.skills_ids.skill_name',
    #     readonly=True,
    #     store=True

    # )
    # skill_description = fields.Text(
    #     string="Skill Description",
    #     related='personnel_requisition_id.skills_ids.skill_description',
    #     readonly=True,
    #     store=True
    # )

    # skill_type = fields.Char(
    #     string="Skill Type",
    #     related='personnel_requisition_id.skills_ids.skill_type_id.skill_type',
    #     readonly=True,
    #     store=True
    # )

    # skill_level = fields.Selection(
    #     string='skill_level',
    #     selection=[
    #         ('beginner', 'Beginner'),
    #         ('novice', 'Novice'),
    #         ('adept', 'Adept'),
    #         ('advanced', 'Advanced'),
    #         ('expert', 'Expert'),
    #     ],

    # skill_level = fields.Char(string="Skill Level",
    #     related='personnel_requisition_id.skills_ids.skill_level_ids.skill_level',
    #             store=True
    # )
    # skill_level_description = fields.Char(
    #     string="Skill Level Description",
    #     related="personnel_requisition_id.skills_ids.skill_level_ids.skill_level_description")

    job_qualification = fields.Text(string="Qualification")

    @api.multi
    def _get_historical_requisition(self):
        pass
