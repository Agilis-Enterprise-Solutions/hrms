# -*- coding: utf-8 -*-
from odoo import models, fields, api


class JobPosting(models.Model):
    _inherit = 'hr.job'

    personnel_requisition_id = fields.Many2one('hr.personnel.requisition')
    proposed_salary = fields.Float(
        string="Proposed Salary",
        related='personnel_requisition_id.proposed_salary',
        readonly=True,
        store=True
    )

    skills_ids = fields.Many2many(
        'hr.employee.skills',
        string="Skills")

    job_qualification = fields.Text(string="Qualification")

    @api.multi
    def _get_historical_requisition(self):
        pass
