# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, timedelta
_logger = logging.getLogger("_name_")



class Suspension(models.TransientModel):
    _name = 'create.suspension'
    _description = 'Suspension Wizard Model'


    suspension_days = fields.Integer(string="Suspension Days")
    remaining_days = fields.Integer(string="Remaining Days")
    use_suspension_days = fields.Integer(string="Use Suspension")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")

    # def create_suspension(self):
    #     vals = {
    #         'patient_id': self.patient_id.id,
    #         'appointment_date': self.appointment_date,
    #         'notes': 'Created From The Wizard/Code'
    #     }
    #     # adding a message to the chatter from code
    #     self.patient_id.message_post(body="Test string ", subject="Appointment Creation")
    #     # creating appointments from the code
    #     self.env['hospital.appointment'].create(vals)

