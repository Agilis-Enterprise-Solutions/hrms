# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, timedelta

_logger = logging.getLogger("_name_")


"""Main Model of Infractions which houses the fields
    responsible for the main form and tree view"""


class Infractions(models.Model):
    _name = "hr.infraction"
    _rec_name = "emp_id"
    _description = "Infractions Management"
    _inherit = ["mail.thread", "mail.activity.mixin", "resource.mixin"]

    emp_id = fields.Many2one(
        "hr.employee", string="Employee", track_visibility="onchange"
    )
    job_id = fields.Many2one(
        "hr.job", string="Job", related="emp_id.job_id", readonly=True, store=True
    )
    manager_id = fields.Many2one(
        "hr.employee",
        string="Manager",
        related="emp_id.parent_id",
        readonly=True,
        store=True,
    )

    violation_id = fields.Many2one(
        "hr.company.violation", string="Violation", track_visibility="onchange"
    )
    policy_violated_id = fields.Many2one(
        "hr.company.policy",
        string="Policies Violated",
        track_visibility="onchange",
        # domain=[('id','in',violation_id)]
        
        # context={'default_violation_id': violation_id}
        
    )

    frequency_id = fields.Many2one(
        "hr.company.offense.frequency",
        string="Frequency",
        track_visibility="onchange",
        # compute="_compute_frequency_ids",
    )

    # @api.depends("violation_id")
    # def _get_policy_ids(self):
    #     self.update(
    #         {"policy_violated_ids": [
    #             (6, 0, self.violation_id.policy_violated_ids.ids)]}
    #     )
    #     return True

    # @api.depends("violation_id", "policy_violated_ids")
    # def _compute_frequency_ids(self):
    #     result = []
    #     for i in self:
    #         policy_violated_ids = i.violation_id.policy_violated_ids
    #         for j in policy_violated_ids:
    #             offense_id = j.offense_code_id
    #             for k in offense_id:
    #                 corrective_action_ids = k.corrective_action_ids

        # self.update(
        #     # {"frequency_ids": [
        #     #     (6, 0, self.violation_id.policy_violated_ids.ids)]}
        # )
        # return True

    violation_date = fields.Date(
        string="Date of Violation", track_visibility="onchange"
    )
    case_status = fields.Char(string="Case Status")
    state = fields.Selection(
        string="status",
        selection=[
            ("draft", "Draft"),
            ("open", "Open"),
            ("in_progress", "In Progress"),
            ("for_closure", "For Case Closure"),
            ("closed", "Closed"),
        ],
        default="draft",
    )
    violation_details = fields.Text(
        string="How Did It Occur?", required=True, track_visibility="onchange"
    )
    history = fields.One2many(
        "hr.infraction.action_history",
        "infraction_id",
        string="Action History",
        track_visibility="onchange",
    )

    @api.multi
    def type_offenses_others(self):
        pass


"""Company Policy houses data of company policies with their corresponding offenses"""


class PolicyCode(models.Model):
    _name = "hr.company.policy"
    _rec_name = "name"
    _description = "Company Policy houses data of company policies with their corresponding offenses"
    _inherit = ["mail.thread", "mail.activity.mixin", "resource.mixin"]

    name = fields.Char(string="Policy Code")
    offense_code_id = fields.Many2one(
        "hr.company.offense", string="Offense Code")
    description = fields.Text(string="Policy Description")


class OffenseCode(models.Model):
    _name = "hr.company.offense"
    _rec_name = "name"

    name = fields.Char(string="Offense Code", size=64)
    corrective_action_ids = fields.Many2many(
        "hr.company.offense.frequency", string="Corrective Actions",
    )
    description = fields.Text(string="Offense Code Description")
    frequency = fields.Integer(string="Frequency", compute="_get_frequency")
    corrective_action_enumerate = fields.Text(
        string="Corrective Actions", readonly=True, compute="_get_frequency"
    )

    @api.depends("corrective_action_ids")
    def _get_frequency(self):
        counter = 0
        list = []
        for i in self:
            corrective_action_ids = i.corrective_action_ids
            for j in corrective_action_ids:
                counter += 1
                list.append(j.action)
            i.frequency = len(i.corrective_action_ids.ids)


"""Corrective Action houses Offense Codes that are used for each Company Policy"""


