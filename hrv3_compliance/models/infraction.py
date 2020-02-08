# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, timedelta

_logger = logging.getLogger("_name_")


"""Main Model of Infractions which houses the fields
    responsible for the main form and tree view"""


class Infractions(models.Model):
    _name = "hr.infraction"
    _rec_name = "infraction_sequence_id"
    _description = "Infractions Management"
    _inherit = ["mail.thread", "mail.activity.mixin", "resource.mixin"]

    infraction_sequence_id = fields.Char(string='Infraction ID', required=True, copy=False, readonly=True,
                                         index=True, default=lambda self: _('New'))

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

    policy_violated_ids = fields.Many2many("hr.company.policy", string="Policies Violated",
                                           compute='_compute_policy_violated_ids', help="FOR POLICY VIOLATED ID DOMAIN PURPOSES ONLY")

    offense_code_id = fields.Many2one('hr.company.offense', string='Offense Code',
                                      related='policy_violated_id.offense_code_id',
                                      readonly=True,
                                      store=True,
                                      )

    policy_violated_id = fields.Many2one(
        "hr.company.policy",
        string="Policies Violated",
        track_visibility="onchange",
        domain="[('id', 'in', policy_violated_ids)]",

    )

    frequency = fields.Char(
        string="Frequency",
        track_visibility="onchange",
        compute='compute_policy_violation_instance',
        store=True,
    )

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

    # ============================================================================================
    # STATE BUTTON FIELDS
    # ============================================================================================
    date_opened = fields.Date(string="Date Opened",
                              track_visibility='onchange'
                              )
    date_in_progress = fields.Date(string="Date In Progress",
                                   track_visibility='onchange'
                                   )
    date_for_closure = fields.Date(string="Date For Closure",
                                   track_visibility='onchange'
                                   )
    date_closed = fields.Date(string="Date Closed",
                              track_visibility='onchange')
    set_open_by = fields.Many2one('res.users', string="Set to Open By",
                                  track_visibility='onchange'
                                  )
    set_in_progress_by = fields.Many2one('res.users', string="Set to In Progress By",
                                         track_visibility='onchange'
                                         )
    set_for_closure_by = fields.Many2one('res.users', string="Set to For Closure By",
                                         track_visibility='onchange'
                                         )
    set_closed_by = fields.Many2one('res.users', string="Set to Closed By",
                                    track_visibility='onchange'
                                    )
    # ============================================================================================

    @api.multi
    def type_offenses_others(self):
        pass

    @api.model
    def create(self, vals):
        if vals.get('infraction_sequence_id', _('New')) == _('New'):
            vals['infraction_sequence_id'] = self.env['ir.sequence'].next_by_code(
                'infraction.code.sequence') or _('New')
        result = super(Infractions, self).create(vals)
        return result

    # ============================================================================================
    # COMPUTES FOR FREQUENCY DEPENDING ON NUMBER OF VIOLATION INSTANCES IN A GIVEN POLICY CODE
    # ============================================================================================
    @api.depends('emp_id', 'policy_violated_id', 'offense_code_id',)
    def compute_policy_violation_instance(self):
        data = []
        frequency = ""
        active_emp_id = self.emp_id.id
        record_set = self.env['hr.infraction'].search(
            [('emp_id', '=', active_emp_id), ('state', 'not in ', ['closed'])])
        for i in record_set:
            data.append(i.policy_violated_id.id)
        counter = data.count(self.policy_violated_id.id)
        for i in self.offense_code_id.corrective_action_ids:
            frequency = i.frequencies
        if self.offense_code_id and self.offense_code_id.corrective_action_ids:
            _logger.info("\n\n\nCASE 1\n\n\n")
            self.frequency = frequency[counter -
                                       1 if counter > 0 else counter][1]
            _logger.info("\n\n\nCounter{}\nFrequency{}\n\n\n".format(
                counter-1, frequency))
        elif counter < 0:
            _logger.info("\n\n\nCASE 2\n\n\n")
            self.frequency = frequency[0][1]
        else:
            _logger.info("\n\n\nCASE 3\n\n\n")
            self.frequency = ""
    # ============================================================================================

    # =============================================================================================
    # FOR POLICY VIOLATED ID DOMAIN PURPOSES ONLY
    # ============================================================================================
    @api.depends('violation_id')
    def _compute_policy_violated_ids(self):
        for record in self:
            record.policy_violated_ids = record.violation_id.policy_violated_ids.ids
    # =============================================================================================

    # ==============================================================================================
    # STATE BUTTON FUNCTIONS
    # ============================================================================================

    @api.multi
    def set_state_open(self):
        self.write({
            'state': 'open',
            'date_opened': datetime.now(),
            'set_open_by': self._uid
        })
        return True

    @api.multi
    def set_state_inprogress(self):
        self.write({
            'state': 'in_progress',
            'date_in_progress': datetime.now(),
            'set_in_progress_by': self._uid
        })
        return True

    @api.multi
    def set_state_forclosure(self):
        self.write({
            'state': 'for_closure',
            'date_for_closure': datetime.now(),
            'set_for_closure_by': self._uid
        })
        return True

    @api.multi
    def set_state_closed(self):
        self.write({
            'state': 'closed',
            'date_closed': datetime.now(),
            'set_closed_by': self._uid
        })
        return True
    # ==============================================================================================


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
    corrective_action_ids = fields.One2many(
        "hr.company.offense.frequency",
        'offense_code_id',
        string="Corrective Actions",
    )
    description = fields.Text(string="Offense Code Description")
    frequency = fields.Integer(string="Frequency", compute="_get_frequency")
    corrective_action_enumerate = fields.Text(
        string="Corrective Actions", readonly=True, compute="_get_frequency"
    )

    # ============================================================================================
    # COMPUTES FOR NUMBER OF CORRECTIVE ACTIONS
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
    # ============================================================================================


