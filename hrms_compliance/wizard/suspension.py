# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, timedelta
_logger = logging.getLogger("_name_")


class Suspension(models.TransientModel):
    _name = 'create.suspension'
    _description = 'Suspension Wizard Model'

    status = [
        ('on_going', 'On Going'),
        ('completed', 'Completed')
    ]

    state = fields.Selection(
        string='Status',
        selection=status
    )
    emp_id = fields.Many2one('hr.employee', string="Offending Employee")
    infraction_id = fields.Many2one(
        'hr.infraction', string="Infraction Record")
    suspension_days = fields.Integer(string="Suspension Days")
    remaining_days = fields.Integer(
        string="Remaining Days", compute='compute_remaining_days')
    use_suspension_days = fields.Integer(
        string="Use Suspension", compute='compute_use_suspension_days')
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    history_ids = fields.Many2many('suspension.history',
                                   string="History",
                                   # domain="[('emp_id','=',emp_id)]",
                                   compute="get_history"
                                   )

    contract_id = fields.Many2one(
        'hr.contract', string='Current Contract',
        related='emp_id.contract_id',
        readonly=True,
    )

    @api.depends('use_suspension_days')
    def compute_remaining_days(self):
        for rec in self:
            suspension_days = rec.suspension_days
        self.remaining_days = suspension_days - rec.use_suspension_days
        return True

    @api.depends('start_date', 'end_date')
    def compute_use_suspension_days(self):
        if self.start_date and self.end_date:
            self.use_suspension_days = abs(
                (self.start_date - self.end_date)).days
        return True

    @api.depends('infraction_id')
    def get_history(self):
        result = self.env['suspension.history'].search(
            [('infraction_id', '=', self.infraction_id.id)]).ids
        self.update({
            "history_ids": [(6, 0, result)]
        })

    @api.multi
    def create_suspension(self):
        self.state = "on_going"
        if self.remaining_days < 0:
            raise UserError(
                _('Suspension days to be used must not be more than remaining suspension days.'))
        elif self.start_date == False and self.end_date == False:
            raise UserError(
                _('Please set start date and end date before clicking on Submit'))
        elif self.start_date == False and self.end_date != False:
            raise UserError('Please set start date before clicking on Submit')
        elif self.start_date != False and self.end_date == False:
            raise UserError('Please set end date before clicking on Submit')
        elif self.start_date < date.today():
            raise UserError(
                _('You cannot set the start date before today\'s date.'))
        elif self.start_date > self.end_date:
            raise UserError('Start Date must not be later than End Date')
        elif self.start_date == self.end_date and self.use_suspension_days == 0:
            raise UserError(_('Start Date must not be the same as End Date'))
        else:
            vals = {
                'emp_id': self.emp_id.id,
                'infraction_id': self.infraction_id.id,
                'used_days': self.use_suspension_days,
                'date_from': self.start_date,
                'date_to': self.end_date,
                'state': self.state,
            }
        # adding a message to the chatter from code
        # self.patient_id.message_post(
        #     body="Test string ", subject="Appointment Creation")
        # creating appointments from the code
        self.env['suspension.history'].create(vals)


class SuspensionHistoryWizard(models.TransientModel):
    _name = 'suspension.history.wizard'
    _description = 'Staggered Suspension History Model Wizard'

    status = [
        ('on_going', 'On Going'),
        ('completed', 'Completed')
    ]

    # suspension_id = fields.Many2one(
    #     'create.suspension', string="Create Suspension")
    used_days = fields.Integer(string="Used Days")
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    duration = fields.Integer(string="Duration")
    state = fields.Selection(
        string='Status',
        selection=status
    )