class CorrectiveAction(models.Model):
    _name = "hr.company.offense.frequency"
    _rec_name = "name"
    _description = "Corrective Action houses Offense Codes that are used for each Company Policy"
    
    frequencies = [
        ("1st_offense", "1st Offense"),
        ("2nd_offense", "2nd Offense"),
        ("3rd_offense", "3rd Offense"),
        ("4th_offense", "4th Offense"),
        ("5th_offense", "5th Offense"),
        ("6th_offense", "6th Offense"),
        ("7th_offense", "7th Offense"),
        ("8th_offense", "8th Offense"),
        ("9th_offense", "9th Offense"),
        ("10th_offense", "10th Offense"),
    ]
    offense_code_id = fields.Many2one(
        "hr.company.offense", string="Offense Code")

    name = fields.Char(string="Offense Frequency",
                       size=64, compute="_get_name")

    frequency = fields.Selection(
        string="Offense Frequency", selection=frequencies, required=True
    )

    action = fields.Selection(
        string="Action",
        selection=[
            ("Verbal Warning", "Verbal Warning"),
            ("Written Warning", "Written Warning"),
            ("Suspension", "Suspension"),
            ("Demotion", "Demotion"),
            ("Dismissal", "Dismissal"),
        ],
        required=True,
    )

    api.depends("frequency")

    def _get_name(self):
        frequencies = self.frequencies
        for i in self:
            if i.frequency == frequencies[0][0]:
                i.name = frequencies[0][1]
            elif i.frequency == frequencies[1][0]:
                i.name = frequencies[1][1]
            elif i.frequency == frequencies[2][0]:
                i.name = frequencies[2][1]
            elif i.frequency == frequencies[3][0]:
                i.name = frequencies[3][1]
            elif i.frequency == frequencies[4][0]:
                i.name = frequencies[4][1]
            elif i.frequency == frequencies[5][0]:
                i.name = frequencies[5][1]
            elif i.frequency == frequencies[6][0]:
                i.name = frequencies[6][1]
            elif i.frequency == frequencies[7][0]:
                i.name = frequencies[7][1]
            elif i.frequency == frequencies[8][0]:
                i.name = frequencies[8][1]
            else:
                i.name = frequencies[9][1]

    # @api.multi
    # def name_get(self):
    #     data = []
    #     for i in self:
    #         display_value = frequencies[i]
    #         data.append((i.id, display_value))
    #     return data


"""Violation deals with acts committed by offenders which are then assigned 
    offense codes based on company policies violated by said act/s"""


class Violation(models.Model):
    _name = "hr.company.violation"
    _inherit = ["mail.thread", "mail.activity.mixin", "resource.mixin"]

    name = fields.Char(string="Violation", size=128)
    description = fields.Text(string="Violation Description")
    policy_violated_ids = fields.Many2many(
        "hr.company.policy", string="Policy Violated"
    )

    # infraction_id = fields.Many2one('hr.infraction',string="Infraction")



"""Provides Tree View of Policy and Offense codes commited """


class PolicyOffenseViolationLine(models.Model):
    _name = "hr.company.violation.policy.offense"
    _description = "Provides Tree View of Policy and Offense codes commited"
    _inherit = ["mail.thread", "mail.activity.mixin", "resource.mixin"]

    policy_id = fields.Many2one("hr.company.policy", string="Policy Code")
    offense_id = fields.Many2one(
        "hr.company.offense",
        string="Offense Code",
        readonly=True,
        store=True,
        compute="_get_offense_code",
    )

    @api.depends("policy_id")
    def _get_offense_code(self):
        for record in self:
            record.offense_id = record.policy_id.offense_code_id

    @api.multi
    def name_get(self):
        data = []
        for i in self:
            display_value = "{} - {}".format(i.policy_id.name,
                                             i.offense_id.name)
            data.append((i.id, display_value))
        return data


"""Every corrective action applied to employee is recorded here"""


class ActionHistory(models.Model):
    _name = "hr.infraction.action_history"
    _description = "Every corrective action applied to employee for specific violation is recorded here"
    infraction_id = fields.Many2one(
        "hr.infraction", string="Infraction Record")
    _inherit = ["mail.thread", "mail.activity.mixin", "resource.mixin"]

    stage = fields.Selection(
        string="Stage",
        selection=[
            ("incident_report", "Incident Report"),
            ("inv_nte_issuance", "Investigation and NTE Issuance"),
            ("collaboration", "Collaboration with IMC"),
            ("corrective_action", "Corrective Action"),
        ],
    )

    corrective_action = fields.Many2one("hr.company.offense.frequency")
    action = fields.Selection(
        string="Corrective Action",
        related="corrective_action.action",
        readonly=True,
        store=True,
    )
    offense_frequency = fields.Char(
        string="Offense & Frequency", compute="_get_default_offense"
    )
    violation_id = fields.Many2one("hr.company.violation", string="Violation")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    duration = fields.Integer(string="Duration")
    days_remaining = fields.Integer(
        string="Days Remaining", compute="_get_remaining_days"
    )
    submit_nte = fields.Boolean(string="Submit NTE")
    attachment = fields.Binary(string="Attachment")
    notes = fields.Text(string="Notes")
    number_of_days = fields.Integer(string="Number of Days")
    staggered = fields.Boolean(string="Staggered")

    @api.depends("infraction_id", "stage")
    def _get_default_offense(self):
        for i in self:
            policy_violated_id = i.infraction_id.policy_violated_id
            for j in policy_violated_id:
                code = j.offense_code_id.name
        _logger.info("\n\n\n{}\n\n\n".format(code))
        frequency = "Sample 2nd Offense"
        self.offense_frequency = "{} - {}".format(code, frequency)
        return True

    @api.onchange("start_date", "end_date")
    def _get_duration(self):
        duration = (
            abs((self.end_date - self.start_date)).days
            if self.end_date
            and self.start_date
            and (self.end_date - self.start_date).days > 0
            else 0
        )
        self.duration = duration

    @api.depends("start_date", "end_date")
    def _get_remaining_days(self):
        duration = (
            abs((self.end_date - self.start_date)).days
            if self.end_date
            and self.start_date
            and (self.end_date - self.start_date).days > 0
            else 0
        )
        self.days_remaining = (
            abs((self.end_date - date.today())).days
            if self.end_date and self.start_date and (date.today() > self.start_date)
            else duration
        )
        return True
