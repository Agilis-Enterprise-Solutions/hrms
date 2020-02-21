# coding: utf-8
from odoo import models, fields, api
from datetime import date
from logging import getLogger


def log(**to_output):
    getLogger().info("\n\n\n{0}\n\n".format(to_output))


class HealthCondition(models.Model):
    _name = 'health.condition'

    employee_id = fields.Many2one('hr.employee')

    health_condition = fields.Char()
    doctor_name = fields.Char('Name of the Doctor')
    address = fields.Char()
    medications = fields.Char()
    medical_documents = fields.Binary()
    date = fields.Date()
    fit_to_work = fields.Boolean()


class Employee(models.Model):
    _inherit = 'hr.employee'

    """======================WORK INFORMATION======================"""
    mobile_phone = fields.Char(compute="_auto_populate_work_info")
    work_email = fields.Char(compute="_auto_populate_work_info")
    work_location = fields.Char(compute="_auto_populate_work_info")
    work_phone = fields.Char(compute="_auto_populate_work_info")

    """======================PRIVATE INFORMATION======================"""
    passport_validity_date = fields.Date()
    place_of_passport_issuance = fields.Char()

    marital = fields.Selection([
        ('single', 'Single'),
        ('Single Mother', 'Single Mother'),
        ('Single Father', 'Single Father'),
        ('Married', 'Married'),
        ('Divorced', 'Divorced'),
        ('Widowed', 'Widowed')
    ])

    age = fields.Integer(compute="_compute_age_years")

    """======================PRE-EMPLOYMENT INFORMATION======================"""
    sss_checkbox = fields.Boolean('SSS', compute="_auto_tick")
    hdmf_checkbox = fields.Boolean(compute="_auto_tick")
    philhealth_checkbox = fields.Boolean(compute="_auto_tick")
    gsis_checkbox = fields.Boolean(compute="_auto_tick")
    tin_checkbox = fields.Boolean(compute="_auto_tick")
    medical_transaction_number_checkbox = fields.Boolean(compute="_auto_tick")

    nbi_checkbox = fields.Boolean(compute="_auto_tick")
    police_checkbox = fields.Boolean(compute="_auto_tick")
    barangay_checkbox = fields.Boolean(compute="_auto_tick")

    birth_checkbox = fields.Boolean(compute="_auto_tick")
    tor_checkbox = fields.Boolean(compute="_auto_tick")
    diploma_checkbox = fields.Boolean(compute="_auto_tick")

    sss = fields.Integer('SSS')
    hdmf = fields.Integer('HDMF')
    philhealth = fields.Integer('PhilHealth', default=None)
    gsis = fields.Integer('GSIS')
    tin = fields.Integer('TIN')
    medical_transaction_number = fields.Char()

    nbi_clearance = fields.Char('NBI')
    nbi_expiration = fields.Date()
    nbi_issued_at = fields.Char()
    nbi_date_issued = fields.Date()
    nbi_clearance_photo = fields.Binary()

    police_clearance = fields.Char('Police Clearance')
    police_expiration = fields.Date()
    police_issued_at = fields.Char()
    police_date_issued = fields.Date()
    police_clearance_photo = fields.Binary()

    barangay_clearance = fields.Char('Barangay Clearance')
    barangay_expiration = fields.Date()
    barangay_issued_at = fields.Char()
    barangay_date_issued = fields.Date()
    barangay_clearance_photo = fields.Binary()

    birth_certificate = fields.Binary()
    transcript_of_records = fields.Binary()
    diploma = fields.Binary()

    """======================SKILLS AND TRAINING======================"""
    skill_ids = fields.One2many('hrmsv3.skills', 'employee_id',
                                string="Skills")

    """======================HEALTH INFORMATION======================"""
    fit_to_work = fields.Boolean()

    height = fields.Float()
    height_uom = fields.Selection([
        ('mm', 'mm'),
        ('cm', 'cm'),
        ('inch', 'inch'),
        ('ft', 'ft')
    ])

    weight = fields.Float()
    weight_uom = fields.Selection([
        ('lbs', 'lbs'),
        ('kg', 'kg')
    ])

    blood_type = fields.Selection([
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-')
    ])
    drug_test = fields.Selection([
        ('Positive', 'Positive'),
        ('Negative', 'Negative')
    ])

    health_card_provider = fields.Char()
    id_number = fields.Char(string='ID Number')
    cap_limit = fields.Float()
    credit_usage = fields.Float()

    hmo_validity_date = fields.Date(string='HMO Validity Date')
    hmo_validity_date_end = fields.Date()
    for_renewal = fields.Boolean()
    renewal_date = fields.Date()

    health_condition_ids = fields.One2many('health.condition', 'employee_id')

    """======================INFRACTION======================"""
    infraction_ids = fields.One2many(
        'hr.infraction', 'emp_id',
        string="Infractions",
        compute='_compute_infraction_record'
    )

    @api.depends('children')
    def _compute_infraction_record(self):
        record = self.env['hr.infraction'].search([('emp_id', '=', self.id)])
        self.update({
            'infraction_ids': [(6, 0, record.ids)],
        })

    """======================EMPLOYEE MOVEMENT======================"""
    contract_history_ids = fields.One2many(
        'hr.contract', 'employee_id',
        string="Contract History",
        compute='_compute_contract_history_record'
    )

    @api.depends('children')
    def _compute_contract_history_record(self):
        record = self.env['hr.contract'].search([('employee_id', '=', self.id)])
        self.update({
            'contract_history_ids': [(6, 0, record.ids)],
        })

    """================PRE-EMPLOYMENT REQUIREMENTS FUNCTIONS==============="""

    @api.depends('sss', 'hdmf', 'philhealth', 'gsis', 'nbi_clearance',
                 'nbi_expiration', 'nbi_issued_at', 'nbi_date_issued',
                 'nbi_clearance_photo', 'birth_certificate',
                 'transcript_of_records', 'diploma', 'police_clearance',
                 'police_expiration', 'police_issued_at', 'police_date_issued',
                 'police_clearance_photo', 'barangay_clearance',
                 'barangay_expiration', 'barangay_issued_at',
                 'barangay_date_issued', 'barangay_clearance_photo', 'tin',
                 'medical_transaction_number')
    def _auto_tick(self):
        for rec in self:
            rec.sss_checkbox = True if rec.sss else False
            rec.hdmf_checkbox = True if rec.hdmf else False
            rec.philhealth_checkbox = True if rec.philhealth else False
            rec.gsis_checkbox = True if rec.gsis else False
            rec.tin_checkbox = True if rec.tin else False
            rec.medical_transaction_number_checkbox = (True if
                                                       rec.medical_transaction_number
                                                       else False)

            rec.nbi_checkbox = True if (rec.nbi_clearance
                                        and rec.nbi_expiration
                                        and rec.nbi_issued_at
                                        and rec.nbi_date_issued
                                        and rec.nbi_clearance_photo) else False
            rec.police_checkbox = True if (rec.police_clearance
                                           and rec.police_expiration
                                           and rec.police_issued_at
                                           and rec.police_date_issued
                                           and rec.police_clearance_photo) else False
            rec.barangay_checkbox = True if (rec.barangay_clearance
                                             and rec.barangay_expiration
                                             and rec.barangay_issued_at
                                             and rec.barangay_date_issued
                                             and rec.barangay_clearance_photo) else False

            rec.birth_checkbox = True if rec.birth_certificate else False
            rec.tor_checkbox = True if rec.transcript_of_records else False
            rec.diploma_checkbox = True if rec.diploma else False

    """======================PRIVATE INFORMATION FUNCTIONS======================"""
    @api.depends('birthday')
    def _compute_age_years(self):
        today = date.today()
        for rec in self:
            if rec.birthday:
                rec.age = (today.year - rec.birthday.year
                           - ((today.month, today.day) < (rec.birthday.month,
                                                          rec.birthday.day)))

    """======================WORK INFORMATION FUNCTIONS======================"""
    @api.depends('address_id')
    def _auto_populate_work_info(self):
        for rec in self:
            if rec.address_id:
                rec.mobile_phone = rec.address_id.mobile or ""
                rec.work_email = rec.address_id.email or ""
                rec.work_location = ((rec.address_id.street
                                      or "")
                                     + ", " + (rec.address_id.street2
                                               or "")
                                     + ", " + (rec.address_id.city
                                               or "")
                                     + ", " + (rec.address_id.state_id.name
                                               or "")
                                     + ", " + (rec.address_id.zip
                                               or "")
                                     + ", " + (rec.address_id.country_id.name
                                               or ""))
                rec.work_phone = rec.address_id.phone or ""
