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
        string="Skills")

    job_qualification = fields.Text(string="Qualification")

    @api.multi
    def _get_historical_requisition(self):
        pass
