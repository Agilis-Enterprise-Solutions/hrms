# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, timedelta
import logging
import itertools
import calendar
from odoo.exceptions import ValidationError
from num2words import num2words


class Applicant(models.Model):
    _inherit = "hr.applicant"

    skills_ids = fields.Many2many(
        'hrmsv3.skills',
        string="Skills")

    @api.multi
    def create_job_offer(self):
        pass

    @api.multi
    def action_get_assessment_tree_view(self):
        pass