"""Corrective Action houses Offense Codes that are used for each Company Policy"""


class CorrectiveAction(models.Model):
    _name = "hr.company.offense.frequency"
    _rec_name = "action"
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
                       size=64, compute="_get_name", store=True,)

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

    @api.depends("frequency")
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

    stage = fields.Selection(
        string="Stage",
        selection=[
            ("incident_report", "Incident Report"),
            ("inv_nte_issuance", "Investigation and NTE Issuance"),
            ("collaboration", "Collaboration with IMC"),
            ("corrective_action", "Corrective Action"),
        ],
    )
    offense_code_id = fields.Many2one('hr.company.offense', 'Offense Code',
                                      related='infraction_id.offense_code_id',
                                      readonly=True,
                                      store=True
                                      )
    corrective_action = fields.Many2one("hr.company.offense.frequency",
                                        domain="[('offense_code_id', '=', offense_code_id)]"
                                        )
    action = fields.Selection(
        string="Corrective Action",
        related="corrective_action.action",
        readonly=True,
        store=True,
    )
    offense_frequency = fields.Char(
        string="Offense & Frequency",
        compute="_get_default_offense"
    )
    violation_id = fields.Many2one("hr.company.violation", string="Violation")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    duration = fields.Integer(string="Duration")
    days_remaining = fields.Integer(
        string="Days Remaining",
        compute="_get_remaining_days"
    )
    submit_nte = fields.Boolean(string="Submit NTE")
    attachment = fields.Binary(string="Attachment")
    notes = fields.Text(string="Notes")
    number_of_days = fields.Integer(
        string="Number of Days", compute='_get_duration')
    staggered = fields.Boolean(string="Staggered")

    @api.depends
    def _get_corrective_action(self):

        pass

    @api.depends("infraction_id", "stage")
    def _get_default_offense(self):
        for i in self:
            policy_violated_id = i.infraction_id.policy_violated_id
            for j in policy_violated_id:
                code = j.offense_code_id.name
        frequency = self.infraction_id.frequency
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
        self.number_of_days = duration

    @api.depends("start_date", "end_date")
    def _get_remaining_days(self):
        for line in self:
            duration = (
                abs((line.end_date - line.start_date)).days
                if line.end_date
                and line.start_date
                and (line.end_date - line.start_date).days > 0
                else 0
            )
            line.days_remaining = (
                abs((line.end_date - line.today())).days
                if line.end_date and line.start_date and (date.today() > line.start_date)
                else duration
            )
        return True
